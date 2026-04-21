"""Tests for the Code plugin.

This module tests the CodePlugin class for rendering source code content
using Rich's Syntax renderer.
"""

from rich.syntax import Syntax

from clitic.plugins import CodePlugin


class TestCodePluginProperties:
  """Tests for CodePlugin properties."""

  def test_name_returns_code(self) -> None:
    """The name property should return 'Code'."""
    plugin = CodePlugin()
    assert plugin.name == "Code"

  def test_priority_returns_5(self) -> None:
    """The priority property should return 5."""
    plugin = CodePlugin()
    assert plugin.priority == 5


class TestCodePluginCanRender:
  """Tests for CodePlugin.can_render method."""

  def test_can_render_code_python(self) -> None:
    """Should accept 'code/python' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("code/python", "print('hello')") is True

  def test_can_render_code_javascript(self) -> None:
    """Should accept 'code/javascript' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("code/javascript", "console.log('hello')") is True

  def test_can_render_code_rust(self) -> None:
    """Should accept 'code/rust' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("code/rust", "fn main() {}") is True

  def test_can_render_code_with_suffix(self) -> None:
    """Should accept 'code/*' content types."""
    plugin = CodePlugin()
    assert plugin.can_render("code/go", "package main") is True
    assert plugin.can_render("code/ruby", "puts 'hello'") is True
    assert plugin.can_render("code/typescript", "const x = 1") is True

  def test_can_render_case_insensitive(self) -> None:
    """Should handle content type case-insensitively."""
    plugin = CodePlugin()
    assert plugin.can_render("CODE/Python", "print()") is True
    assert plugin.can_render("Code/JavaScript", "console.log()") is True

  def test_can_render_strips_whitespace(self) -> None:
    """Should handle content type with surrounding whitespace."""
    plugin = CodePlugin()
    assert plugin.can_render("  code/python  ", "print()") is True
    assert plugin.can_render("\tcode/rust\t", "fn main()") is True

  def test_cannot_render_text_plain(self) -> None:
    """Should reject 'text/plain' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("text/plain", "hello world") is False

  def test_cannot_render_text_markdown(self) -> None:
    """Should reject 'text/markdown' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("text/markdown", "# Header") is False

  def test_cannot_render_application_json(self) -> None:
    """Should reject 'application/json' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("application/json", '{"key": "value"}') is False

  def test_cannot_render_markdown(self) -> None:
    """Should reject 'markdown' content type."""
    plugin = CodePlugin()
    assert plugin.can_render("markdown", "# Header") is False

  def test_can_render_stores_content_type(self) -> None:
    """can_render should store content_type for later use in render."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "print()")
    assert plugin._content_type == "code/python"


class TestCodePluginRender:
  """Tests for CodePlugin.render method."""

  def test_render_returns_rich_syntax(self) -> None:
    """render should return a Rich Syntax object."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "print('hello')")
    result = plugin.render("print('hello')")
    assert isinstance(result, Syntax)

  def test_render_uses_python_lexer(self) -> None:
    """render should use python lexer for code/python."""
    from pygments.lexers import PythonLexer

    plugin = CodePlugin()
    plugin.can_render("code/python", "print('hello')")
    result = plugin.render("print('hello')")
    assert isinstance(result.lexer, PythonLexer)

  def test_render_uses_javascript_lexer(self) -> None:
    """render should use javascript lexer for code/javascript."""
    from pygments.lexers import JavascriptLexer

    plugin = CodePlugin()
    plugin.can_render("code/javascript", "console.log()")
    result = plugin.render("console.log()")
    assert isinstance(result.lexer, JavascriptLexer)

  def test_render_uses_rust_lexer(self) -> None:
    """render should use rust lexer for code/rust."""
    from pygments.lexers import RustLexer

    plugin = CodePlugin()
    plugin.can_render("code/rust", "fn main() {}")
    result = plugin.render("fn main() {}")
    assert isinstance(result.lexer, RustLexer)

  def test_render_sets_code_content(self) -> None:
    """render should set the code content."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "ignored")
    result = plugin.render("print('actual content')")
    assert result.code == "print('actual content')"

  def test_render_with_renderable_object(self) -> None:
    """render should accept objects with __str__ method."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "ignored")

    class CustomRenderable:
      def __str__(self) -> str:
        return "custom code content"

    custom = CustomRenderable()
    result = plugin.render(custom)
    assert result.code == "custom code content"

  def test_render_empty_content(self) -> None:
    """render should handle empty content."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "")
    result = plugin.render("")
    assert isinstance(result, Syntax)
    assert result.code == ""

  def test_render_has_line_numbers(self) -> None:
    """render should enable line numbers."""
    plugin = CodePlugin()
    plugin.can_render("code/python", "print('hello')")
    result = plugin.render("print('hello')")
    assert result.line_numbers is True


class TestCodePluginExtractLanguage:
  """Tests for CodePlugin._extract_language method."""

  def test_extract_python(self) -> None:
    """Should extract 'python' from 'code/python'."""
    plugin = CodePlugin()
    assert plugin._extract_language("code/python") == "python"

  def test_extract_javascript(self) -> None:
    """Should extract 'javascript' from 'code/javascript'."""
    plugin = CodePlugin()
    assert plugin._extract_language("code/javascript") == "javascript"

  def test_extract_with_whitespace(self) -> None:
    """Should handle content type with whitespace."""
    plugin = CodePlugin()
    assert plugin._extract_language("  code/rust  ") == "rust"

  def test_extract_case_preserved(self) -> None:
    """Should preserve case of language name."""
    plugin = CodePlugin()
    assert plugin._extract_language("code/Python") == "python"

  def test_extract_no_prefix_returns_text(self) -> None:
    """Should return 'text' if no 'code/' prefix."""
    plugin = CodePlugin()
    assert plugin._extract_language("python") == "text"

  def test_extract_empty_string(self) -> None:
    """Should return 'text' for empty string."""
    plugin = CodePlugin()
    assert plugin._extract_language("") == "text"


class TestCodePluginIntegration:
  """Integration tests for CodePlugin."""

  def test_multiple_plugins_independently(self) -> None:
    """Test that multiple plugin instances work independently."""
    from pygments.lexers import JavascriptLexer, PythonLexer

    plugin1 = CodePlugin()
    plugin2 = CodePlugin()

    plugin1.can_render("code/python", "print('one')")
    plugin2.can_render("code/javascript", "console.log('two')")

    assert plugin1._content_type == "code/python"
    assert plugin2._content_type == "code/javascript"

    result1 = plugin1.render("print('one')")
    result2 = plugin2.render("console.log('two')")

    assert isinstance(result1.lexer, PythonLexer)
    assert isinstance(result2.lexer, JavascriptLexer)

  def test_full_workflow(self) -> None:
    """Test full workflow: can_render -> render."""
    from pygments.lexers import PythonLexer

    plugin = CodePlugin()

    code = "def hello():\n    print('world')"

    # Step 1: Check if can render
    assert plugin.can_render("code/python", code) is True

    # Step 2: Render the content
    syntax = plugin.render(code)

    # Step 3: Verify the result
    assert isinstance(syntax, Syntax)
    assert syntax.code == code
    assert isinstance(syntax.lexer, PythonLexer)

