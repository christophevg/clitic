"""Scrollable content container for conversation messages.

This module provides the Conversation widget, a scrollable container
for displaying conversation messages with different roles using virtual
rendering for optimal performance with large content.
"""

from __future__ import annotations

import uuid
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.segment import Segment as RichSegment
from rich.style import Style
from rich.text import Text
from textual._context import NoActiveAppError
from textual.events import Resize
from textual.geometry import Size
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

if TYPE_CHECKING:
  from clitic.session import SessionManager

_DEFAULT_WIDTH: int = 80


@dataclass(frozen=True)
class BlockInfo:
  """Immutable block information for public API access.

  Attributes:
      block_id: Unique identifier for this block.
      role: The role of the message (user, assistant, system, tool).
      content: The text content of the message.
      metadata: Immutable metadata for custom application data.
      timestamp: UTC-aware timestamp when the block was created.
      sequence: 0-indexed position in the conversation.
  """

  block_id: str
  role: str
  content: str
  metadata: dict[str, Any] = field(default_factory=dict)
  timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
  sequence: int = 0

  @property
  def relative_timestamp(self) -> str:
    """Human-readable relative time (e.g., '2 min ago')."""
    now = datetime.now(timezone.utc)
    delta = now - self.timestamp
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
      return "just now"
    elif total_seconds < 3600:
      minutes = total_seconds // 60
      return f"{minutes} min{'s' if minutes != 1 else ''} ago"
    elif total_seconds < 86400:
      hours = total_seconds // 3600
      return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
      days = total_seconds // 86400
      return f"{days} day{'s' if days != 1 else ''} ago"


@dataclass
class _BlockData:
  """Internal dataclass for storing content block information.

  Attributes:
      info: The immutable BlockInfo for this block.
      line_count: Number of lines this block occupies when rendered.
  """

  info: BlockInfo
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
      session_id: The unique session UUID for this conversation.

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

  Conversation.loading {
    opacity: 0.7;
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
    session_uuid: str | None = None,
    auto_scroll: bool = True,
    persistence_enabled: bool = False,
    session_dir: Path | None = None,
    max_blocks_in_memory: int = 100,
    name: str | None = None,
    id: str | None = None,  # noqa: A002
    classes: str | None = None,
    disabled: bool = False,
  ) -> None:
    """Initialize the Conversation.

    Args:
        session_uuid: Optional UUID for the session. If not provided,
            a new UUID will be generated.
        auto_scroll: Whether to automatically scroll to new content.
        persistence_enabled: Whether to enable session persistence.
        session_dir: Optional session directory for persistence.
        max_blocks_in_memory: Maximum blocks to keep in memory (0 = unlimited).
            When exceeded, oldest blocks are pruned from memory but remain
            in the session file. Default: 100.
        name: Name of the widget.
        id: ID of the widget.
        classes: Space-separated CSS classes.
        disabled: Whether the widget is disabled.
    """
    self._session_uuid: str = session_uuid or str(uuid.uuid4())
    self._sequence_counter: int = 0
    self._block_index: dict[str, int] = {}
    self._blocks: list[_BlockData] = []
    self._strips: list[Strip] = []
    self._cumulative_heights: list[int] = []  # Running total of lines per block
    self._total_lines: int = 0
    self._last_width: int = 0
    self._session_manager: SessionManager | None = None
    # Pruning-related state
    self._max_blocks_in_memory: int = max_blocks_in_memory
    self._pruned_blocks: dict[int, tuple[str, int]] = {}  # sequence -> (block_id, line_count)
    self._is_loading: bool = False
    super().__init__(name=name, id=id, classes=classes, disabled=disabled)
    self.auto_scroll = auto_scroll

    # Initialize session manager if persistence is enabled
    if persistence_enabled:
      from clitic.session import SessionManager

      self._session_manager = SessionManager(
        persistence_enabled=True,
        session_dir=session_dir,
      )
      self._session_manager.start_session(self._session_uuid)

  @property
  def session_id(self) -> str:
    """Read-only session UUID."""
    return self._session_uuid

  @property
  def max_blocks_in_memory(self) -> int:
    """Maximum blocks to keep in memory (0 = unlimited)."""
    return self._max_blocks_in_memory

  @max_blocks_in_memory.setter
  def max_blocks_in_memory(self, value: int) -> None:
    """Set the maximum blocks to keep in memory.

    Args:
        value: The maximum number of blocks (0 = unlimited).
    """
    if value < 0:
      raise ValueError("max_blocks_in_memory must be >= 0")
    self._max_blocks_in_memory = value

  @property
  def in_memory_block_count(self) -> int:
    """Number of blocks currently in memory."""
    return len(self._blocks)

  @property
  def pruned_block_count(self) -> int:
    """Number of blocks that have been pruned from memory."""
    return len(self._pruned_blocks)

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

  def _should_prune(self) -> bool:
    """Check if pruning should occur.

    Returns:
        True if pruning is needed, False otherwise.
    """
    # Pruning disabled if threshold is 0
    if self._max_blocks_in_memory == 0:
      return False
    # Pruning requires persistence
    if self._session_manager is None:
      return False
    # Check if threshold exceeded
    return len(self._blocks) > self._max_blocks_in_memory

  def _prune_oldest_blocks(self) -> None:
    """Prune oldest blocks from memory.

    Evicts blocks from memory while preserving them in the session file.
    The pruned blocks are tracked in _pruned_blocks for lazy loading.
    """
    if not self._should_prune():
      return

    # Calculate how many blocks to remove
    blocks_to_prune = len(self._blocks) - self._max_blocks_in_memory

    for _ in range(blocks_to_prune):
      if not self._blocks:
        break

      # Get the oldest block (first in list)
      oldest_block = self._blocks[0]
      sequence = oldest_block.info.sequence
      block_id = oldest_block.info.block_id
      line_count = oldest_block.line_count

      # Record in pruned_blocks before removing
      self._pruned_blocks[sequence] = (block_id, line_count)

      # Remove from blocks list
      self._blocks.pop(0)

      # Remove from strips
      self._strips = self._strips[line_count:]

      # Update cumulative heights
      lines_removed = line_count
      self._cumulative_heights = [h - lines_removed for h in self._cumulative_heights]
      self._cumulative_heights.pop(0)

      # Update total lines
      self._total_lines -= line_count
      self.virtual_size = Size(
        self.virtual_size.width,
        self._total_lines,
      )

    # Rebuild block index (indices shifted)
    self._block_index.clear()
    for i, block in enumerate(self._blocks):
      self._block_index[block.info.block_id] = i

    # Refresh display
    self.refresh()

  def _restore_pruned_blocks(self, start_sequence: int, count: int = 1) -> bool:
    """Restore pruned blocks from the session file.

    Loads blocks from the file and inserts them back into memory.

    Args:
        start_sequence: The sequence number to start restoring from.
        count: Number of blocks to restore (default: 1).

    Returns:
        True if blocks were restored, False otherwise.
    """
    # Prevent concurrent loading
    if self._is_loading:
      return False

    if self._session_manager is None:
      return False

    # Check which sequences are already in memory
    in_memory_sequences = {block.info.sequence for block in self._blocks}

    # Find sequences to restore (must be pruned AND not already in memory)
    sequences_to_restore = sorted(
      [s for s in self._pruned_blocks.keys()
       if s >= start_sequence and s not in in_memory_sequences]
    )[:count]

    if not sequences_to_restore:
      return False

    self._is_loading = True
    self.add_class("loading")
    try:
      # Load blocks from file
      end_sequence = max(sequences_to_restore)
      blocks_to_restore = self._session_manager.load_blocks_by_sequence_range(
        self._session_uuid, start_sequence, end_sequence
      )

      if not blocks_to_restore:
        return False

      # Get current render width
      width = self._get_content_width()

      # Insert blocks at the beginning
      inserted_count = 0
      for block_info in reversed(blocks_to_restore):
        # Check if this sequence is in pruned_blocks AND not already in memory
        if block_info.sequence not in self._pruned_blocks:
          continue
        if block_info.sequence in in_memory_sequences:
          continue

        # Remove from pruned_blocks
        del self._pruned_blocks[block_info.sequence]

        # Create block data
        block = _BlockData(info=block_info)

        # Render the block
        block_strips = self._render_block_to_strips(block, width)
        block.line_count = len(block_strips)

        # Insert at beginning
        self._blocks.insert(0, block)

        # Insert strips at beginning
        self._strips = block_strips + self._strips

        # Update cumulative heights
        for i in range(len(self._cumulative_heights)):
          self._cumulative_heights[i] += block.line_count
        self._cumulative_heights.insert(0, block.line_count)

        # Update total lines
        self._total_lines += block.line_count

        inserted_count += 1

      if inserted_count == 0:
        return False

      # Rebuild block index
      self._block_index.clear()
      for i, block in enumerate(self._blocks):
        self._block_index[block.info.block_id] = i

      # Update virtual size
      region = self.scrollable_content_region
      vwidth = region.width if region and region.width > 0 else width
      self.virtual_size = Size(vwidth, self._total_lines)

      # Refresh display
      self.refresh()

      return True

    finally:
      self._is_loading = False
      self.remove_class("loading")

  def _render_block_to_strips(self, block: _BlockData, width: int) -> list[Strip]:
    """Render a block's content to a list of Strips.

    Args:
        block: The block data to render.
        width: The width to render at (for text wrapping).

    Returns:
        List of Strip objects, one per line.
    """
    # Create the styled text based on role
    if block.info.role == "user":
      text = Text(f"[You] {block.info.content}", style=Style(bold=True, color="blue"))
    elif block.info.role == "assistant":
      text = Text(f"[Assistant] {block.info.content}", style=Style(bold=True, color="green"))
    elif block.info.role == "system":
      text = Text(f"[System] {block.info.content}", style=Style(bold=True, color="yellow"))
    elif block.info.role == "tool":
      text = Text(f"[Tool] {block.info.content}", style=Style(bold=True, color="magenta"))
    else:
      # Default styling for unknown roles
      text = Text(f"[{block.info.role}] {block.info.content}", style=Style(bold=True, color="grey62"))

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
    # Check if we need to restore pruned blocks when scrolling up
    # Pass the new scroll position for testing purposes
    self._check_and_restore_pruned_blocks(_scroll_y=new)

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

  def _check_and_restore_pruned_blocks(self, _scroll_y: float | None = None) -> None:
    """Check if pruned blocks should be restored based on scroll position.

    When the user scrolls near the top (within RESTORE_THRESHOLD lines),
    restore pruned blocks from the session file to provide seamless UX.

    The restored blocks are inserted at the top, and scroll position is
    adjusted to maintain the user's view.

    Args:
        _scroll_y: Optional scroll position for testing. If None, uses self.scroll_y.
    """
    RESTORE_THRESHOLD = 10  # Lines from top to trigger restoration
    current_scroll_y = _scroll_y if _scroll_y is not None else self.scroll_y

    # Don't restore if no pruned blocks
    if not self._pruned_blocks:
      return

    # Don't restore if already loading
    if self._is_loading:
      return

    # Don't restore if persistence is disabled
    if self._session_manager is None:
      return

    # Check if user is scrolling near the top
    if current_scroll_y > RESTORE_THRESHOLD:
      return

    # Find the minimum sequence in pruned blocks (oldest pruned block)
    min_sequence = min(self._pruned_blocks.keys())

    # Get the line count of the block we're about to restore
    # to adjust scroll position
    block_info = self._pruned_blocks[min_sequence]
    if isinstance(block_info, tuple):
      _, line_count = block_info
    else:
      line_count = 0

    # Restore the block
    restored = self._restore_pruned_blocks(min_sequence, count=1)

    # Adjust scroll position to maintain user's view
    # After restoration, the new block is at the top, shifting everything down
    if restored and line_count > 0:
      try:
        self.scroll_to(y=self.scroll_y + line_count, animate=False)
      except NoActiveAppError:
        # Widget not mounted - scroll adjustment will happen naturally
        # when the widget is mounted and renders
        pass

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

  def append(
    self,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
  ) -> str:
    """Add a new content block to the conversation.

    Args:
        role: The role of the message (user, assistant, system, tool).
        content: The text content of the message.
        metadata: Optional metadata dictionary for custom application data.

    Returns:
        The unique ID of the created block.
    """
    block_id = f"{self._session_uuid}-{self._sequence_counter}"
    sequence = self._sequence_counter
    self._sequence_counter += 1

    # Get current width for rendering
    width = self._get_content_width()

    # Check if width has changed since last render - re-render all if so
    if self._last_width != 0 and width != self._last_width:
      # Width changed, need to re-render everything at new width
      self._rerender_all_blocks()
      # Now append the new block at the new width
      width = self._get_content_width()

    # Create the BlockInfo and BlockData
    info = BlockInfo(
      block_id=block_id,
      role=role,
      content=content,
      metadata=metadata if metadata is not None else {},
      timestamp=datetime.now(timezone.utc),
      sequence=sequence,
    )
    block = _BlockData(info=info)
    self._blocks.append(block)

    # Save block to session file if persistence is enabled
    if self._session_manager is not None:
      self._session_manager.save_block(info)

    # Prune oldest blocks if threshold exceeded
    if self._should_prune():
      self._prune_oldest_blocks()

    # Update the block index for O(1) lookup
    self._block_index[block_id] = len(self._blocks) - 1

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
    """Clear all content blocks from the conversation.

    Note: This does NOT reset the sequence counter or session UUID.
    Block IDs will continue from the current sequence number.
    """
    self._blocks.clear()
    self._strips.clear()
    self._cumulative_heights.clear()
    self._block_index.clear()
    self._pruned_blocks.clear()
    self._total_lines = 0
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

  def get_block(self, block_id: str) -> BlockInfo | None:
    """Get block by ID. O(1) performance for in-memory blocks.

    Falls back to file lookup for pruned blocks.

    Args:
        block_id: The unique identifier of the block.

    Returns:
        The BlockInfo if found, None otherwise.
    """
    # Try in-memory first
    if block_id in self._block_index:
      index = self._block_index[block_id]
      return self._blocks[index].info

    # Fall back to file lookup for pruned blocks
    if self._session_manager is not None:
      # Extract sequence number from block_id (format: {session_uuid}-{sequence})
      try:
        sequence = int(block_id.split("-")[-1])
        # Check if this block is pruned
        if sequence in self._pruned_blocks:
          return self._session_manager.load_block_by_sequence(
            self._session_uuid, sequence
          )
      except (ValueError, IndexError):
        pass

    return None

  def get_block_at_index(self, index: int) -> BlockInfo | None:
    """Get block by sequence position. O(1) performance.

    Args:
        index: The 0-indexed position in the conversation.

    Returns:
        The BlockInfo if found, None otherwise.
    """
    if 0 <= index < len(self._blocks):
      return self._blocks[index].info
    return None

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
      return self._blocks[block_index].info.block_id
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

  @classmethod
  def resume(
    cls,
    session_id: str,
    session_dir: Path | None = None,
    max_blocks_in_memory: int = 100,
    **kwargs: Any,
  ) -> Conversation:
    """Resume a conversation from a saved session.

    Args:
        session_id: The session ID to resume.
        session_dir: Optional session directory override.
        max_blocks_in_memory: Maximum blocks to keep in memory (0 = unlimited).
            When the session has more blocks than this threshold, only the
            newest blocks are loaded into memory. Default: 100.
        **kwargs: Additional arguments passed to Conversation constructor.

    Returns:
        A Conversation instance with restored blocks.

    Raises:
        SessionError: If session file not found or invalid.
    """
    from clitic.session import SessionManager

    manager = SessionManager(session_dir=session_dir)
    blocks = manager.resume_session(session_id)

    # Create conversation with the resumed session UUID
    # Enable persistence so that get_block can load pruned blocks from file
    conversation = cls(
      session_uuid=session_id,
      persistence_enabled=True,
      session_dir=session_dir,
      max_blocks_in_memory=max_blocks_in_memory,
      **kwargs,
    )

    # Restore sequence counter from last block
    conversation._sequence_counter = max(b.sequence for b in blocks) + 1 if blocks else 0

    # Determine which blocks to keep in memory
    total_blocks = len(blocks)
    if max_blocks_in_memory > 0 and total_blocks > max_blocks_in_memory:
      # Keep only the newest blocks in memory
      blocks_to_prune = total_blocks - max_blocks_in_memory
      pruned_blocks = blocks[:blocks_to_prune]
      blocks_to_keep = blocks[blocks_to_prune:]

      # Record pruned blocks
      for block_info in pruned_blocks:
        # We don't know the line count yet, so we store 0 as placeholder
        # The actual line count will be calculated if the block is restored
        conversation._pruned_blocks[block_info.sequence] = (block_info.block_id, 0)

      # Only restore the newest blocks
      blocks = blocks_to_keep

    # Restore blocks (using internal append to avoid triggering persistence)
    for block_info in blocks:
      # Create _BlockData directly
      block = _BlockData(info=block_info)
      conversation._blocks.append(block)
      conversation._block_index[block_info.block_id] = len(conversation._blocks) - 1

    # Render all blocks for display
    if blocks:
      conversation._rerender_all_blocks()

    return conversation

  def get_session_manager(self) -> SessionManager | None:
    """Get the session manager, if persistence is enabled.

    Returns:
        The SessionManager if persistence is enabled, None otherwise.
    """
    return self._session_manager
