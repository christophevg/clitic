"""Scrollable content container for conversation messages.

This module provides the Conversation widget, a scrollable container
for displaying conversation messages with different roles using virtual
rendering for optimal performance with large content.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass

from rich.console import Console
from rich.segment import Segment as RichSegment
from rich.style import Style
from rich.text import Text
from textual.events import Resize
from textual.geometry import Size
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

_DEFAULT_WIDTH: int = 80


@dataclass
class _BlockData:
  """Internal dataclass for storing content block information.

  Attributes:
      block_id: Unique identifier for this block.
      role: The role of the message (user, assistant, system, tool).
      content: The text content of the message.
      line_count: Number of lines this block occupies when rendered.
  """

  block_id: str
  role: str
  content: str
  line_count: int = 0


class Conversation(ScrollView):
  """Scrollable content container for conversation messages.

  A virtual-scrolling container that efficiently displays conversation
  messages with different roles (user, assistant, system, tool).
  Uses Textual's Line API for O(1) visible line rendering, supporting
  100,000+ lines without performance degradation.

  Attributes:
      block_count: The number of content blocks in the conversation.
      auto_scroll: Whether to automatically scroll to new content.

  Example:
      ```python
      from textual.app import App, ComposeResult
      from clitic import Conversation

      class MyApp(App):
          def compose(self) -> ComposeResult:
              yield Conversation()

          def on_mount(self) -> None:
              conversation = self.query_one(Conversation)
              conversation.append("user", "Hello!")
              conversation.append("assistant", "Hi there!")
      ```
  """

  DEFAULT_CSS = """
  Conversation {
    height: 1fr;
    padding: 1;
    background: $surface;
  }

  Conversation.paused {
    border-top: thick $warning;
  }
  """

  BINDINGS = [
    ("up", "scroll_up", "Scroll up"),
    ("down", "scroll_down", "Scroll down"),
    ("pageup", "page_up", "Page up"),
    ("pagedown", "page_down", "Page down"),
    ("home", "scroll_home", "To start"),
    ("end", "scroll_end", "To end"),
  ]

  auto_scroll = reactive(True)

  def __init__(
    self,
    *,
    auto_scroll: bool = True,
    name: str | None = None,
    id: str | None = None,  # noqa: A002
    classes: str | None = None,
    disabled: bool = False,
  ) -> None:
    """Initialize the Conversation.

    Args:
        auto_scroll: Whether to automatically scroll to new content.
        name: Name of the widget.
        id: ID of the widget.
        classes: Space-separated CSS classes.
        disabled: Whether the widget is disabled.
    """
    self._blocks: list[_BlockData] = []
    self._block_counter: int = 0
    self._strips: list[Strip] = []
    self._cumulative_heights: list[int] = []  # Running total of lines per block
    self._total_lines: int = 0
    self._last_width: int = 0
    super().__init__(name=name, id=id, classes=classes, disabled=disabled)
    self.auto_scroll = auto_scroll

  def _get_content_width(self) -> int:
    """Get the available content width for rendering.

    Returns:
        The width available for content, accounting for padding.
    """
    region = self.scrollable_content_region
    if region and region.width > 0:
      # Account for horizontal padding from CSS (padding: 1 = 2 chars total)
      return max(1, region.width - 2)
    return _DEFAULT_WIDTH

  def _render_block_to_strips(self, block: _BlockData, width: int) -> list[Strip]:
    """Render a block's content to a list of Strips.

    Args:
        block: The block data to render.
        width: The width to render at (for text wrapping).

    Returns:
        List of Strip objects, one per line.
    """
    # Create the styled text based on role
    if block.role == "user":
      text = Text(f"[You] {block.content}", style=Style(bold=True, color="blue"))
    elif block.role == "assistant":
      text = Text(f"[Assistant] {block.content}", style=Style(bold=True, color="green"))
    elif block.role == "system":
      text = Text(f"[System] {block.content}", style=Style(bold=True, color="yellow"))
    elif block.role == "tool":
      text = Text(f"[Tool] {block.content}", style=Style(bold=True, color="magenta"))
    else:
      # Default styling for unknown roles
      text = Text(f"[{block.role}] {block.content}", style=Style(bold=True, color="grey62"))

    # Wrap the text to the available width
    # Using renderables requires converting to lines
    console = Console(width=width)
    lines = list(console.render_lines(text))

    # Convert each line to a Strip
    strips: list[Strip] = []
    for line in lines:
      # Ensure segments have 3-tuple format (text, style, control)
      segments = []
      for segment in line:
        if len(segment) == 2:
          # Add None for control if missing
          segments.append(RichSegment(segment[0], segment[1], None))
        else:
          segments.append(segment)
      strip = Strip(segments, width)
      strips.append(strip)

    # Add a blank line as margin between blocks
    blank_strip = Strip.blank(width, getattr(self, "rich_style", None))
    strips.append(blank_strip)

    return strips

  def _rerender_all_blocks(self) -> None:
    """Re-render all blocks with current width."""
    width = self._get_content_width()
    self._strips.clear()
    self._cumulative_heights.clear()
    self._total_lines = 0

    for block in self._blocks:
      block_strips = self._render_block_to_strips(block, width)
      block.line_count = len(block_strips)
      self._strips.extend(block_strips)
      self._total_lines += block.line_count
      self._cumulative_heights.append(self._total_lines)

    self._last_width = width
    # Use actual content region width for virtual size
    region = self.scrollable_content_region
    vwidth = region.width if region and region.width > 0 else width
    self.virtual_size = Size(vwidth, self._total_lines)
    # Don't call refresh() here - let the caller handle it

  def watch_scroll_y(self, old: float, new: float) -> None:
    """Watch for scroll position changes to manage auto_scroll state.

    Args:
        old: Previous scroll position.
        new: Current scroll position.
    """
    # Call parent's watch_scroll_y to ensure ScrollView updates properly
    super().watch_scroll_y(old, new)
    self._update_auto_scroll_from_scroll_position()

  def on_resize(self, event: Resize) -> None:
    """Handle resize events to re-render content with new width.

    Args:
        event: The resize event.
    """
    new_width = self._get_content_width()
    if new_width != self._last_width and self._blocks:
      self._rerender_all_blocks()

    self._update_auto_scroll_from_scroll_position()

  def _update_auto_scroll_from_scroll_position(self) -> None:
    """Update auto_scroll based on current scroll position."""
    max_y = self.max_scroll_y
    # If all content fits, auto-scroll should be enabled
    if max_y == 0:
      self.auto_scroll = True
    # At or near bottom - resume auto-scroll
    elif self.scroll_y >= max_y - 1:
      self.auto_scroll = True
    # Scrolled up - pause auto-scroll
    else:
      self.auto_scroll = False

  def watch_auto_scroll(self, old: bool, new: bool) -> None:
    """Watch for auto_scroll changes to update visual state.

    Args:
        old: Previous auto_scroll state.
        new: Current auto_scroll state.
    """
    if new:
      self.remove_class("paused")
    else:
      self.add_class("paused")

  def render_line(self, y: int) -> Strip:
    """Render a single line of content using the Line API.

    This method is called by Textual for each visible line on screen,
    enabling O(1) per-line rendering regardless of total content size.

    Args:
        y: The screen y-coordinate (0 is top of visible region).

    Returns:
        A Strip containing the rendered content for this line.
    """
    # Get scroll offset to map screen y to data y
    scroll_x, scroll_y = self.scroll_offset
    # Convert to int for array indexing - scroll values can be floats
    data_y = int(scroll_y) + y

    # Check if we're past the content
    if data_y >= self._total_lines or data_y < 0:
      width = self.scrollable_content_region.width if self.scrollable_content_region else _DEFAULT_WIDTH
      return Strip.blank(width, getattr(self, "rich_style", None))

    # Get the strip for this line
    strip = self._strips[data_y]

    # Handle horizontal scrolling by cropping the strip
    width = self.scrollable_content_region.width if self.scrollable_content_region else _DEFAULT_WIDTH
    return strip.crop_extend(int(scroll_x), int(scroll_x) + width, getattr(self, "rich_style", None))

  def append(self, role: str, content: str) -> str:
    """Add a new content block to the conversation.

    Args:
        role: The role of the message (user, assistant, system, tool).
        content: The text content of the message.

    Returns:
        The unique ID of the created block.
    """
    block_id = f"block-{self._block_counter}"
    self._block_counter += 1

    # Get current width for rendering
    width = self._get_content_width()

    # Check if width has changed since last render - re-render all if so
    if self._last_width != 0 and width != self._last_width:
      # Width changed, need to re-render everything at new width
      self._rerender_all_blocks()
      # Now append the new block at the new width
      width = self._get_content_width()

    # Create the block data
    block = _BlockData(block_id=block_id, role=role, content=content)
    self._blocks.append(block)

    # Render the block to strips
    block_strips = self._render_block_to_strips(block, width)
    block.line_count = len(block_strips)

    # Append to strips list
    self._strips.extend(block_strips)

    # Update cumulative heights and total lines
    self._total_lines += block.line_count
    self._cumulative_heights.append(self._total_lines)

    # Update virtual size for scrolling
    # Use the actual content region width if available, otherwise use the render width
    region = self.scrollable_content_region
    vwidth = region.width if region and region.width > 0 else width
    self.virtual_size = Size(vwidth, self._total_lines)

    # Update last width
    self._last_width = width

    # Auto-scroll to end if enabled
    if self.auto_scroll:
      self.call_after_refresh(self.scroll_end, animate=False)

    # Refresh to trigger redraw
    self.refresh()

    return block_id

  def clear(self) -> None:
    """Clear all content blocks from the conversation."""
    self._blocks.clear()
    self._strips.clear()
    self._cumulative_heights.clear()
    self._total_lines = 0
    self._block_counter = 0
    self._last_width = 0
    self.virtual_size = Size(0, 0)
    self.refresh()

  @property
  def block_count(self) -> int:
    """Return the number of content blocks in the conversation.

    Returns:
        The number of content blocks.
    """
    return len(self._blocks)

  def get_block_id_at_line(self, line: int) -> str | None:
    """Get the block ID at a specific line index.

    Uses binary search on cumulative heights for O(log n) lookup.

    Args:
        line: The line index (0-based).

    Returns:
        The block ID if found, None otherwise.
    """
    if line < 0 or line >= self._total_lines or not self._cumulative_heights:
      return None

    # Binary search to find which block this line belongs to
    block_index = bisect_right(self._cumulative_heights, line)
    if 0 <= block_index < len(self._blocks):
      return self._blocks[block_index].block_id
    return None

  def action_scroll_up(self) -> None:
    """Scroll up by one line."""
    self.scroll_to(y=self.scroll_y - 1, animate=False)

  def action_scroll_down(self) -> None:
    """Scroll down by one line."""
    self.scroll_to(y=self.scroll_y + 1, animate=False)

  def action_page_up(self) -> None:
    """Scroll up by one page."""
    self.scroll_page_up()

  def action_page_down(self) -> None:
    """Scroll down by one page."""
    self.scroll_page_down()

  def action_scroll_home(self) -> None:
    """Scroll to the start of the conversation."""
    self.scroll_home()

  def action_scroll_end(self) -> None:
    """Scroll to the end of the conversation."""
    self.scroll_end()
