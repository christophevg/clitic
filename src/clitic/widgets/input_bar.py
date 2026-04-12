"""Multiline input widget with submit-on-Enter behavior.

This module provides the InputBar widget, a TextArea-based input component
that supports multiline text editing with Enter-to-submit behavior.
"""

from __future__ import annotations

from textual.events import Key
from textual.geometry import Size
from textual.message import Message
from textual.widgets import TextArea


class InputBar(TextArea):
  """Multiline input widget with submit-on-Enter behavior.

  InputBar extends TextArea to provide a chat-style input experience where
  pressing Enter submits the text and Shift+Enter inserts a newline.

  The widget supports auto-grow functionality, expanding its height as content
  grows up to a configurable maximum height, with internal scrolling for longer
  content.

  Attributes:
      Submit: Message class emitted when input is submitted.
      max_height: Maximum height in lines for auto-grow (default: 10).

  Example:
      ```python
      from textual.app import App, ComposeResult
      from clitic import InputBar

      class MyApp(App):
          def compose(self) -> ComposeResult:
              yield InputBar()

          def on_input_bar_submit(self, message: InputBar.Submit) -> None:
              print(f"Submitted: {message.text}")
      ```
  """

  DEFAULT_CSS = """
  InputBar {
    height: auto;
    min-height: 1;
  }
  """

  BINDINGS = [
    ("enter", "submit_input", "Submit"),
    ("shift+enter", "insert_newline", "New line"),
    ("f7", "select_all", "Select all"),
    ("ctrl+shift+a", "select_all", "Select all"),
  ]

  class Submit(Message):
    """Message emitted when input is submitted.

    Attributes:
        text: The submitted text content.
    """

    def __init__(self, text: str) -> None:
      """Initialize the Submit message.

      Args:
          text: The submitted text content.
      """
      super().__init__()
      self.text: str = text

  def __init__(
    self,
    text: str = "",
    *,
    max_height: int = 10,
    language: str | None = None,
    theme: str = "monokai",
    name: str | None = None,
    id: str | None = None,  # noqa: A002
    classes: str | None = None,
    disabled: bool = False,
    placeholder: str = "",
    read_only: bool = False,
  ) -> None:
    """Initialize the InputBar.

    Args:
        text: Initial text content (default: empty).
        max_height: Maximum height in lines for auto-grow (default: 10).
        language: Language for syntax highlighting (default: None).
        theme: Theme for syntax highlighting (default: "monokai").
        name: Name of the widget.
        id: ID of the widget.
        classes: Space-separated CSS classes.
        disabled: Whether the widget is disabled.
        placeholder: Placeholder text when empty.
        read_only: Whether the widget is read-only (default: False).
    """
    self._max_height = max_height
    super().__init__(
      text,
      language=language,
      theme=theme,
      name=name,
      id=id,
      classes=classes,
      disabled=disabled,
      placeholder=placeholder,
      read_only=read_only,
    )

  @property
  def max_height(self) -> int:
    """Maximum height in lines for auto-grow.

    Returns:
        The maximum height in lines.
    """
    return self._max_height

  @max_height.setter
  def max_height(self, value: int) -> None:
    """Set the maximum height in lines for auto-grow.

    Args:
        value: The new maximum height in lines.

    Note:
        Triggers a layout refresh to update widget height.
    """
    self._max_height = value
    self.refresh()

  def get_content_height(
    self, container: Size, viewport: Size, width: int
  ) -> int:
    """Calculate content height based on wrapped lines, clamped to max_height.

    This method is called by Textual's layout system when height is set to
    'auto' in CSS. It returns the actual height needed by the content, up to
    the configured maximum height.

    Args:
        container: Size of the container.
        viewport: Size of the viewport.
        width: Available width for content.

    Returns:
        The content height in lines, clamped to [1, max_height].
    """
    # wrapped_document.height returns visual lines (after soft wrapping)
    content_lines = self.wrapped_document.height
    return max(1, min(content_lines, self._max_height))

  def clear_text(self) -> None:
    """Clear all text from the input bar.

    Note: This is distinct from TextArea.clear() which returns EditResult.
    """
    self.text = ""

  def submit(self) -> None:
    """Submit the current text content.

    Emits a Submit message if the text is not empty, then clears the input.
    """
    current_text = self.text
    if current_text.strip():
      self.post_message(self.Submit(current_text))
      self.clear_text()

  def action_submit_input(self) -> None:
    """Handle Enter key action."""
    self.submit()

  def action_insert_newline(self) -> None:
    """Handle Shift+Enter key action - insert a newline."""
    # Insert a newline at the current cursor position
    self.insert("\n")

  def on_key(self, event: Key) -> None:
    """Handle key events for submit-on-Enter behavior.

    Enter without Shift: submit the text.
    Shift+Enter: insert newline (default TextArea behavior).

    Note: Shift+Enter detection requires terminal support for the Kitty
    keyboard protocol. Terminals without this support will treat Enter
    and Shift+Enter identically.

    Args:
        event: The key event.
    """
    # Don't process keys if widget is disabled
    if self.disabled:
      return

    # Handle Enter key (submit) vs Shift+Enter (newline)
    # When Kitty keyboard protocol is supported, shift+enter is a distinct key
    if event.key == "enter":
      # Regular Enter: submit
      event.stop()
      event.prevent_default()
      self.submit()
    elif "enter" in event.key:
      # Any other Enter variant (shift+enter, ctrl+enter, etc.)
      # Let it pass through for TextArea to handle
      return
    # When shift+enter is detected (Kitty protocol supported), let it pass through
    # to TextArea for default newline insertion
