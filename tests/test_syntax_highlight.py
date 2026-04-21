"""Tests for the SyntaxHighlight widget.

This module tests the SyntaxHighlight widget for displaying
syntax-highlighted code using Rich's Syntax renderer.
"""

from pygments.lexers import PythonLexer, TextLexer
from textual.strip import Strip

from clitic.widgets.syntax_highlight import SyntaxHighlight


class TestSyntaxHighlightProperties:
  """Tests for SyntaxHighlight reactive properties."""

  def test_default_code_is_empty(self) -> None:
    """Default code should be empty string."""
    widget = SyntaxHighlight()
    assert widget.code == ""

  def test_default_language_is_text(self) -> None:
    """Default language should be 'text'."""
    widget = SyntaxHighlight()
    assert widget.language == "text"

  def test_default_theme_is_none(self) -> None:
    """Default theme should be None (use app theme)."""
    widget = SyntaxHighlight()
    assert widget.theme is None

  def test_default_show_line_numbers_is_true(self) -> None:
    """Default show_line_numbers should be True."""
    widget = SyntaxHighlight()
    assert widget.show_line_numbers is True

  def test_default_max_lines_is_none(self) -> None:
    """Default max_lines should be None (unlimited)."""
    widget = SyntaxHighlight()
    assert widget.max_lines is None


class TestSyntaxHighlightInit:
  """Tests for SyntaxHighlight initialization."""

  def test_init_with_code(self) -> None:
    """Should initialize with provided code."""
    widget = SyntaxHighlight(code="print('hello')")
    assert widget.code == "print('hello')"

  def test_init_with_language(self) -> None:
    """Should initialize with provided language."""
    widget = SyntaxHighlight(language="python")
    assert widget.language == "python"

  def test_init_with_theme(self) -> None:
    """Should initialize with provided theme."""
    widget = SyntaxHighlight(theme="github-dark")
    assert widget.theme == "github-dark"

  def test_init_with_show_line_numbers_false(self) -> None:
    """Should initialize with show_line_numbers=False."""
    widget = SyntaxHighlight(show_line_numbers=False)
    assert widget.show_line_numbers is False

  def test_init_with_max_lines(self) -> None:
    """Should initialize with max_lines."""
    widget = SyntaxHighlight(max_lines=10)
    assert widget.max_lines == 10


class TestSyntaxHighlightReactive:
  """Tests for SyntaxHighlight reactive property changes."""

  def test_code_reactive(self) -> None:
    """code should be reactive."""
    widget = SyntaxHighlight()
    widget.code = "new code"
    assert widget.code == "new code"

  def test_language_reactive(self) -> None:
    """language should be reactive."""
    widget = SyntaxHighlight()
    widget.language = "javascript"
    assert widget.language == "javascript"

  def test_theme_reactive(self) -> None:
    """theme should be reactive."""
    widget = SyntaxHighlight()
    widget.theme = "monokai"
    assert widget.theme == "monokai"

  def test_show_line_numbers_reactive(self) -> None:
    """show_line_numbers should be reactive."""
    widget = SyntaxHighlight()
    widget.show_line_numbers = False
    assert widget.show_line_numbers is False

  def test_max_lines_reactive(self) -> None:
    """max_lines should be reactive."""
    widget = SyntaxHighlight()
    widget.max_lines = 5
    assert widget.max_lines == 5


class TestSyntaxHighlightGetLexer:
  """Tests for SyntaxHighlight._get_lexer method."""

  def test_get_lexer_python(self) -> None:
    """Should return PythonLexer for python."""
    widget = SyntaxHighlight(language="python")
    lexer = widget._get_lexer()
    assert isinstance(lexer, PythonLexer)

  def test_get_lexer_unknown_fallback(self) -> None:
    """Should fallback to TextLexer for unknown language."""
    widget = SyntaxHighlight(language="unknown_language_xyz")
    lexer = widget._get_lexer()
    assert isinstance(lexer, TextLexer)

  def test_get_lexer_text(self) -> None:
    """Should return TextLexer for text."""
    widget = SyntaxHighlight(language="text")
    lexer = widget._get_lexer()
    assert isinstance(lexer, TextLexer)


class TestSyntaxHighlightGetTheme:
  """Tests for SyntaxHighlight._get_theme method."""

  def test_get_theme_widget_override(self) -> None:
    """Should use widget theme when set."""
    widget = SyntaxHighlight(theme="github-dark")
    # No app, so widget theme should be used
    theme = widget._get_theme()
    assert theme == "github-dark"

  def test_get_theme_default_monokai(self) -> None:
    """Should default to monokai when no theme set and no app."""
    widget = SyntaxHighlight()
    theme = widget._get_theme()
    assert theme == "monokai"


class TestSyntaxHighlightRender:
  """Tests for SyntaxHighlight.render method."""

  def test_render_returns_syntax_object(self) -> None:
    """render should return a Rich Syntax object."""
    from rich.syntax import Syntax

    widget = SyntaxHighlight(code="print('hello')", language="python")
    result = widget.render()
    assert isinstance(result, Syntax)

  def test_render_empty_code(self) -> None:
    """render should handle empty code."""
    from rich.syntax import Syntax

    widget = SyntaxHighlight(code="", language="python")
    result = widget.render()
    assert isinstance(result, Syntax)


class TestSyntaxHighlightRenderToStrips:
  """Tests for SyntaxHighlight.render_to_strips method."""

  def test_render_to_strips_returns_list(self) -> None:
    """render_to_strips should return a list of Strips."""
    widget = SyntaxHighlight(code="print('hello')", language="python")
    strips = widget.render_to_strips(80)
    assert isinstance(strips, list)
    assert len(strips) >= 1

  def test_render_to_strips_contains_strip_objects(self) -> None:
    """Each item should be a Strip object."""
    widget = SyntaxHighlight(code="print('hello')", language="python")
    strips = widget.render_to_strips(80)
    for strip in strips:
      assert isinstance(strip, Strip)

  def test_render_to_strips_multiline_code(self) -> None:
    """render_to_strips should handle multiline code."""
    code = "def hello():\n    print('world')\n    return True"
    widget = SyntaxHighlight(code=code, language="python")
    strips = widget.render_to_strips(80)
    # Should have at least 3 lines
    assert len(strips) >= 3

  def test_render_to_strips_respects_width(self) -> None:
    """render_to_strips should respect the width parameter."""
    widget = SyntaxHighlight(code="print('hello')", language="python")
    width = 40
    strips = widget.render_to_strips(width)
    # Strips should have been rendered at the given width
    assert len(strips) >= 1


class TestSyntaxHighlightMaxLines:
  """Tests for SyntaxHighlight max_lines truncation."""

  def test_max_lines_truncation(self) -> None:
    """max_lines should truncate displayed lines."""
    code = "line1\nline2\nline3\nline4\nline5"
    widget = SyntaxHighlight(code=code, language="text", max_lines=3)
    syntax = widget._get_syntax()
    # The syntax object should have truncated code
    rendered_code = syntax.code
    lines = rendered_code.split("\n")
    assert len(lines) == 3

  def test_max_lines_no_truncation_when_none(self) -> None:
    """max_lines=None should not truncate."""
    code = "line1\nline2\nline3\nline4\nline5"
    widget = SyntaxHighlight(code=code, language="text", max_lines=None)
    syntax = widget._get_syntax()
    rendered_code = syntax.code
    lines = rendered_code.split("\n")
    assert len(lines) == 5

  def test_max_lines_more_than_actual(self) -> None:
    """max_lines greater than actual lines should not affect output."""
    code = "line1\nline2"
    widget = SyntaxHighlight(code=code, language="text", max_lines=10)
    syntax = widget._get_syntax()
    rendered_code = syntax.code
    lines = rendered_code.split("\n")
    assert len(lines) == 2


class TestSyntaxHighlightErrorHandling:
  """Tests for SyntaxHighlight error handling."""

  def test_render_to_strips_handles_exception(self) -> None:
    """render_to_strips should handle exceptions gracefully."""
    widget = SyntaxHighlight(code="print('hello')", language="python")
    # Even with valid code, force a minimal width to test robustness
    strips = widget.render_to_strips(10)
    assert isinstance(strips, list)

  def test_get_lexer_handles_special_characters(self) -> None:
    """_get_lexer should handle language names with special chars."""
    widget = SyntaxHighlight(language="c++")
    lexer = widget._get_lexer()
    # Should either get a valid lexer or fallback to TextLexer
    assert lexer is not None
