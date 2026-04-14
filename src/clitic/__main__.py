"""
clitic - Executable showcase application.

This module provides an interactive TUI that demonstrates all
currently implemented features of the clitic package.

Run with:
    python -m clitic
    # or
    make showcase
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widgets import Footer, Header

from clitic import App, Conversation, InputBar, __version__

if TYPE_CHECKING:
  pass


class ShowcaseApp(App):
  """Interactive showcase application for clitic."""

  CSS = """
  /* Light theme colors */
  $accent: #3B82F6;
  $accent-dark: #2563EB;
  $background: #FFFFFF;
  $background-light: #F3F4F6;
  $foreground: #1F2937;
  $foreground-muted: #6B7280;

  Conversation {
    height: 1fr;
    padding: 1;
    background: $background;
  }

  Header {
    background: $accent;
    color: $background;
  }

  Footer {
    background: $accent;
    color: $background;
  }

  InputBar {
    dock: bottom;
    height: auto;
    max-height: 10;
    margin: 1 0;
    padding: 0 1;
    width: 100%;
    background: $background-light;
  }
  """

  def __init__(self) -> None:
    """Initialize the showcase app."""
    super().__init__(title=f"clitic v{__version__} Showcase")
    self._message_count = 0

  def compose(self) -> ComposeResult:
    """Compose the app layout."""
    yield Header()
    yield Conversation(id="messages")
    # Note: Use submit_on_enter=False to make Shift+Enter submit and Enter insert newline
    yield InputBar(placeholder="Type your message here...", theme="github_light")
    yield Footer()

  def on_mount(self) -> None:
    """Focus the input bar when the app starts and add welcome message."""
    conversation = self.query_one(Conversation)

    # Demonstrate session_id access
    session_info = f"Session ID: {conversation.session_id[:8]}..."

    # Add welcome messages demonstrating metadata usage
    conversation.append(
      "system",
      f"Welcome to clitic v{__version__}!",
      metadata={"type": "welcome", "version": __version__},
    )
    conversation.append("system", session_info, metadata={"type": "info"})

    # Demonstrate block retrieval
    self.query_one(InputBar).focus()

  def on_input_bar_submit(self, event: InputBar.Submit) -> None:
    """Handle InputBar submit.

    Args:
        event: The Submit event.
    """
    self._message_count += 1

    # Add the user's message to the conversation with metadata
    conversation = self.query_one(Conversation)
    user_block_id = conversation.append(
      "user",
      event.text,
      metadata={"source": "user_input", "count": self._message_count},
    )

    # Demonstrate block retrieval by ID
    user_block = conversation.get_block(user_block_id)
    if user_block:
      # Access block info (demonstrating BlockInfo API)
      relative_time = user_block.relative_timestamp
      response_text = f"Received message #{self._message_count}!"
      response_text += f" (sent {relative_time})"

      # Also demonstrate get_block_at_index
      block_count = conversation.block_count
      if block_count > 0:
        last_block = conversation.get_block_at_index(block_count - 1)
        if last_block:
          response_text += f" [Block {last_block.sequence}]"

      conversation.append(
        "clitic",
        response_text,
        metadata={"type": "response", "user_block_id": user_block_id},
      )

    # Focus back on the input
    self.query_one(InputBar).focus()


def main() -> None:
  """Run the clitic showcase application."""
  app = ShowcaseApp()
  app.run()


if __name__ == "__main__":
  main()
