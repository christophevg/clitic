# Widgets

clitic provides widgets for building interactive TUI applications.

## InputBar

The `InputBar` widget is a multiline text input with Enter-to-submit behavior.

```python
from textual.app import App, ComposeResult
from clitic import InputBar

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield InputBar(placeholder="Type your message...")

    def on_input_bar_submit(self, event: InputBar.Submit) -> None:
        print(f"Submitted: {event.text}")
```

### Key Features

- **Multiline editing**: Full cursor movement, selection, copy/paste
- **Enter to submit**: Press Enter to submit, Shift+Enter for newline
- **Placeholder text**: Optional placeholder when empty
- **Theme support**: Light and dark themes available

### Constructor

```python
InputBar(
    text: str = "",           # Initial text content
    placeholder: str = "",    # Placeholder text when empty
    theme: str = "monokai",   # Syntax highlighting theme
    name: str | None = None,  # Widget name
    id: str | None = None,    # Widget ID
    classes: str | None = None,  # CSS classes
    disabled: bool = False,   # Whether disabled
)
```

### Methods

| Method | Description |
|--------|-------------|
| `clear_text()` | Clear all text from the input |
| `submit()` | Submit the current text |
| `focus()` | Focus the input (inherited from TextArea) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Get or set the current text content |
| `disabled` | `bool` | Whether the widget is disabled |

### Submit Message

The `InputBar.Submit` message is emitted when the user presses Enter:

```python
class Submit(Message):
    text: str  # The submitted text content
```

Handle it with:

```python
def on_input_bar_submit(self, event: InputBar.Submit) -> None:
    text = event.text
    # Process the submitted text
```

### Example: Chat Application

```python
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static
from clitic import InputBar

class ChatApp(App):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="messages")
        yield InputBar(placeholder="Type a message...", theme="github_light")

    def on_input_bar_submit(self, event: InputBar.Submit) -> None:
        # Add user message to the conversation
        messages = self.query_one("#messages")
        messages.mount(Static(f"You: {event.text}"))
        messages.scroll_end()
```

### Themes

InputBar supports Textual's TextArea themes:

| Theme | Description |
|-------|-------------|
| `monokai` | Dark theme (default) |
| `github_light` | Light theme |
| `css` | Minimal theme |
| `vscode_dark` | VS Code dark theme |
| `dracula` | Dracula theme |

### Shift+Enter Behavior

Shift+Enter inserts a newline. This requires terminal support for the [Kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/).

Supported terminals:
- Kitty
- Ghostty
- WezTerm (requires `enable_kitty_keyboard = true`)
- iTerm2
- Alacritty

If your terminal doesn't support this, Enter and Shift+Enter will behave identically.