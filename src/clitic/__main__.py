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
    """Focus the input bar when the app starts."""
    self.query_one(InputBar).focus()

  def on_input_bar_submit(self, event: InputBar.Submit) -> None:
    """Handle InputBar submit.

    Args:
        event: The Submit event.
    """
    self._message_count += 1

    # Add the user's message to the conversation
    conversation = self.query_one(Conversation)
    conversation.append("user", event.text)

    # Add a system response
    conversation.append("clitic", f"Received message #{self._message_count}!")

    # Focus back on the input
    self.query_one(InputBar).focus()


def main() -> None:
  """Run the clitic showcase application."""
  app = ShowcaseApp()
  app.run()


if __name__ == "__main__":
  main()
