"""Scrollable content container for conversation messages.

This module provides the Conversation widget, a scrollable container
for displaying conversation messages with different roles.
"""

from __future__ import annotations

from rich.text import Text
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Static


class _ContentBlock(Static):
  """Internal widget for a single content block.

  Each content block represents a single message in the conversation,
  with a role (user, assistant, system, tool) and content.
  """

  DEFAULT_CSS = """
  _ContentBlock {
    margin: 0 0 1 0;
    padding: 0 1;
  }
  """

  def __init__(
    self,
    role: str,
    content: str,
    block_id: str,
    *,
    name: str | None = None,
    id: str | None = None,  # noqa: A002
    classes: str | None = None,
    disabled: bool = False,
  ) -> None:
    """Initialize the content block.

    Args:
        role: The role of the message (user, assistant, system, tool).
        content: The text content of the message.
        block_id: The unique identifier for this block.
        name: Name of the widget.
        id: ID of the widget.
        classes: Space-separated CSS classes.
        disabled: Whether the widget is disabled.
    """
    super().__init__(name=name, id=id, classes=classes, disabled=disabled)
    self.role: str = role
    self.content: str = content
    self.block_id: str = block_id

  def render(self) -> Text:
    """Render the content block based on role.

    Returns:
        Rich Text object with role-appropriate styling.
    """
    if self.role == "user":
      return Text(f"[You] {self.content}", style="bold blue")
    if self.role == "assistant":
      return Text(f"[Assistant] {self.content}", style="bold green")
    if self.role == "system":
      return Text(f"[System] {self.content}", style="bold yellow")
    if self.role == "tool":
      return Text(f"[Tool] {self.content}", style="bold magenta")
    # Default styling for unknown roles
    return Text(f"[{self.role}] {self.content}", style="bold grey")


class Conversation(VerticalScroll):
  """Scrollable content container for conversation messages.

  A vertical scrolling container that manages content blocks with
  different roles (user, assistant, system, tool). Messages are
  displayed in chronological order with appropriate styling.

  Attributes:
      block_count: The number of content blocks in the conversation.

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
    self._blocks: list[_ContentBlock] = []
    self._block_counter: int = 0
    super().__init__(name=name, id=id, classes=classes, disabled=disabled)
    self.auto_scroll = auto_scroll

  def watch_scroll_y(self, old: float, new: float) -> None:
    """Watch for scroll position changes to manage auto_scroll state.

    Args:
        old: Previous scroll position.
        new: Current scroll position.
    """
    self._update_auto_scroll_from_scroll_position()

  def on_resize(self, event: object) -> None:
    """Handle resize events to update auto_scroll when all content fits.

    When window is resized to fit all content, auto-scroll should be enabled.

    Args:
        event: The resize event.
    """
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

    block = _ContentBlock(role, content, block_id)
    self._blocks.append(block)
    self.mount(block)

    if self.auto_scroll:
      self.call_after_refresh(self.scroll_end, animate=False)

    return block_id

  def clear(self) -> None:
    """Clear all content blocks from the conversation."""
    for block in self._blocks:
      block.remove()
    self._blocks.clear()

  @property
  def block_count(self) -> int:
    """Return the number of content blocks in the conversation.

    Returns:
        The number of content blocks.
    """
    return len(self._blocks)

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
