"""Tests for the Markdown plugin.

This module tests the MarkdownPlugin class for rendering Markdown content
using Rich's Markdown renderer.
"""

import pytest
from rich.markdown import Markdown

from clitic.plugins import MarkdownPlugin


class TestMarkdownPluginProperties:
  """Tests for MarkdownPlugin properties."""

  def test_name_returns_markdown(self) -> None:
    """The name property should return 'Markdown'."""
    plugin = MarkdownPlugin()
    assert plugin.name == "Markdown"

  def test_priority_returns_10(self) -> None:
    """The priority property should return 10."""
    plugin = MarkdownPlugin()
    assert plugin.priority == 10


class TestMarkdownPluginCanRender:
  """Tests for MarkdownPlugin.can_render method."""

  def test_can_render_text_markdown(self) -> None:
    """Should accept 'text/markdown' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("text/markdown", "# Hello") is True

  def test_can_render_markdown(self) -> None:
    """Should accept 'markdown' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("markdown", "# Hello") is True

  def test_can_render_markdown_variant(self) -> None:
    """Should accept 'markdown/*' content types."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("markdown/commonmark", "# Hello") is True
    assert plugin.can_render("markdown/gfm", "# Hello") is True

  def test_can_render_case_insensitive(self) -> None:
    """Should handle content type case-insensitively."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("TEXT/MARKDOWN", "# Hello") is True
    assert plugin.can_render("Markdown", "# Hello") is True
    assert plugin.can_render("MARKDOWN/GFM", "# Hello") is True

  def test_can_render_strips_whitespace(self) -> None:
    """Should handle content type with surrounding whitespace."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("  text/markdown  ", "# Hello") is True
    assert plugin.can_render("\tmarkdown\t", "# Hello") is True

  def test_cannot_render_text_plain(self) -> None:
    """Should reject 'text/plain' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("text/plain", "# Hello") is False

  def test_cannot_render_text_html(self) -> None:
    """Should reject 'text/html' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("text/html", "<h1>Hello</h1>") is False

  def test_cannot_render_application_json(self) -> None:
    """Should reject 'application/json' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("application/json", '{"key": "value"}') is False

  def test_cannot_render_code_python(self) -> None:
    """Should reject 'code/python' content type."""
    plugin = MarkdownPlugin()
    assert plugin.can_render("code/python", "print('hello')") is False

  def test_can_render_ignores_content(self) -> None:
    """Should only check content type, not content."""
    plugin = MarkdownPlugin()
    # Empty content should still return True for markdown content type
    assert plugin.can_render("text/markdown", "") is True
    # Non-markdown content should return True for markdown content type
    assert plugin.can_render("text/markdown", "not valid markdown {{{") is True


class TestMarkdownPluginRender:
  """Tests for MarkdownPlugin.render method."""

  def test_render_returns_markdown_object(self) -> None:
    """render should return a Rich Markdown object."""
    plugin = MarkdownPlugin()
    result = plugin.render("# Hello World")
    assert isinstance(result, Markdown)

  def test_render_with_simple_header(self) -> None:
    """render should handle simple header."""
    plugin = MarkdownPlugin()
    result = plugin.render("# Hello World")
    assert isinstance(result, Markdown)

  def test_render_with_paragraph(self) -> None:
    """render should handle paragraph text."""
    plugin = MarkdownPlugin()
    result = plugin.render("This is a paragraph.")
    assert isinstance(result, Markdown)

  def test_render_with_ordered_list(self) -> None:
    """render should handle ordered list."""
    plugin = MarkdownPlugin()
    markdown_text = "1. First item\n2. Second item\n3. Third item"
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_unordered_list(self) -> None:
    """render should handle unordered list."""
    plugin = MarkdownPlugin()
    markdown_text = "- First item\n- Second item\n- Third item"
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_inline_code(self) -> None:
    """render should handle inline code."""
    plugin = MarkdownPlugin()
    result = plugin.render("Use `print()` for output.")
    assert isinstance(result, Markdown)

  def test_render_with_code_block(self) -> None:
    """render should handle code block with language."""
    plugin = MarkdownPlugin()
    markdown_text = """```python
def hello():
    print("Hello, World!")
```"""
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_code_block_no_language(self) -> None:
    """render should handle code block without language."""
    plugin = MarkdownPlugin()
    markdown_text = """```
Plain code block
```"""
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_link(self) -> None:
    """render should handle links."""
    plugin = MarkdownPlugin()
    result = plugin.render("[Click here](https://example.com)")
    assert isinstance(result, Markdown)

  def test_render_with_headers_all_levels(self) -> None:
    """render should handle all header levels (h1-h6)."""
    plugin = MarkdownPlugin()
    markdown_text = """# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6"""
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_nested_content(self) -> None:
    """render should handle nested content."""
    plugin = MarkdownPlugin()
    markdown_text = """# Main Header

This is a paragraph with **bold** and *italic* text.

## Sub Header

- List item 1
- List item 2
  - Nested item

```python
def example():
    return "code block"
```

[Link to example](https://example.com)"""
    result = plugin.render(markdown_text)
    assert isinstance(result, Markdown)

  def test_render_with_renderable_object(self) -> None:
    """render should accept objects with __str__ method."""
    plugin = MarkdownPlugin()

    class CustomRenderable:
      def __str__(self) -> str:
        return "# Custom Content"

    custom = CustomRenderable()
    result = plugin.render(custom)
    assert isinstance(result, Markdown)

  def test_render_empty_content(self) -> None:
    """render should handle empty content."""
    plugin = MarkdownPlugin()
    result = plugin.render("")
    assert isinstance(result, Markdown)


class TestMarkdownPluginRenderAsync:
  """Tests for MarkdownPlugin.render_async method."""

  @pytest.mark.asyncio
  async def test_render_async_returns_markdown_object(self) -> None:
    """render_async should return a Rich Markdown object."""
    plugin = MarkdownPlugin()
    result = await plugin.render_async("# Hello World")
    assert isinstance(result, Markdown)

  @pytest.mark.asyncio
  async def test_render_async_uses_render(self) -> None:
    """render_async should delegate to render by default."""
    plugin = MarkdownPlugin()
    sync_result = plugin.render("# Test")
    async_result = await plugin.render_async("# Test")
    # Both should return Markdown objects
    assert isinstance(sync_result, Markdown)
    assert isinstance(async_result, Markdown)


class TestMarkdownPluginIntegration:
  """Integration tests for MarkdownPlugin."""

  def test_multiple_plugins_independently(self) -> None:
    """Test that multiple plugin instances work independently."""
    plugin1 = MarkdownPlugin()
    plugin2 = MarkdownPlugin()

    assert plugin1.name == "Markdown"
    assert plugin2.name == "Markdown"
