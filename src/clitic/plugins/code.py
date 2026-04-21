"""Code content plugin for clitic.

This module provides a Code plugin that renders source code content
using Rich's Syntax renderer for syntax highlighting.
"""

from rich.syntax import Syntax

from clitic.plugins.base import ContentPlugin, Renderable


class CodePlugin(ContentPlugin):
  """Content plugin for rendering source code with syntax highlighting.

  This plugin handles code content (content_type starting with "code/")
  and renders it using Rich's Syntax renderer with Pygments lexers.

  Attributes:
    name: Human-readable name ("Code").
    priority: Plugin priority (5, lower than Markdown for explicit code handling).
  """

  def __init__(self) -> None:
    """Initialize the CodePlugin."""
    self._content_type: str = ""
    self._theme: str | None = None

  @property
  def name(self) -> str:
    """Return the human-readable name of this plugin."""
    return "Code"

  @property
  def priority(self) -> int:
    """Return the priority for this plugin.

    Lower than Markdown (10) so explicit code/* content types are handled
    by this plugin rather than being rendered as markdown.

    Returns:
      Priority value (5 by default for code).
    """
    return 5

  def can_render(self, content_type: str, content: str | Renderable) -> bool:
    """Check if this plugin can render the given content.

    This plugin handles content types:
    - "code/*" (any code content with language in the subtype)
    - e.g., "code/python", "code/javascript", "code/rust"

    Args:
      content_type: MIME type or identifier for the content.
      content: The content to potentially render (not used for detection).

    Returns:
      True if this plugin can render the content, False otherwise.
    """
    normalized = content_type.lower().strip()
    if normalized.startswith("code/"):
      self._content_type = content_type
      return True
    return False

  def render(self, content: str | Renderable) -> Syntax:
    """Render code content to a Rich Syntax object.

    Args:
      content: The code content to render.

    Returns:
      A Rich Syntax renderable with syntax highlighting.
    """
    code_text = str(content)
    language = self._extract_language(self._content_type)
    theme = self._theme if self._theme else "monokai"

    return Syntax(
      code_text,
      lexer=language,
      theme=theme,
      line_numbers=True,
      word_wrap=False,
    )

  def with_theme(self, theme: str | None) -> "CodePlugin":
    """Set the theme for syntax highlighting.

    Args:
      theme: The Pygments theme to use.

    Returns:
      Self for method chaining.
    """
    self._theme = theme
    return self

  def _extract_language(self, content_type: str) -> str:
    """Extract the programming language from a content type.

    Args:
      content_type: The content type string (e.g., "code/python").

    Returns:
      The language name (e.g., "python"), or "text" if not found.
    """
    normalized = content_type.lower().strip()
    if normalized.startswith("code/"):
      return normalized[5:]  # Remove "code/" prefix
    return "text"
