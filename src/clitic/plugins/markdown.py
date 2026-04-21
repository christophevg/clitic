"""Markdown content plugin for clitic.

This module provides a Markdown plugin that renders Markdown content
using Rich's Markdown renderer.
"""

from rich.markdown import Markdown

from clitic.plugins.base import ContentPlugin, Renderable


class MarkdownPlugin(ContentPlugin):
  """Content plugin for rendering Markdown.

  This plugin handles Markdown content (content_type starting with "text/markdown"
  or "markdown/") and renders it using Rich's Markdown renderer, which supports:

  - Headers (h1-h6)
  - Paragraphs
  - Lists (ordered and unordered)
  - Inline code with backticks
  - Code blocks with language tags
  - Links

  Attributes:
    name: Human-readable name ("Markdown").
    priority: Plugin priority (10, high for default handling).
  """

  @property
  def name(self) -> str:
    """Return the human-readable name of this plugin."""
    return "Markdown"

  @property
  def priority(self) -> int:
    """Return the priority for this plugin.

    Higher priority means this plugin is checked first when determining
    which plugin should render content.

    Returns:
      Priority value (10 by default for markdown).
    """
    return 10

  def can_render(self, content_type: str, content: str | Renderable) -> bool:
    """Check if this plugin can render the given content.

    This plugin handles content types:
    - "text/markdown" (standard MIME type)
    - "markdown" (short form)
    - "markdown/*" (any markdown variant)

    Args:
      content_type: MIME type or identifier for the content.
      content: The content to potentially render (not used for detection).

    Returns:
      True if this plugin can render the content, False otherwise.
    """
    normalized = content_type.lower().strip()
    if normalized == "text/markdown":
      return True
    if normalized == "markdown":
      return True
    if normalized.startswith("markdown/"):
      return True
    return False

  def render(self, content: str | Renderable) -> Markdown:
    """Render Markdown content to a Rich Markdown renderable.

    Args:
      content: The Markdown content to render.

    Returns:
      A Rich Markdown renderable displaying the rendered content.
    """
    markdown_text = str(content)
    return Markdown(markdown_text)
