# UX/UI Design Analysis: Syntax Highlighting Widget

**Task:** syntax-highlighting-widget
**Reviewer:** UI/UX Designer Agent
**Date:** 2026-04-21
**Status:** Design Review (Pre-Implementation)

---

## 1. Executive Summary

This analysis examines the UX/UI design considerations for creating a syntax highlighting widget for the clitic TUI framework. The widget must integrate with the existing virtual rendering architecture while providing language-aware syntax highlighting for code content.

**Key Design Decisions:**
- Widget should be usable both standalone and as embedded component
- Theme integration should map pygments styles to app themes
- Pre-rendering approach for virtual rendering compatibility
- Language detection should be explicit with optional auto-detection

**Recommendation:** Proceed with implementation using a dual-mode approach (widget + ContentPlugin) with pre-rendered strips for Conversation integration.

---

## 2. Widget API Design

### 2.1 Core Widget Interface

The `SyntaxHighlight` widget should accept these parameters:

```python
class SyntaxHighlight(Widget):
    """Widget for displaying syntax-highlighted code.

    Args:
        code: The source code to highlight.
        language: Language identifier (e.g., "python", "javascript").
                  If None, attempts auto-detection.
        theme: Theme name to use for highlighting. If None, uses app theme.
        show_line_numbers: Whether to display line numbers (default: False).
        line_number_start: Starting line number (default: 1).
        tab_size: Tab width for indentation (default: 4).
        highlight_lines: Lines to highlight (e.g., {2, 3, 5}).
        name: Widget name.
        id: Widget ID.
        classes: Space-separated CSS classes.
        disabled: Whether widget is disabled.
    """
```

### 2.2 Usage Patterns

**Standalone Usage:**
```python
from clitic import SyntaxHighlight

# In a compose method
yield SyntaxHighlight(
    code="def hello():\n    print('world')",
    language="python",
    show_line_numbers=True,
)
```

**Embedded in Conversation (via ContentPlugin):**
```python
# Via metadata in Conversation.append()
conversation.append(
    "assistant",
    code_content,
    metadata={
        "content_type": "code/python",
        "language": "python",
    }
)
```

### 2.3 Reactive Properties

The widget should support reactive updates for dynamic content:

| Property | Type | Reactive | Description |
|----------|------|----------|-------------|
| `code` | `str` | Yes | The source code content |
| `language` | `str \| None` | Yes | Language identifier |
| `theme` | `str \| None` | Yes | Highlighting theme |
| `show_line_numbers` | `bool` | Yes | Line number visibility |

When `code` changes, the widget should re-render efficiently (cache parsed result if possible).

---

## 3. Theme Integration Strategy

### 3.1 Theme Mapping Architecture

The syntax highlighter needs to map app themes to pygments themes:

| App Theme | Pygments Theme | Notes |
|-----------|----------------|-------|
| `dark` | `monokai` | Dark background, vibrant colors |
| `light` | `github-light` | Light background, muted colors |

**Implementation Approach:**

```python
# Theme mapping configuration
THEME_MAP = {
    "dark": "monokai",
    "light": "github-light",
    # Future themes can be added here
}

def get_pygments_theme(app_theme: str) -> str:
    """Map app theme to pygments theme."""
    return THEME_MAP.get(app_theme, "monokai")  # Default to monokai
```

### 3.2 Theme Fallback Mechanism

When theme is not specified:

1. **First:** Check widget `theme` parameter
2. **Second:** Query parent app's `theme_name` property
3. **Fallback:** Use `monokai` (good dark theme default)

**Fallback Chain:**
```
widget.theme -> app.theme_name -> "monokai"
```

### 3.3 Custom Theme Support

Users should be able to specify custom pygments themes:

```python
SyntaxHighlight(
    code=code,
    theme="dracula",  # Direct pygments theme name
)
```

Custom themes bypass the mapping and use the specified name directly.

### 3.4 Theme CSS Variables

For consistency with base styles, the widget should respect CSS variables:

```python
# When rendering, check if theme colors can use CSS variables
# For embedded usage, role colors should influence highlighting
```

**Role Color Integration:**
- Code blocks in assistant messages: subtle background tint
- Code blocks in user messages: accent color for language badge
- Code blocks in system messages: warning color for border

---

## 4. Virtual Rendering Compatibility

### 4.1 Pre-Rendering Strategy

The Conversation widget uses `render_line()` for O(1) performance. The syntax highlight widget must support pre-rendering to strips.

**Two Modes:**

1. **Widget Mode:** Standard Textual widget for standalone use
2. **Strip Mode:** Pre-rendered strips for Conversation integration

**Strip Pre-Rendering:**

```python
def render_to_strips(self, width: int) -> list[Strip]:
    """Pre-render highlighted code to strips for Conversation.

    Args:
        width: Available width for line wrapping.

    Returns:
        List of Strip objects, one per line.
    """
    # Use Rich Console to render highlighted code
    highlighted = self._highlight_code()
    console = Console(width=width)
    lines = list(console.render_lines(highlighted))

    # Convert to strips
    strips = []
    for line in lines:
        segments = self._line_to_segments(line)
        strips.append(Strip(segments, width))
    return strips
```

### 4.2 Integration with Conversation

**Current Flow:**
```
Conversation._render_block_to_strips(block, width)
  -> if content_type matches plugin
     -> plugin.render(content) -> Rich renderable
     -> _renderable_to_strips(renderable, width)
```

**For Code Content:**
```
Conversation._render_block_to_strips(block, width)
  -> if content_type starts with "code/"
     -> extract language from metadata
     -> SyntaxHighlight.render_to_strips(code, width, language, theme)
```

### 4.3 Content Type Naming

**Recommended Content Types:**

| Content Type | Description | Example |
|--------------|-------------|---------|
| `code/python` | Python code | `metadata={"content_type": "code/python"}` |
| `code/javascript` | JavaScript code | `metadata={"content_type": "code/javascript"}` |
| `code/bash` | Shell/Bash script | `metadata={"content_type": "code/bash"}` |
| `code/<language>` | Generic code | Any language supported by pygments |
| `text/x-diff` | Unified diff | Diff output |

**Alternative Approach (Markdown Integration):**
- Markdown code blocks automatically use syntax highlighting
- Language extracted from code fence info string
- No separate content type needed

### 4.4 Performance Considerations for Virtual Rendering

**Pre-rendering Cost:**
- Syntax highlighting is CPU-intensive
- Large code blocks may take noticeable time
- Must not block UI during append

**Recommendations:**

1. **Cache Highlighted Results:**
   ```python
   class SyntaxHighlight:
       def __init__(self, ...):
           self._highlighted_cache: dict[str, Text] = {}
           self._cache_key: str | None = None
   ```

2. **Lazy Rendering:**
   - Only highlight when content is visible
   - For virtual rendering, highlight happens during `render_to_strips()`

3. **Size Limits:**
   - Consider warning for very large code blocks (>10,000 lines)
   - Provide `max_lines` parameter to truncate display

---

## 5. Language Detection Strategy

### 5.1 Explicit Language Specification (Preferred)

The primary method should be explicit language specification:

```python
# Via widget parameter
SyntaxHighlight(code=source, language="python")

# Via content_type metadata
metadata={"content_type": "code/python"}
```

**Advantages:**
- Deterministic behavior
- No ambiguity
- Clear user intent

### 5.2 Auto-Detection Support

Optional auto-detection for cases where language is unknown:

```python
class SyntaxHighlight(Widget):
    def __init__(self, code: str, language: str | None = None, ...):
        if language is None:
            language = self._detect_language(code)
```

**Detection Heuristics:**
- File extension patterns (shebang, import statements)
- Language-specific keywords
- Syntax patterns

**Limitations:**
- May be incorrect for ambiguous code
- Adds processing overhead
- Should be opt-in, not default

### 5.3 Supported Languages

**Tier 1 (Priority Support):**
- Python (`python`, `py`)
- JavaScript (`javascript`, `js`, `typescript`, `ts`)
- Bash/Shell (`bash`, `sh`, `shell`, `zsh`)
- JSON (`json`)
- YAML (`yaml`, `yml`)

**Tier 2 (Common Languages):**
- C/C++
- Java
- Go
- Rust
- HTML/CSS
- SQL

**Tier 3 (Extended Support):**
- All pygments-lexers languages (200+ languages)

### 5.4 Unknown Language Fallback

When language is not recognized:

```python
def _get_lexer(self, language: str | None, code: str) -> Lexer:
    """Get appropriate lexer for language."""
    if language:
        try:
            return get_lexer_by_name(language)
        except ClassNotFound:
            pass  # Fall through to auto-detection

    if self._auto_detect:
        try:
            return guess_lexer(code)
        except ClassNotFound:
            pass  # Fall through to default

    return TextLexer()  # Plain text fallback
```

---

## 6. Performance Optimizations

### 6.1 Caching Strategy

**Cache Key Components:**
- Code content (hash)
- Language identifier
- Theme name
- Width (for wrapping)

```python
def _get_cache_key(self) -> str:
    """Generate cache key for current state."""
    return f"{hash(self.code)}:{self.language}:{self.theme}"
```

**Cache Invalidation:**
- On `code` change: Invalidate and re-highlight
- On `language` change: Invalidate and re-highlight
- On `theme` change: Re-highlight with new theme
- On `width` change: Re-wrap only (reuse highlighted content)

### 6.2 Large Code Block Handling

**Problem:** Very large code blocks can cause performance issues.

**Solutions:**

1. **Virtual Scrolling Within Widget:**
   - For standalone use, widget can scroll internally
   - Only render visible portion

2. **Truncation with Indicator:**
   ```python
   SyntaxHighlight(
       code=large_code,
       max_lines=500,  # Truncate display
       show_truncation_indicator=True,
   )
   ```

3. **Progressive Rendering:**
   - Render first N lines immediately
   - Background thread highlights remaining lines
   - Update display incrementally

### 6.3 Memory Considerations

**Strip Storage:**
- Pre-rendered strips are stored in Conversation's `_strips` list
- Each strip contains segments with styles
- Memory is bounded by total line count

**Recommendations:**
- Code blocks should respect conversation's memory pruning
- Consider storing only visible lines for very large blocks
- Clear cache when widget is removed from DOM

---

## 7. Accessibility Considerations

### 7.1 Color Contrast (WCAG AA Compliance)

**Requirement:** All syntax highlighting must maintain 4.5:1 contrast ratio.

**Pygments Theme Analysis:**

| Theme | Background | Text Contrast | Notes |
|-------|------------|---------------|-------|
| `monokai` | #272822 | ~7:1 | Excellent for dark theme |
| `github-light` | #ffffff | ~8:1 | Good for light theme |
| `dracula` | #282a36 | ~9:1 | Good for dark theme |
| `vim` | #000000 | Varies | Check individual colors |

**Custom Theme Creation:**

For themes that don't meet WCAG AA, create custom accessible variants:

```python
# Custom accessible monokai variant
ACCESSIBLE_MONOKAI = {
    "background": "#272822",
    "text": "#f8f8f2",      # Higher contrast
    "keyword": "#f92672",   # Check: must be visible
    "string": "#e6db74",
    "comment": "#75715e",   # Muted but readable
    # ... additional token colors
}
```

### 7.2 Semantic Information

**Screen Reader Announcements:**
- Code blocks should announce: "code block, language: python"
- Line numbers should be announced: "line 1, line 2"
- Highlighted lines should announce: "highlighted line 5"

**Implementation:**
```python
# Accessibility properties on the widget
def get_aria_label(self) -> str:
    """Return accessible name for screen readers."""
    language_name = self.language or "unknown"
    return f"code block, language: {language_name}"
```

### 7.3 Color Independence

**Requirement:** Information should not rely solely on color.

**Syntax Highlighting Considerations:**
- Keywords: Color + bold
- Strings: Color + italic (or quotes)
- Comments: Color + italic (clearly distinct)
- Line numbers: Muted color + right-aligned

**Visual Indicators:**
- Language badge above code block
- Line numbers in separate visual column
- Border around code block

---

## 8. Integration Patterns

### 8.1 Standalone Widget Usage

**Use Case:** Display code in a dedicated view (e.g., code viewer app).

```python
from textual.app import App, ComposeResult
from clitic import SyntaxHighlight

class CodeViewerApp(App):
    def compose(self) -> ComposeResult:
        yield SyntaxHighlight(
            code=source_code,
            language="python",
            show_line_numbers=True,
            theme="monokai",
        )
```

**Widget Features:**
- Full Textual widget lifecycle
- CSS styling support
- Focus handling
- Keyboard navigation

### 8.2 Embedded in Conversation

**Use Case:** Code blocks in chat messages.

```python
# Via MarkdownPlugin (recommended)
conversation.append(
    "assistant",
    "```python\nprint('hello')\n```",
    metadata={"content_type": "text/markdown"},
)

# Via direct code content type
conversation.append(
    "assistant",
    "print('hello')",
    metadata={"content_type": "code/python"},
)
```

**Plugin Architecture:**
- CodePlugin registered with App
- Handles `code/*` content types
- Delegates to SyntaxHighlight widget for rendering

### 8.3 Markdown Code Block Integration

**Recommended Approach:**

Enhance `MarkdownPlugin` to use `SyntaxHighlight` for code blocks:

```python
class MarkdownPlugin(ContentPlugin):
    def __init__(self, code_theme: str | None = None):
        self._code_theme = code_theme

    def render(self, content: str | Renderable) -> Markdown:
        # Rich's Markdown already supports syntax highlighting
        # But we can customize the theme
        return Markdown(str(content), code_theme=self._code_theme)
```

**Rich's Built-in Support:**
- Rich's `Markdown` class already supports pygments
- Pass `code_theme` parameter for customization
- Language extracted from code fence automatically

### 8.4 Diff Plugin Integration

**Use Case:** Unified diff rendering with syntax highlighting.

```python
class DiffPlugin(ContentPlugin):
    def can_render(self, content_type: str, content: str | Renderable) -> bool:
        return content_type in ("text/x-diff", "diff")

    def render(self, content: str | Renderable) -> Panel:
        # Parse diff and highlight each section
        # Use SyntaxHighlight for context lines
        pass
```

---

## 9. Acceptance Criteria UX Review

| Criterion | UX Assessment | Implementation Notes |
|-----------|---------------|---------------------|
| `src/clitic/widgets/syntax_highlight.py` exists | Clear widget location | Follows project structure |
| Supports multiple languages | Good - use pygments | Document supported languages |
| Uses Rich/pygments for highlighting | Good choice | Leverage existing Rich integration |
| Configurable theme | Needs design | See Section 3 for mapping strategy |
| Works within virtual rendering | Critical | See Section 4 for strip rendering |
| Can be used standalone | Good - dual mode | Widget + render_to_strips method |
| Unit tests for highlighting | Essential | Include contrast tests for accessibility |

---

## 10. Design Decisions Required

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Language detection | Explicit only vs Auto-detect vs Hybrid | Explicit only for v1, auto-detect opt-in |
| Theme mapping | Hardcoded vs Configurable | Hardcoded mapping with custom theme override |
| Content type namespace | `code/python` vs `text/x-python` | `code/<language>` for clarity |
| Line numbers | Always vs Never vs Configurable | Configurable, default off |
| Max lines limit | No limit vs Fixed vs Configurable | Configurable, default 10,000 |
| Cache invalidation | Time-based vs Content-based | Content-based (hash) |
| Unknown language handling | Error vs Plain text vs Auto-detect | Plain text fallback |

---

## 11. Recommendations Summary

### 11.1 Implementation Priority

1. **P0 - Critical:**
   - Core SyntaxHighlight widget with explicit language
   - Basic theme mapping (dark/light)
   - Strip rendering for Conversation integration
   - Fallback to plain text for unknown languages

2. **P1 - Essential:**
   - CodePlugin for `code/*` content types
   - MarkdownPlugin integration for code blocks
   - Line numbers support
   - Language auto-detection (opt-in)

3. **P2 - Important:**
   - Custom theme support
   - Highlighted lines feature
   - Large code block optimization
   - Accessibility improvements

4. **P3 - Nice-to-have:**
   - Code folding
   - Copy button for code
   - Line-based navigation

### 11.2 Testing Requirements

**Unit Tests:**
- Language detection correctness
- Theme mapping accuracy
- Strip rendering output
- Fallback behavior

**Visual Tests:**
- Screenshot comparison for different themes
- Contrast ratio validation
- Line number alignment

**Performance Tests:**
- Large code block rendering time
- Memory usage for 10,000+ line files
- Cache hit/miss ratios

### 11.3 Documentation Needs

**User Documentation:**
- How to use SyntaxHighlight widget
- Supported languages list
- Theme customization
- Content type specification

**Developer Documentation:**
- Integration with Conversation
- Creating custom theme mappings
- Performance tuning guidelines

---

## 12. Appendix: Implementation Outline

### 12.1 File Structure

```
src/clitic/widgets/
  syntax_highlight.py    # Main widget class

src/clitic/plugins/
  code.py               # CodePlugin for content type routing

src/clitic/themes/
  highlight.py          # Theme mapping utilities
```

### 12.2 Key Methods

```python
class SyntaxHighlight(Widget):
    def __init__(self, code: str, language: str | None = None, ...):
        ...

    def render(self) -> RenderResult:
        """Render widget for standalone use."""
        ...

    def render_to_strips(self, width: int) -> list[Strip]:
        """Pre-render for Conversation virtual rendering."""
        ...

    def _highlight_code(self) -> Text:
        """Apply syntax highlighting to code."""
        ...

    def _get_lexer(self) -> Lexer:
        """Get pygments lexer for language."""
        ...

    def _get_theme_style(self) -> Style:
        """Get pygments style for current theme."""
        ...
```

### 12.3 CodePlugin Outline

```python
class CodePlugin(ContentPlugin):
    """Plugin for rendering code content with syntax highlighting."""

    @property
    def name(self) -> str:
        return "Code"

    @property
    def priority(self) -> int:
        return 5  # Lower than markdown

    def can_render(self, content_type: str, content: str | Renderable) -> bool:
        return content_type.startswith("code/")

    def render(self, content: str | Renderable) -> SyntaxHighlight:
        # Extract language from content_type (e.g., "code/python" -> "python")
        language = content_type.split("/", 1)[1]
        return SyntaxHighlight(code=str(content), language=language)
```

---

**Document Status:** Complete
**Next Review:** After implementation
**Related Documents:**
- `analysis/ux-plugin-integration.md` - Plugin integration design
- `analysis/ui-ux.md` - Overall UX analysis
- `TODO.md` - Task tracking