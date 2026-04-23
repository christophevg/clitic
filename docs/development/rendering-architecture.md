# Rendering Architecture Guide

A deep dive into how clitic renders content, from Textual's core rendering pipeline through Rich's segment model to our custom plugins.

## Table of Contents

1. [Overview](#overview)
2. [The Textual Rendering Pipeline](#the-textual-rendering-pipeline)
3. [Rich's Segment Model](#richs-segment-model)
4. [Textual's Strip Class](#textuals-strip-class)
5. [clitic's Conversation Widget](#clitics-conversation-widget)
6. [The Plugin System](#the-plugin-system)
7. [Case Study: The Diff Artifact Bug](#case-study-the-diff-artifact-bug)
8. [Best Practices](#best-practices)

---

## Overview

clitic renders conversation messages using a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│  Textual Compositor - Coordinates widget rendering      │
├─────────────────────────────────────────────────────────┤
│  Conversation.render_line() - Maps screen → data coords │
├─────────────────────────────────────────────────────────┤
│  Plugin.render_to_strips() - Width-aware rendering      │
├─────────────────────────────────────────────────────────┤
│  Rich Segment / Textual Strip - Low-level primitives    │
└─────────────────────────────────────────────────────────┘
```

The key challenge: **virtual scrolling**. We support 100,000+ lines of conversation content, but only render what's visible. This requires careful coordination between:

- **Screen coordinates**: Where on the physical terminal a line appears (y=0 is top of visible area)
- **Data coordinates**: Where in the full content a line lives (y=0 is the first line ever)
- **Strip cell length**: How many terminal cells a strip occupies vs. what we tell Textual it occupies

---

## The Textual Rendering Pipeline

### Widget.render_line()

Textual calls `render_line(y)` on each visible widget to get the content for a specific line. The `y` parameter is a **screen coordinate** - `y=0` is the top of the widget's visible area, not the first line of content.

```python
# From textual/widget.py
def render_line(self, y: int) -> Strip:
    """Render a line of content.

    Args:
        y: Y Coordinate of line (screen coordinate, 0 = top of visible area).
    """
    if self._dirty_regions:
        self._render_content()
    try:
        line = self._render_cache.lines[y]
    except IndexError:
        line = Strip.blank(self.size.width, self.visual_style.rich_style)
    return line
```

The default implementation uses an internal render cache. For virtual scrolling, we override this method to compute lines on-demand.

### ScrollView and Virtual Content

`ScrollView` (which `Conversation` extends) manages a **virtual size** that can be larger than the physical screen:

```python
# Virtual size = full content dimensions
self.virtual_size = Size(width, total_lines)

# scroll_offset.y = how far we've scrolled down
scroll_x, scroll_y = self.scroll_offset

# max_scroll_y = virtual_size.height - container_size.height
```

When rendering, we convert screen coordinates to data coordinates:

```python
def render_line(self, y: int) -> Strip:
    scroll_x, scroll_y = self.scroll_offset
    data_y = int(scroll_y) + y  # Screen coord → Data coord
    strip = self._strips[data_y]
    return strip.crop_extend(scroll_x, scroll_x + width, extend_style)
```

**Key insight**: `scroll_y=10` with `y=0` means "render the 11th line of content at the top of the visible area."

---

## Rich's Segment Model

Rich represents formatted text as `Segment` objects - tuples of `(text, style, control)`:

```python
from rich.segment import Segment

# A green "added" line prefix
Segment("+", Style(color="green", bgcolor="#e3fedf"))

# The text content with background only
Segment("added line", Style(bgcolor="#e3fedf"))

# Padding spaces to fill width
Segment(" " * 29, Style(bgcolor="#e3fedf"))
```

Segments are **immutable** and composable. A line of text is a list of segments that, when rendered, produce the final visual output.

### Console.render_lines()

Rich's `Console` converts renderables (Text, Syntax, etc.) into segments:

```python
from rich.console import Console
from rich.text import Text

console = Console(width=80)
text = Text("[bold green]+[/bold green] added line")

# render_lines returns an iterable of segment lists
lines = list(console.render_lines(text))
# lines[0] = [Segment("+", ...), Segment(" added line", ...)]
```

Each "line" is a list of segments. The segments' text lengths may not add up to the console width - that's where padding comes in.

---

## Textual's Strip Class

Textual's `Strip` wraps Rich segments with additional functionality for terminal rendering:

```python
from textual.strip import Strip

strip = Strip(segments, cell_length=None)
```

### The cell_length Parameter

**This is where our bug originated.**

The second parameter to `Strip()` is an **optional cached value** for the cell length. If provided, Textual uses this value instead of calculating from segments:

```python
@property
def cell_length(self) -> int:
    """Get the number of cells required to render this object."""
    if self._cell_length is None:
        self._cell_length = get_line_length(self._segments)
    return self._cell_length
```

**Danger**: If you pass `cell_length=40` but the segments only total 35 cells, `cell_length` returns 40 (the cached value), not 35 (the actual length).

### crop_extend()

When a strip needs to be cropped to a different width, `crop_extend()` is used:

```python
def crop_extend(self, start: int, end: int, style: Style | None) -> Strip:
    """Crop between two points, extending the length if required."""
    cache_key = (start, end, style)
    cached_result = self._crop_extend_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # extend_cell_length uses self.cell_length for comparison
    strip = self.extend_cell_length(end, style).crop(start, end)
    self._crop_extend_cache[cache_key] = strip
    return strip
```

And `extend_cell_length()`:

```python
def extend_cell_length(self, cell_length: int, style: Style | None = None) -> Strip:
    """Extend the cell length if it is less than the given value."""
    if self.cell_length < cell_length:
        missing_space = cell_length - self.cell_length
        segments = self._segments + [Segment(" " * missing_space, style)]
        return Strip(segments, cell_length)
    else:
        return self  # No extension needed
```

**The bug**: If `self.cell_length` returns a cached value that's larger than the actual segment content, the `if self.cell_length < cell_length` check fails incorrectly, and no extension happens. The subsequent `crop()` then operates on incomplete data.

---

## clitic's Conversation Widget

### Architecture

```
src/clitic/widgets/conversation.py
├── Conversation(ScrollView)
│   ├── _blocks: list[_BlockData]       # Message metadata
│   ├── _strips: list[Strip]            # Rendered content
│   ├── _cumulative_heights: list[int]  # For binary search
│   └── render_line(y: int) -> Strip    # Line API override
```

### _render_block_to_strips()

Each message block is rendered to strips:

```python
def _render_block_to_strips(
    self, block: _BlockData, width: int, is_selected: bool = False
) -> list[Strip]:
    # Check for plugin rendering
    content_type = block.info.metadata.get("content_type")
    if content_type and self._plugins:
        plugin = self._get_matching_plugin(content_type, block.info.content)
        if plugin:
            plugin_strips = self._render_plugin_to_strips(
                plugin, block.info.content, width, block.info.role, is_selected
            )
            # Add role label and margin
            return [role_label_strip] + plugin_strips + [blank_strip]
    
    # Fall back to plain text rendering
    ...
```

### render_line() - The Virtual Scroll Bridge

```python
def render_line(self, y: int) -> Strip:
    """Render a single line using the Line API.
    
    Args:
        y: Screen y-coordinate (0 = top of visible region).
    """
    scroll_x, scroll_y = self.scroll_offset
    data_y = int(scroll_y) + y  # Convert screen → data coordinate
    
    width = self._get_content_width()
    
    # Bounds check using actual strips length, not _total_lines
    if data_y < 0 or not self._strips or data_y >= len(self._strips):
        return Strip.blank(width, getattr(self, "rich_style", None))
    
    strip = self._strips[data_y]
    
    # Extract background style from last segment for crop_extend
    extend_style = None
    strip_segments = list(strip)
    if strip_segments:
        last_seg = strip_segments[-1]
        if last_seg.style:
            extend_style = last_seg.style
    
    return strip.crop_extend(int(scroll_x), int(scroll_x) + width, extend_style)
```

**Key design decisions:**

1. **Bounds check uses `len(self._strips)`** - Not `_total_lines`, which could be stale after pruning or during resize
2. **extend_style extraction** - Gets the background color from the last segment so `crop_extend()` uses consistent styling
3. **Defensive blank strip** - Returns a blank strip for out-of-bounds access rather than crashing

---

## The Plugin System

Plugins provide custom rendering for specific content types:

```python
# src/clitic/plugins/base.py
class ContentPlugin:
    @property
    def name(self) -> str: ...
    
    @property
    def priority(self) -> int: ...
    
    def can_render(self, content_type: str, content: str) -> bool: ...
    
    def render(self, content: str) -> Renderable:
        """Return a Rich renderable (default implementation)."""
    
    def render_to_strips(self, content: str, width: int) -> list[Strip] | None:
        """Return strips directly (optional, for width-aware rendering)."""
```

### render() vs render_to_strips()

- **`render()`**: Returns a Rich renderable (Text, Syntax, etc.). Goes through `Console.render_lines()` which handles padding automatically.
- **`render_to_strips()`**: Returns Textual Strips directly. Full control over segments and padding, but full responsibility for correctness.

The Diff plugin uses `render_to_strips()` because it needs precise control over background colors spanning the full line width.

---

## Case Study: The Diff Artifact Bug

### Symptoms

When resizing the terminal window with diff content visible:
- Dark squares/artifacts appeared in the diff output
- Worse when viewport was smaller than content (scrollbar visible)
- Speed-dependent: faster resize = more artifacts
- Only affected diff content, not code highlighting or markdown

### Root Cause Analysis

The bug was in `DiffPlugin.render_to_strips()`:

```python
# BEFORE (buggy)
elif line.startswith("+"):
    text = line[1:]
    text_cell_len = cell_len(text)
    total_cells = 1 + text_cell_len
    padding = max(0, width - total_cells)
    
    segments.append(RichSegment("+", _DIFF_ADDED_PREFIX_STYLE))
    if text:
        segments.append(RichSegment(text, _DIFF_ADDED_TEXT_STYLE))
    # BUG: Only add padding if needed
    if padding > 0:
        segments.append(RichSegment(" " * padding, _DIFF_ADDED_TEXT_STYLE))
    
    # BUG: Pass width as cached cell_length
    strips.append(Strip(segments, width))
```

**The problem:**

1. When `padding == 0` (text exactly fills width), no padding segment is added
2. Segments total: 1 (prefix) + 39 (text) = 40 cells... but wait, we passed `width=40` as the cache
3. Actually, if text is 39 chars and we have a 1-char prefix, that's 40 cells - but the cache says 40
4. Now `crop_extend()` is called with a different width during resize...
5. `extend_cell_length()` checks `if self.cell_length < cell_length` → `40 < new_width`
6. If `new_width > 40`, it extends. But if `new_width <= 40`, it doesn't!
7. The cached value (40) doesn't match reality if segments were constructed incorrectly

**The real issue**: The cache creates a lie. Textual trusts the cached `cell_length` instead of computing from segments. When segments don't add up to the cached value, `crop_extend()` makes wrong decisions.

### The Fix

```python
# AFTER (fixed)
elif line.startswith("+"):
    text = line[1:]
    text_cell_len = cell_len(text)
    total_cells = 1 + text_cell_len
    padding = max(0, width - total_cells)
    
    segments.append(RichSegment("+", _DIFF_ADDED_PREFIX_STYLE))
    if text:
        segments.append(RichSegment(text, _DIFF_ADDED_TEXT_STYLE))
    # FIX: Always add padding segment (even if empty)
    segments.append(RichSegment(" " * padding, _DIFF_ADDED_TEXT_STYLE))
    
    # FIX: Don't pass cached cell_length - let Textual calculate from segments
    strips.append(Strip(segments, None))
```

**Why this works:**

1. **Always include padding**: Segments always total exactly `width` cells
2. **No cached lie**: Passing `None` forces Textual to compute `cell_length` from actual segments
3. **crop_extend() now works correctly**: The extension check uses accurate data

### Testing the Fix

The test suite was updated to reflect the new behavior:

```python
# test_render_to_strips_no_padding_when_text_fills_width
def test_render_to_strips_no_padding_when_text_fills_width(self) -> None:
    """Padding segment should still be added (empty) when text fills width."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("+" + "x" * 39, 40)
    strip = strips[0]
    segments = list(strip)
    
    assert segments[0].text == "+"
    assert segments[1].text == "x" * 39
    assert segments[2].text == ""  # Empty padding segment
    assert len(segments) == 3
```

---

## Best Practices

### 1. Never Lie to Textual About Cell Length

```python
# BAD: Cached value might not match segments
Strip(segments, width)

# GOOD: Let Textual calculate from actual segments
Strip(segments, None)

# ALSO GOOD: Ensure segments actually total width cells
segments.append(RichSegment(" " * padding, style))
Strip(segments, None)
```

### 2. Always Pad to Full Width in render_to_strips()

When implementing `render_to_strips()`, ensure every strip's segments total exactly the render width:

```python
def render_to_strips(self, content: str, width: int) -> list[Strip]:
    for line in content.split("\n"):
        segments = []
        # ... add content segments ...
        
        # Calculate and add padding
        content_cells = sum(cell_len(seg.text) for seg in segments)
        padding = max(0, width - content_cells)
        segments.append(RichSegment(" " * padding, background_style))
        
        strips.append(Strip(segments, None))
```

### 3. Extract extend_style from Last Segment

When implementing `render_line()`, extract the background style for `crop_extend()`:

```python
def render_line(self, y: int) -> Strip:
    strip = self._strips[data_y]
    
    # Get background style from last segment
    extend_style = None
    strip_segments = list(strip)
    if strip_segments:
        last_seg = strip_segments[-1]
        if last_seg.style:
            extend_style = last_seg.style
    
    return strip.crop_extend(start, end, extend_style)
```

This ensures padding uses the same background as the content, preventing visual artifacts.

### 4. Use len(_strips) for Bounds Checking

Don't trust `_total_lines` during resize or pruning:

```python
# BAD: _total_lines might be stale
if data_y >= self._total_lines:
    return Strip.blank(width, style)

# GOOD: len() reflects actual array state
if data_y >= len(self._strips):
    return Strip.blank(width, style)
```

### 5. Atomic Swaps During Resize

Prevent race conditions by building new data in temporary variables:

```python
def _rerender_all_blocks(self) -> None:
    width = self._get_content_width()
    
    # Build in temporaries
    new_strips: list[Strip] = []
    new_cumulative_heights: list[int] = []
    new_total_lines = 0
    
    for block in self._blocks:
        block_strips = self._render_block_to_strips(block, width)
        new_strips.extend(block_strips)
        new_total_lines += len(block_strips)
        new_cumulative_heights.append(new_total_lines)
    
    # Atomic swap - all or nothing
    self._strips = new_strips
    self._cumulative_heights = new_cumulative_heights
    self._total_lines = new_total_lines
```

### 6. Clear Textual's Caches on Resize

Force Textual to recompute layout after structural changes:

```python
def on_resize(self, event: Resize) -> None:
    if new_width != self._last_width:
        self._rerender_all_blocks()
        self.clear_cached_dimensions()
        self._clear_arrangement_cache()
        self.refresh(layout=True)
```

---

## Debugging Tips

### Inspect Strip Cell Length

```python
strip = Strip(segments, cell_length_hint)
print(f"Hint: {cell_length_hint}")
print(f"Actual: {strip.cell_length}")
print(f"Segments: {[seg.text for seg in strip]}")
```

### Trace render_line Calls

Add temporary logging to see what's being rendered:

```python
def render_line(self, y: int) -> Strip:
    data_y = int(self.scroll_offset.y) + y
    print(f"render_line(y={y}) -> data_y={data_y}, len(_strips)={len(self._strips)}")
    ...
```

### Visualize crop_extend Behavior

```python
# Test crop_extend directly
strip = Strip([Segment("+test", Style(bgcolor="green"))], None)
print(f"Original cell_length: {strip.cell_length}")

extended = strip.crop_extend(0, 80, Style(bgcolor="green"))
print(f"Extended cell_length: {extended.cell_length}")
print(f"Extended segments: {[seg.text for seg in extended]}")
```

---

## Summary

The rendering pipeline flows from Textual's compositor down to terminal cells:

1. **Textual** calls `render_line(y)` with screen coordinates
2. **Conversation** converts to data coordinates and retrieves strips
3. **Plugins** provide width-aware rendering via `render_to_strips()`
4. **Rich Segments** carry text and style information
5. **Textual Strips** wrap segments for terminal rendering
6. **crop_extend()** adjusts strips to fit the viewport

The key lesson: **always ensure cached values match reality**. When in doubt, let Textual calculate from actual data rather than providing hints that might become stale.
