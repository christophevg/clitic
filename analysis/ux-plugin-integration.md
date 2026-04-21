# UX Review: Plugin-Conversation Integration

**Task:** plugin-conversation-integration
**Reviewer:** UI/UX Designer Agent
**Date:** 2026-04-21
**Status:** Design Review (Pre-Implementation)

---

## 1. Executive Summary

This review assesses the UX implications of integrating the ContentPlugin system with the Conversation widget's virtual rendering architecture. The integration presents a significant architectural challenge: plugins return Textual Widgets while virtual rendering requires pre-rendered Strips.

**Key Findings:**
- Hybrid rendering approach needed to maintain performance
- Visual consistency requires design system alignment
- Loading/error states critical for user trust
- Content type detection must be intuitive

**Recommendation:** Proceed with implementation using the Hybrid Strip Extraction approach (Section 3.1), with staged rollout starting with MarkdownPlugin.

---

## 2. Current State Analysis

### 2.1 Conversation Virtual Rendering

The Conversation widget uses Textual's Line API for O(1) per-line rendering:

```
Block Append Flow:
  append(role, content)
    -> _render_block_to_strips(block, width)
    -> Store in _strips list
    -> Update cumulative heights

Display Flow:
  render_line(y)
    -> Direct _strips[y] access
    -> Crop for horizontal scroll
```

**Performance Characteristics:**
- Pre-rendering happens once per block
- Re-rendering only on resize
- O(1) per-line display
- Memory-efficient for 100,000+ lines

### 2.2 ContentPlugin Architecture

```python
class ContentPlugin(ABC):
    def can_render(self, content_type: str, content: str | Renderable) -> bool
    def render(self, content: str | Renderable) -> Widget
    async def render_async(self, content: str | Renderable) -> Widget
```

**Key Observation:** Plugins return Textual `Widget` instances, not pre-rendered `Strip` objects. This is an impedance mismatch with virtual rendering.

### 2.3 MarkdownPlugin Status

The `MarkdownPlugin` class exists and is functional:
- Returns `textual.widgets.Markdown` widget
- Supports headers, paragraphs, lists, code blocks, links
- Has `open_links` configuration
- **Not connected** to Conversation widget

---

## 3. Integration Architecture Options

### 3.1 Hybrid Strip Extraction (Recommended)

Convert plugin Widget output to Strips for virtual rendering:

```
Plugin Content Flow:
  append(role, content, metadata={"content_type": "markdown"})
    -> Check metadata for content_type
    -> Query registered plugins for matching renderer
    -> plugin.render(content) -> Widget
    -> Render widget to Console -> lines
    -> Convert lines to Strips
    -> Store in _strips list (same as plain text)
```

**Pros:**
- Preserves virtual rendering performance
- Consistent with existing architecture
- Works with resize handling
- Memory-efficient

**Cons:**
- Loses widget interactivity (links, buttons)
- Requires temporary Console rendering
- May not work for all widget types

**UX Impact:**
- Performance maintained: Users see no degradation
- Static rendering: Links not clickable (acceptable trade-off)
- Visual consistency: Plugin styling preserved in strips

### 3.2 Widget Embedding (Alternative)

Store widget references and render dynamically:

```
Widget Embedding Flow:
  append(role, content, metadata={...})
    -> If plugin matches, create Widget
    -> Store widget reference in block data
    -> render_line(y) renders widget segments on-demand
```

**Pros:**
- Full widget interactivity
- Links remain clickable
- Dynamic updates possible

**Cons:**
- Complex lifecycle management
- Potential memory leaks
- May break virtual rendering assumptions
- Resize handling more complex

**UX Impact:**
- Interactive elements: Users can click links
- Potential performance impact on large conversations
- Inconsistent with current design

### 3.3 Recommendation

Use **Hybrid Strip Extraction** for initial implementation. The performance guarantees of virtual rendering are critical UX requirements. Widget interactivity (clickable links) can be addressed in Phase 2 with a "selected block" detail view.

---

## 4. Visual Design Considerations

### 4.1 Block Visual Consistency

From `analysis/ui-ux.md` Section 5.3, the block visual design:

```
+------------------------------------------------------------------+
| [Role Badge] [Timestamp]                              [Actions v] |
+------------------------------------------------------------------+
|                                                                  |
|  [Block Content - varies by type]                                |
|                                                                  |
+------------------------------------------------------------------+
```

**Plugin Content Integration Points:**

| Element | Current Behavior | Plugin Behavior |
|---------|------------------|-----------------|
| Role badge | "[You]", "[Assistant]", etc. | Unchanged |
| Content area | Plain text, role-colored | Plugin-rendered, role context |
| Separator | Blank line between blocks | Unchanged |
| Selection highlight | Cyan color override | Apply to plugin strips too |

### 4.2 Plugin Content Styling

**Challenge:** Plugin-rendered content has its own styling (Markdown headers, code blocks, etc.) that must coexist with Conversation styling.

**Recommendations:**

1. **Role Color Integration:**
   - Markdown headers: Use role color as accent
   - Code blocks: Dark background, role color for language badge
   - Links: Role color for underlines

2. **Visual Hierarchy:**
   - Plugin content maintains its internal hierarchy
   - Conversation provides container context (role, selection)
   - No double-borders or redundant framing

3. **Theme Compatibility:**
   - Plugin styles should respond to dark/light theme
   - Color variables passed to plugin renderers
   - MarkdownPlugin should accept theme parameter

### 4.3 Mixed Content Types

**Scenario:** Conversation contains both plain text and plugin-rendered blocks.

**Visual Consistency Requirements:**

1. **Spacing:** Same 1-cell margin between all blocks
2. **Width:** Plugin content wraps to same width as plain text
3. **Role indication:** Same role badge style for all blocks
4. **Selection:** Same highlight behavior for all block types

**Example Visual Flow:**

```
[You] just now
Hello, can you help me with Python?           <- Plain text (blue, bold)

[Assistant] 1 min ago
# Python Help                                 <- Markdown header (green accent)
I'd be happy to help! Here's an example:      <- Markdown paragraph
```python                                     <- Code block start
print("Hello, World!")                        <- Code content
```                                           <- Code block end

[You] 2 min ago
Thanks! That worked perfectly.                <- Plain text (blue, bold)
```

---

## 5. Content Type Detection UX

### 5.1 Detection Mechanisms

**Explicit Declaration (Preferred):**
```python
conversation.append(
    "assistant",
    markdown_content,
    metadata={"content_type": "text/markdown"}
)
```

**Implicit Detection (Future):**
- Auto-detect based on content patterns
- Heuristics for common formats (starts with `#`, has code fences, etc.)
- Risk: False positives reduce user trust

**Recommendation:** Start with explicit `content_type` metadata only. Implicit detection is a Phase 2 feature with user override capability.

### 5.2 Content Type Values

Standardize on MIME-style content types:

| Content Type | Description | Plugin |
|--------------|-------------|--------|
| `text/plain` | Plain text (default) | None (built-in) |
| `text/markdown` | Markdown content | MarkdownPlugin |
| `text/x-diff` | Unified diff | DiffPlugin |
| `text/x-terminal` | Terminal output with ANSI | TerminalPlugin |

### 5.3 Fallback Behavior

**When No Plugin Matches:**
1. Log warning with content_type and available plugins
2. Fall back to plain text rendering
3. User sees content, no error shown
4. Developer can debug via logs

**UX Principle:** Never show empty or error content to user. Always show something, even if degraded.

---

## 6. Loading and Error States

### 6.1 Plugin Loading States

**Scenario:** Plugin takes time to render (complex markdown, large diff).

**Current Loading Indicator:**
- CSS class `.loading` sets `opacity: 0.7`
- Used for block restoration from file

**Recommendations:**

1. **Use existing loading mechanism:**
   - Set `loading` CSS class during plugin render
   - Pre-render should be fast, but async option exists

2. **Progressive rendering (Future):**
   - Show placeholder during async render
   - Swap in rendered content when ready
   - Use animation for smooth transition

### 6.2 Plugin Error Handling

**Error Scenarios:**

| Error Type | User Experience | Developer Experience |
|------------|-----------------|----------------------|
| Plugin not found | Fall back to plain text | Warning log |
| Plugin raises exception | Fall back to plain text | Error log with stack trace |
| Content type unsupported | Fall back to plain text | Debug log |
| Invalid content | Show sanitized content | Warning log |

**Error Display Principle:**
- Users never see stack traces or technical errors
- Content is always visible (degraded, not missing)
- Developers get detailed logs for debugging

### 6.3 Graceful Degradation

**Example: Markdown Plugin Failure**

```
# User's original content:
"Here is some **markdown** with `code`"

# Plugin fails, fallback renders:
"[Assistant] 1 min ago
Here is some **markdown** with `code`    <- Raw markdown shown
"
```

User sees the raw content, not an error. They can still understand the message, just without formatting.

---

## 7. Performance Considerations

### 7.1 Rendering Performance

**Current Benchmarks:**
- 100,000+ lines without degradation
- < 50MB memory for 10,000 blocks
- O(1) per-line rendering

**Plugin Impact Analysis:**

| Operation | Current | With Plugin | Mitigation |
|-----------|---------|-------------|------------|
| Append | O(lines) | O(lines + plugin) | Plugin render must be fast |
| Resize | O(total lines) | O(total lines + plugins) | Parallel plugin renders |
| Scroll | O(1) | O(1) | Unchanged (strips pre-rendered) |
| Memory | ~50 bytes/line | ~same | Strip storage same size |

**Performance Requirements for Plugins:**

1. **Sync render < 16ms:** Block append should not freeze UI
2. **Memory bounded:** Plugin strips should not exceed 2x plain text
3. **No external calls:** Plugins should not make network requests in render

### 7.2 Plugin Performance Testing

**Recommended Benchmarks:**

1. **Append benchmark:**
   - 1000 markdown blocks appended
   - Measure time per append
   - Target: < 5ms per append on average hardware

2. **Resize benchmark:**
   - 100 blocks with various content types
   - Resize terminal multiple times
   - Target: < 100ms total re-render

3. **Memory benchmark:**
   - 10,000 blocks with markdown content
   - Measure memory usage
   - Target: < 100MB total

---

## 8. User Interaction Design

### 8.1 Plugin Content Interactivity

**Current State:** Virtual rendering creates static content.

**Interactive Features Lost:**
- Clickable links (MarkdownPlugin `open_links=True`)
- Code block copy buttons
- Collapsible sections

**Workaround Design:**

1. **Link Handling (Phase 1):**
   - Show links with role-color underline
   - Display URL in parentheses for visibility
   - User can copy URL manually

2. **Link Handling (Phase 2):**
   - Selected block shows detail view
   - Detail view uses full Widget (interactive)
   - Links clickable in detail view

### 8.2 Content Type Switching

**Scenario:** User wants to view markdown source instead of rendered.

**Design:**
- Add metadata toggle: `render_as: "source" | "rendered"`
- Default: "rendered"
- Selected block can toggle via keyboard shortcut (e.g., `v` for view source)

### 8.3 Keyboard Navigation

**Existing Navigation:**
- `Alt+Up/Down` - Navigate between blocks
- `Escape` - Clear selection

**Plugin Content Navigation:**

1. **Block-level:** Same as current (Alt+Up/Down)
2. **Content-level (Future):**
   - `j/k` - Navigate within rendered content
   - Code blocks: scroll within block
   - Tables: navigate cells

**Recommendation:** Keep existing navigation unchanged. Content-level navigation is Phase 2.

---

## 9. Accessibility Considerations

### 9.1 Screen Reader Compatibility

**Plain Text Blocks:**
- Read as "[Role]: [Content]"

**Plugin-Rendered Blocks:**
- Should announce content type: "[Role] Markdown: [Content]"
- Structure should be preserved (headers, lists, code)
- Links should be announced as links

**Implementation:**
- Add `aria-label` equivalent via accessible name
- Plugin strips should include semantic markers
- Code blocks announced as "code block, language: python"

### 9.2 Visual Accessibility

**Contrast Requirements:**
- Plugin content must meet WCAG AA (4.5:1 ratio)
- Dark theme: Use lighter accent colors
- Light theme: Use darker accent colors

**Color Independence:**
- Markdown headers: Use size + color (not just color)
- Links: Use underline + color (not just color)
- Code blocks: Use background + border (not just background)

---

## 10. Acceptance Criteria UX Review

| Criterion | UX Assessment | Recommendation |
|-----------|--------------|----------------|
| Conversation queries registered plugins | Good - explicit registration | Implement plugin registry in App, passed to Conversation |
| Blocks with `content_type` metadata use appropriate plugin | Good - explicit control | Document metadata format in user guide |
| Fallback to plain text when no plugin matches | Critical - user trust | Implement with logging for developers |
| Markdown content renders correctly in Conversation | Good - visual test | Create visual test with golden screenshot |
| Plugin rendering works with virtual rendering | Challenging - see Section 3 | Use Hybrid Strip Extraction |
| Integration tests for plugin rendering flow | Good - testability | Include performance tests |
| Showcase demonstrates markdown rendering | Essential - discoverability | Add markdown example to welcome message |

---

## 11. Recommendations Summary

### 11.1 Implementation Priority

1. **P0 - Critical:**
   - Hybrid Strip Extraction implementation
   - Fallback rendering (never show empty)
   - Basic MarkdownPlugin integration

2. **P1 - Essential:**
   - Plugin registry in App class
   - `content_type` metadata handling
   - Error handling and logging

3. **P2 - Important:**
   - Theme-aware plugin rendering
   - Visual tests with golden screenshots
   - Performance benchmarks

4. **P3 - Nice-to-have:**
   - Content-level navigation
   - View source toggle
   - Interactive link handling via detail view

### 11.2 Design Decisions Required

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Rendering approach | Hybrid vs Widget Embed | Hybrid Strip Extraction |
| Content type detection | Explicit vs Implicit | Explicit only (Phase 1) |
| Plugin registry location | App vs Conversation | App (passed to Conversation) |
| Error display | Toast vs Inline | Silent fallback + logs |
| Link handling | Static vs Interactive | Static (Phase 1), Interactive (Phase 2) |

### 11.3 Next Steps

1. Update TODO.md with refined acceptance criteria
2. Coordinate with API Architect on plugin registry design
3. Create visual design mockup for markdown blocks
4. Implement Hybrid Strip Extraction in `_render_block_to_strips`
5. Add integration tests before merge

---

## 12. Appendix: Technical Implementation Notes

### 12.1 Strip Extraction Code Pattern

```python
def _render_block_to_strips(
    self, block: _BlockData, width: int, is_selected: bool = False
) -> list[Strip]:
    # Check for plugin content
    content_type = block.info.metadata.get("content_type", "text/plain")

    if content_type != "text/plain":
        plugin = self._get_plugin_for_type(content_type, block.info.content)
        if plugin:
            try:
                widget = plugin.render(block.info.content)
                return self._widget_to_strips(widget, width, block.info.role, is_selected)
            except Exception:
                # Log and fall through to plain text
                pass

    # Plain text fallback (existing code)
    return self._plain_text_to_strips(block, width, is_selected)

def _widget_to_strips(
    self, widget: Widget, width: int, role: str, is_selected: bool
) -> list[Strip]:
    # Render widget to Rich segments
    console = Console(width=width)
    # Use widget's render method to get Renderable
    renderable = widget.render()
    lines = list(console.render_lines(renderable))

    # Convert to Strips
    strips = []
    for line in lines:
        segments = [...]
        strips.append(Strip(segments, width))

    return strips
```

### 12.2 Plugin Registry Design

```python
class App:
    def __init__(self, plugins: list[ContentPlugin] | None = None):
        self._plugins: dict[str, ContentPlugin] = {}
        if plugins:
            for plugin in plugins:
                self.register_plugin(plugin)

    def register_plugin(self, plugin: ContentPlugin) -> None:
        plugin.on_register(self)
        self._plugins[plugin.name] = plugin

    def get_plugin_for_content(self, content_type: str, content: str) -> ContentPlugin | None:
        # Sort by priority, check can_render
        for plugin in sorted(self._plugins.values(), key=lambda p: -p.priority):
            if plugin.can_render(content_type, content):
                return plugin
        return None
```

---

**Document Status:** Complete
**Next Review:** After implementation
**Related Documents:**
- `analysis/ui-ux.md` - Overall UX analysis
- `analysis/api.md` - API design
- `TODO.md` - Task tracking