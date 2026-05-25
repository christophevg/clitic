"""Diff content plugin for clitic.

This module provides a Diff plugin that renders unified diff content
with color-coded line annotations using Rich's Text renderer.
"""

from __future__ import annotations

from rich.segment import Segment as RichSegment
from rich.style import Style
from rich.text import Text
from textual.strip import Strip

from clitic.plugins.base import ContentPlugin, Renderable

# Styles for diff line types
# Colors from Claude Code / GitHub diff rendering
_DIFF_ADDED_PREFIX_STYLE = Style(color="green", bold=True, bgcolor="#e3fedf")
_DIFF_ADDED_TEXT_STYLE = Style(bgcolor="#e3fedf")
_DIFF_REMOVED_PREFIX_STYLE = Style(color="red", bold=True, bgcolor="#f9dddd")
_DIFF_REMOVED_TEXT_STYLE = Style(bgcolor="#f9dddd")
_DIFF_HEADER_STYLE = Style(color="cyan", bold=True)
_DIFF_HUNK_STYLE = Style(color="yellow")
_DIFF_MARK_STYLE = Style(color="magenta")
_DIFF_DEFAULT_STYLE = Style()


class DiffPlugin(ContentPlugin):
  """Content plugin for rendering unified diff output.

  This plugin handles diff content (content_type starting with "text/x-diff",
  "diff", or "application/x-diff") and renders it with color-coded annotations:

  - ``+`` prefix in green, rest of line on light green background
  - ``-`` prefix in red, rest of line on light red background
  - ``@@`` hunk headers in yellow
  - ``---`` / ``+++`` file headers in cyan
  - Context lines in default style

  Attributes:
    name: Human-readable name ("Diff").
    priority: Plugin priority (15, higher than Markdown for explicit diffs).
  """

  @property
  def name(self) -> str:
    """Return the human-readable name of this plugin."""
    return "Diff"

  @property
  def priority(self) -> int:
    """Return the priority for this plugin.

    Higher than Markdown (10) so explicit diff content types are handled
    by this plugin rather than being rendered as markdown.

    Returns:
      Priority value (15 by default for diff).
    """
    return 15

  def can_render(self, content_type: str, content: str | Renderable) -> bool:
    """Check if this plugin can render the given content.

    This plugin handles content types:
    - "text/x-diff" (standard MIME type)
    - "diff" (short form)
    - "application/x-diff" (alternative MIME type)
    - "text/x-patch" (patch files)
    - "x-diff" (legacy short form)

    Args:
      content_type: MIME type or identifier for the content.
      content: The content to potentially render (not used for detection).

    Returns:
      True if this plugin can render the content, False otherwise.
    """
    normalized = content_type.lower().strip()
    diff_types = {
      "text/x-diff",
      "diff",
      "application/x-diff",
      "text/x-patch",
      "x-diff",
    }
    return normalized in diff_types or normalized.startswith("diff/")

  def render(self, content: str | Renderable) -> Text:
    """Render diff content to a Rich Text object with color coding.

    Parses unified diff format and applies color-coded styles:
    - Added lines (+): green prefix, neutral text on light green background
    - Removed lines (-): red prefix, neutral text on light red background
    - Hunk headers (@@) in yellow
    - File headers (---, +++) in cyan
    - Context lines in default style

    Args:
      content: The diff content to render.

    Returns:
      A Rich Text renderable with styled diff output.
    """
    diff_text = str(content)
    result = Text()
    lines = diff_text.split("\n")

    for i, line in enumerate(lines):
      if i > 0:
        result.append("\n")

      # File headers must be checked before +/- prefixes
      if line.startswith("--- ") or line.startswith("+++ "):
        style = self._line_style(line)
        result.append(line, style=style)
      elif line.startswith("+"):
        result.append("+", style=_DIFF_ADDED_PREFIX_STYLE)
        result.append(line[1:], style=_DIFF_ADDED_TEXT_STYLE)
      elif line.startswith("-"):
        result.append("-", style=_DIFF_REMOVED_PREFIX_STYLE)
        result.append(line[1:], style=_DIFF_REMOVED_TEXT_STYLE)
      else:
        style = self._line_style(line)
        result.append(line, style=style)

    return result

  def render_to_strips(self, content: str | Renderable, width: int) -> list[Strip]:
    """Render diff content directly to Strips with full-width backgrounds.

    This method handles width-aware rendering so that added/removed lines
    have their background color spanning the full line width.

    Args:
      content: The diff content to render.
      width: The render width.

    Returns:
      A list of Strip objects, one per line.
    """
    from rich.cells import cell_len

    diff_text = str(content)
    lines = diff_text.split("\n")
    strips: list[Strip] = []

    for line in lines:
      segments: list[RichSegment] = []

      # File headers must be checked before +/- prefixes
      if line.startswith("--- ") or line.startswith("+++ "):
        style = self._line_style(line)
        segments.append(RichSegment(line, style))
        # Always pad header lines to full width to avoid crop_extend issues
        line_cell_len = cell_len(line)
        if line_cell_len < width:
          segments.append(RichSegment(" " * (width - line_cell_len), style))
        strips.append(Strip(segments, None))  # Let Textual calculate cell length
      elif line.startswith("+"):
        text = line[1:]
        text_cell_len = cell_len(text)
        # Calculate total cells used by prefix and text
        total_cells = 1 + text_cell_len  # 1 for the '+' prefix
        padding = max(0, width - total_cells)

        # Use separate segments for prefix, text, and padding
        segments.append(RichSegment("+", _DIFF_ADDED_PREFIX_STYLE))
        if text:
          segments.append(RichSegment(text, _DIFF_ADDED_TEXT_STYLE))
        # Always add padding to ensure strip cell length matches width
        # This prevents crop_extend from having mismatched cached vs actual length
        segments.append(RichSegment(" " * padding, _DIFF_ADDED_TEXT_STYLE))

        strips.append(Strip(segments, None))  # Let Textual calculate cell length
      elif line.startswith("-"):
        text = line[1:]
        text_cell_len = cell_len(text)
        total_cells = 1 + text_cell_len  # 1 for the '-' prefix
        padding = max(0, width - total_cells)

        # Use separate segments for prefix, text, and padding
        segments.append(RichSegment("-", _DIFF_REMOVED_PREFIX_STYLE))
        if text:
          segments.append(RichSegment(text, _DIFF_REMOVED_TEXT_STYLE))
        # Always add padding to ensure strip cell length matches width
        segments.append(RichSegment(" " * padding, _DIFF_REMOVED_TEXT_STYLE))

        strips.append(Strip(segments, None))  # Let Textual calculate cell length
      else:
        style = self._line_style(line)
        segments.append(RichSegment(line, style))
        # Pad other lines to full width
        line_cell_len = cell_len(line)
        if line_cell_len < width:
          segments.append(RichSegment(" " * (width - line_cell_len), style))
        strips.append(Strip(segments, None))  # Let Textual calculate cell length

    return strips

  def _line_style(self, line: str) -> Style:
    """Determine the Rich Style for a diff line.

    Args:
      line: A single line from the diff output.

    Returns:
      The appropriate Rich Style for the line type.
    """
    if not line:
      return _DIFF_DEFAULT_STYLE

    # File headers
    if line.startswith("--- ") or line.startswith("+++ "):
      return _DIFF_HEADER_STYLE

    # Hunk headers
    if line.startswith("@@"):
      return _DIFF_HUNK_STYLE

    # Added lines - prefix handled separately in render methods
    if line.startswith("+"):
      return _DIFF_ADDED_PREFIX_STYLE

    # Removed lines - prefix handled separately in render methods
    if line.startswith("-"):
      return _DIFF_REMOVED_PREFIX_STYLE

    # Git extended headers (e.g., "diff --git", "index ", "new file mode")
    if (
      line.startswith("diff ")
      or line.startswith("index ")
      or line.startswith("new ")
      or line.startswith("deleted ")
      or line.startswith("rename ")
      or line.startswith("similarity ")
      or line.startswith("dissimilarity ")
    ):
      return _DIFF_HEADER_STYLE

    # No newline marker
    if line.startswith("\\"):
      return _DIFF_MARK_STYLE

    # Context lines (start with space or are unchanged)
    return _DIFF_DEFAULT_STYLE
