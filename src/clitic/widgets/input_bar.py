"""Multiline input widget with configurable submit behavior.

This module provides the InputBar widget, a TextArea-based input component
that supports multiline text editing with configurable Enter/Shift+Enter
behavior for submission.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.events import Key
from textual.geometry import Size
from textual.message import Message
from textual.widgets import TextArea

if TYPE_CHECKING:
    from clitic.history import HistoryManager


class InputBar(TextArea):
    """Multiline input widget with configurable submit behavior.

    InputBar extends TextArea to provide a chat-style input experience where
    Enter or Shift+Enter can be configured to submit text.

    The widget supports auto-grow functionality, expanding its height as content
    grows up to a configurable maximum height, with internal scrolling for longer
    content.

    History navigation is supported via Up/Down arrow keys when the cursor is
    at the start (Up) or end (Down) of the text. This requires a HistoryManager
    instance to be provided.

    Attributes:
        Submit: Message class emitted when input is submitted.
        max_height: Maximum height in lines for auto-grow (default: 10).
        submit_on_enter: Whether Enter key submits (default: True).
        history: Optional HistoryManager for command history.

    Example:
        ```python
        from textual.app import App, ComposeResult
        from clitic import InputBar, HistoryManager

        class MyApp(App):
            def compose(self) -> ComposeResult:
                yield InputBar(history=HistoryManager())

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
        submit_on_enter: bool = True,
        max_height: int = 10,
        language: str | None = None,
        theme: str = "monokai",
        history: HistoryManager | None = None,
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
            submit_on_enter: If True (default), Enter submits and Shift+Enter
                inserts newline. If False, Shift+Enter submits and Enter inserts
                newline.
            max_height: Maximum height in lines for auto-grow (default: 10).
            language: Language for syntax highlighting (default: None).
            theme: Theme for syntax highlighting (default: "monokai").
            history: Optional HistoryManager for command history navigation.
                When provided, Up arrow at cursor start navigates to previous
                history entry, and Down arrow at cursor end navigates to next.
            name: Name of the widget.
            id: ID of the widget.
            classes: Space-separated CSS classes.
            disabled: Whether the widget is disabled.
            placeholder: Placeholder text when empty.
            read_only: Whether the widget is read-only (default: False).
        """
        self._submit_on_enter = submit_on_enter
        self._max_height = max_height
        self._history = history
        self._history_cursor: int = -1  # -1 = current position (not browsing)
        self._draft: str = ""  # Saved text when navigating history
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

    @property
    def submit_on_enter(self) -> bool:
        """Whether Enter key submits (True) or Shift+Enter submits (False).

        Returns:
            True if Enter submits (default), False if Shift+Enter submits.
        """
        return self._submit_on_enter

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
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
        If a HistoryManager is configured, the submitted text is added to history.
        """
        current_text = self.text
        if current_text.strip():
            # Add to history if configured
            if self._history is not None:
                self._history.add(current_text)
            self.post_message(self.Submit(current_text))
            self.clear_text()
            # Reset history navigation state
            self._history_cursor = -1
            self._draft = ""

    def action_submit_input(self) -> None:
        """Handle Enter key action."""
        self.submit()

    def action_insert_newline(self) -> None:
        """Handle Shift+Enter key action - insert a newline."""
        # Insert a newline at the current cursor position
        self.insert("\n")

    def on_key(self, event: Key) -> None:
        """Handle key events for configurable submit behavior.

        When submit_on_enter=True (default):
          Enter without Shift: submit the text.
          Shift+Enter: insert newline (default TextArea behavior).

        When submit_on_enter=False:
          Shift+Enter: submit the text.
          Enter: insert newline (default TextArea behavior).

        History navigation (when HistoryManager is configured):
          Up arrow at cursor start: navigate to previous history entry.
          Down arrow at cursor end: navigate to next history entry.

        Note: Shift+Enter detection requires terminal support for the Kitty
        keyboard protocol. Terminals without this support will treat Enter
        and Shift+Enter identically.

        Args:
            event: The key event.
        """
        # Don't process keys if widget is disabled
        if self.disabled:
            return

        # Handle history navigation
        if self._history is not None:
            if event.key == "up":
                if self.cursor_at_start_of_text:
                    self._navigate_history_backward()
                    event.stop()
                    event.prevent_default()
                    return
            elif event.key == "down":
                if self.cursor_at_end_of_text:
                    self._navigate_history_forward()
                    event.stop()
                    event.prevent_default()
                    return

        # Handle Enter key variants
        if "enter" in event.key:
            is_shift_enter = "shift" in event.key or event.key == "shift+enter"
            is_plain_enter = event.key == "enter"

            if self._submit_on_enter:
                # Enter submits, Shift+Enter inserts newline
                if is_plain_enter:
                    event.stop()
                    event.prevent_default()
                    self.submit()
                    return
                # shift+enter passes through for newline insertion by TextArea
            else:
                # Shift+Enter submits, Enter inserts newline
                if is_shift_enter:
                    event.stop()
                    event.prevent_default()
                    self.submit()
                    return
                # plain enter passes through for newline insertion by TextArea

    def _navigate_history_backward(self) -> None:
        """Navigate to the previous (older) history entry.

        Called when Up arrow is pressed at cursor start.
        Saves current text as draft before navigating.
        """
        if self._history is None:
            return

        # Save current text as draft on first navigation
        if self._history_cursor == -1:
            self._draft = self.text

        entry = self._history.get_previous()
        if entry is not None:
            self.text = entry.text
            # Move cursor to end after loading history entry
            self.move_cursor(self.document.end)

    def _navigate_history_forward(self) -> None:
        """Navigate to the next (newer) history entry.

        Called when Down arrow is pressed at cursor end.
        Restores draft when reaching the current position.
        """
        if self._history is None:
            return

        entry = self._history.get_next()
        if entry is not None:
            self.text = entry.text
            # Move cursor to end after loading history entry
            self.move_cursor(self.document.end)
        else:
            # Reached current position, restore draft
            self.text = self._draft
            self._history.reset_navigation()
            self._history_cursor = -1
            # Move cursor to end
            self.move_cursor(self.document.end)
