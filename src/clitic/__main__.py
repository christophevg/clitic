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

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Label, Static

from clitic import App, InputBar, __version__

if TYPE_CHECKING:
  pass


class MessageDisplay(Static):
  """A widget to display a single message."""

  def __init__(self, role: str, content: str) -> None:
    """Initialize the message display.

    Args:
        role: The role of the message (user, system, etc.)
        content: The message content.
    """
    super().__init__()
    self.role = role
    self.content = content

  def render(self) -> Text:
    """Render the message."""
    if self.role == "user":
      return Text(f"[You] {self.content}", style="bold blue")
    return Text(f"[{self.role}] {self.content}", style="bold grey")


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

  VerticalScroll {
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

  MessageDisplay {
    margin: 0 0 1 0;
  }

  .welcome {
    text-align: center;
    text-style: bold;
    color: $accent;
    margin: 2;
  }

  .help-text {
    text-align: center;
    color: $foreground-muted;
    margin: 1;
  }
  """

  def __init__(self) -> None:
    """Initialize the showcase app."""
    super().__init__(title=f"clitic v{__version__} Showcase")
    self._message_count = 0

  def compose(self) -> ComposeResult:
    """Compose the app layout."""
    yield Header()
    yield VerticalScroll(
      Label("Welcome to clitic!", classes="welcome"),
      Label("Type a message and press Enter to submit", classes="help-text"),
      Label("Press Shift+Enter for newline (if your terminal supports it)", classes="help-text"),
      Label("Press Ctrl+C or Ctrl+Q to quit", classes="help-text"),
      id="messages",
    )
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
    messages_container = self.query_one("#messages", VerticalScroll)
    message_display = MessageDisplay("user", event.text)
    messages_container.mount(message_display)

    # Add a system response
    response = MessageDisplay("clitic", f"Received message #{self._message_count}!")
    messages_container.mount(response)

    # Scroll to the bottom
    messages_container.scroll_end(animate=False)

    # Focus back on the input
    self.query_one(InputBar).focus()


def main() -> None:
  """Run the clitic showcase application."""
  app = ShowcaseApp()
  app.run()


if __name__ == "__main__":
  main()
