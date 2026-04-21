"""Markdown content plugin for clitic.

This module provides a Markdown plugin that renders Markdown content
using Textual's built-in Markdown widget.
"""

from textual.widgets import Markdown

from clitic.plugins.base import ContentPlugin, Renderable


class MarkdownPlugin(ContentPlugin):
  """Content plugin for rendering Markdown.

  This plugin handles Markdown content (content_type starting with "text/markdown"
  or "markdown/") and renders it using Textual's Markdown widget, which supports:

  - Headers (h1-h6)
  - Paragraphs
  - Lists (ordered and unordered)
  - Inline code with backticks
  - Code blocks with language tags
  - Links (clickable when open_links=True)

  Attributes:
    name: Human-readable name ("Markdown").
    priority: Plugin priority (10, high for default handling).
    open_links: Whether links should be clickable.
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

  def __init__(self, *, open_links: bool = True) -> None:
    """Initialize the Markdown plugin.

    Args:
      open_links: Whether links should be clickable. Defaults to True.
    """
    self._open_links = open_links

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
    """Render Markdown content to a Textual Markdown widget.

    Args:
      content: The Markdown content to render.

    Returns:
      A Textual Markdown widget displaying the rendered content.

    Raises:
      RenderError: If rendering fails (currently never raised, but
        reserved for future error handling).
    """
    markdown_text = str(content)
    return Markdown(markdown_text, open_links=self._open_links)

  @property
  def open_links(self) -> bool:
    """Whether links should be clickable."""
    return self._open_links
