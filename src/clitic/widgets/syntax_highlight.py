"""Syntax highlighting widget for code display.

This module provides a Textual widget that renders code with syntax highlighting
using Rich's Syntax renderer and Pygments lexers.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound
from rich.console import Console, ConsoleRenderable
from rich.segment import Segment as RichSegment
from rich.syntax import Syntax
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from clitic.utils.highlight import get_pygments_theme

if TYPE_CHECKING:
  from pygments.lexer import Lexer

logger = logging.getLogger(__name__)


class SyntaxHighlight(Widget):
  """A widget for displaying syntax-highlighted code.

  This widget supports both standalone rendering and virtual rendering via
  strips for integration with Conversation's virtual rendering system.

  Attributes:
    code: The source code to highlight.
    language: The programming language for syntax highlighting.
    theme: The Pygments theme to use (overrides app theme).
    show_line_numbers: Whether to display line numbers.
    max_lines: Maximum number of lines to display (None for unlimited).
  """

  DEFAULT_CSS = """
  SyntaxHighlight {
    height: auto;
    padding: 0 1;
  }
  """

  code: reactive[str] = reactive("")
  language: reactive[str] = reactive("text")
  theme: reactive[str | None] = reactive(None)
  show_line_numbers: reactive[bool] = reactive(True)
  max_lines: reactive[int | None] = reactive(None)

  def __init__(
    self,
    code: str = "",
    *,
    language: str = "text",
    theme: str | None = None,
    show_line_numbers: bool = True,
    max_lines: int | None = None,
    name: str | None = None,
    id: str | None = None,  # noqa: A002
    classes: str | None = None,
    disabled: bool = False,
  ) -> None:
    """Initialize the SyntaxHighlight widget.

    Args:
      code: The source code to highlight.
      language: The programming language for syntax highlighting.
      theme: The Pygments theme to use (overrides app theme).
      show_line_numbers: Whether to display line numbers.
      max_lines: Maximum number of lines to display.
      name: Name of the widget.
      id: ID of the widget.
      classes: Space-separated CSS classes.
      disabled: Whether the widget is disabled.
    """
    super().__init__(name=name, id=id, classes=classes, disabled=disabled)
    self.code = code
    self.language = language
    self.theme = theme
    self.show_line_numbers = show_line_numbers
    self.max_lines = max_lines

  def _get_lexer(self) -> Lexer:
    """Get the Pygments lexer for the current language.

    Returns:
      A Pygments Lexer instance. Returns TextLexer for unknown languages.
    """
    try:
      return get_lexer_by_name(self.language)
    except ClassNotFound:
      logger.debug(f"Unknown language: {self.language}, using TextLexer")
      return TextLexer()

  def _get_theme(self) -> str:
    """Get the Pygments theme to use for highlighting.

    Resolution order:
    1. Widget's theme property
    2. App's theme_name
    3. Default "monokai"

    Returns:
      The Pygments theme name.
    """
    if self.theme is not None:
      return self.theme
    try:
      app_theme = getattr(self.app, "theme_name", None)
    except Exception:
      # Widget not mounted in app yet
      app_theme = None
    return get_pygments_theme(app_theme)

  def _get_syntax(self) -> Syntax:
    """Create a Rich Syntax object for the current code.

    Returns:
      A Rich Syntax renderable.
    """
    code = self.code
    if self.max_lines is not None:
      lines = code.split("\n")
      if len(lines) > self.max_lines:
        code = "\n".join(lines[: self.max_lines])

    return Syntax(
      code,
      lexer=self._get_lexer(),
      theme=self._get_theme(),
      line_numbers=self.show_line_numbers,
      word_wrap=False,
    )

  def render(self) -> Syntax:
    """Render the widget for standalone display.

    Returns:
      A Rich Syntax renderable.
    """
    return self._get_syntax()

  def render_to_strips(self, width: int) -> list[Strip]:
    """Render the widget to strips for Conversation integration.

    Args:
      width: The width to render at.

    Returns:
      A list of Strip objects, one per line of code.
    """
    try:
      console = Console(width=width)
      lines = list(console.render_lines(cast(ConsoleRenderable, self._get_syntax())))

      strips: list[Strip] = []
      for line in lines:
        segments = []
        for segment in line:
          if len(segment) == 2:
            segments.append(RichSegment(segment[0], segment[1], None))
          else:
            segments.append(segment)
        strips.append(Strip(segments, width))

      return strips if strips else [Strip([], width)]
    except Exception:
      logger.exception("Failed to render syntax highlight to strips")
      return [Strip([], width)]
