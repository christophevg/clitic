# Consensus: syntax-highlighting-widget

**Task**: Create generic syntax highlighting widget for code content
**Date**: 2026-04-21
**Scope**: Frontend only

## Domain Agents Invoked

- `ui-ux-designer` - Approved

## Consensus Summary

### Widget API Design (Approved)

The widget should accept:
- `code: str` - The source code to highlight
- `language: str | None = None` - Explicit language specification
- `theme: str | None = None` - Pygments theme name
- `show_line_numbers: bool = False` - Line number display
- `max_lines: int | None = None` - Truncation for large code
- `highlight_lines: list[int] | None = None` - Lines to highlight

Reactive properties for dynamic updates are recommended.

### Virtual Rendering Integration (Approved)

The widget must support dual-mode operation:
1. **Standard Textual Widget**: Render directly as a widget
2. **Strip Rendering**: `render_to_strips(width: int) -> list[Strip]` for Conversation integration

Content type namespace: `code/<language>` (e.g., `code/python`)

### Theme Mapping Strategy (Approved)

```
App Theme -> Pygments Theme
-----------|----------------
dark       -> monokai
light      -> github-light

Fallback chain: widget.theme -> app.theme_name -> "monokai"
```

All selected themes must meet WCAG AA contrast requirements (4.5:1 ratio).

### Language Support (Approved)

**Tier 1** (Primary): Python, JavaScript, Bash, JSON, YAML
**Tier 2** (Secondary): C++, Java, Go, Rust
**Tier 3** (All pygments lexers): Available via pygments

- Explicit language specification is primary approach
- Auto-detection is opt-in (not default)
- Unknown language falls back to plain text

### Performance Strategy (Approved)

1. Content-based caching: hash(code + language + theme)
2. Lazy rendering for large code blocks
3. `max_lines` parameter for truncation
4. Memory-efficient strip storage aligned with Conversation's pruning

### Integration Points (Approved)

1. **Standalone**: Direct widget usage for code viewer
2. **CodePlugin**: New plugin for `code/*` content types
3. **MarkdownPlugin**: Enhancement for code block highlighting
4. **DiffPlugin**: Can use SyntaxHighlight for context lines

## Implementation Order

1. Create `SyntaxHighlight` widget with core rendering
2. Add `render_to_strips()` method for virtual rendering
3. Create `CodePlugin` for Conversation integration
4. Update MarkdownPlugin to use CodePlugin for code blocks
5. Add theme mapping utilities
6. Unit tests for all components

## Agent Sign-off

- [x] ui-ux-designer: Approved design recommendations