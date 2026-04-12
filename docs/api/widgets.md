# Widgets

clitic provides widgets for building interactive TUI applications.

## InputBar

The `InputBar` widget is a multiline text input with Enter-to-submit behavior and auto-grow functionality.

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

- **Multiline editing**: Full cursor movement with arrow keys, Home, End, Ctrl+arrows for word navigation
- **Text selection**: Shift+arrows for selection, Ctrl+A for select all
- **Copy/paste**: Ctrl+C, Ctrl+V, Ctrl+X for clipboard operations (terminal-dependent)
- **Enter to submit**: Press Enter to submit, Shift+Enter for newline
- **Auto-grow**: Widget height expands as content grows up to configurable maximum
- **Undo/redo**: Ctrl+Z and Ctrl+Y for undo/redo (inherited from TextArea)
- **Placeholder text**: Optional placeholder when empty
- **Read-only mode**: Optional read-only state
- **Theme support**: Light and dark themes available

### Constructor

```python
InputBar(
    text: str = "",              # Initial text content
    max_height: int = 10,       # Maximum height in lines (auto-grow)
    placeholder: str = "",      # Placeholder text when empty
    theme: str = "monokai",     # Syntax highlighting theme
    language: str | None = None,  # Language for syntax highlighting
    read_only: bool = False,    # Read-only mode
    name: str | None = None,    # Widget name
    id: str | None = None,      # Widget ID
    classes: str | None = None,  # CSS classes
    disabled: bool = False,    # Whether disabled
)
```

### Methods

| Method | Description |
|--------|-------------|
| `clear_text()` | Clear all text from the input |
| `submit()` | Submit the current text |
| `focus()` | Focus the input (inherited from TextArea) |
| `insert(text)` | Insert text at cursor position |
| `load_text(text)` | Replace all content |
| `select_all()` | Select all text |
| `action_undo()` | Undo last edit |
| `action_redo()` | Redo last undone edit |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Get or set the current text content |
| `cursor_location` | `tuple[row, col]` | Get or set cursor position |
| `selection` | `Selection` | Get current selection (start, end) |
| `selected_text` | `str` | Get currently selected text |
| `max_height` | `int` | Maximum height in lines (auto-grow limit) |
| `disabled` | `bool` | Whether the widget is disabled |
| `read_only` | `bool` | Whether the widget is read-only |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Submit text |
| Shift+Enter | Insert newline |
| Arrow keys | Move cursor |
| Ctrl+← / Ctrl+→ | Move by word |
| Home / End | Move to line start/end |
| Shift+arrows | Extend selection |
| Ctrl+A | Select all |
| Ctrl+C | Copy selection |
| Ctrl+V | Paste from clipboard |
| Ctrl+X | Cut selection |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

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
        yield InputBar(placeholder="Type a message...", max_height=5)

    def on_input_bar_submit(self, event: InputBar.Submit) -> None:
        # Add user message to the conversation
        messages = self.query_one("#messages")
        messages.mount(Static(f"You: {event.text}"))
        messages.scroll_end()
```

### Auto-Grow Behavior

InputBar automatically expands its height as content grows:

```python
# Limit to 5 lines before scrolling
input_bar = InputBar(max_height=5)

# Unlimited height (very large number)
input_bar = InputBar(max_height=1000)
```

When content exceeds `max_height`, the widget scrolls internally while maintaining its visible height.

### Selection Example

```python
from clitic import InputBar

input_bar = InputBar(text="Hello, World!")

# Select all text
input_bar.select_all()

# Get selected text
if input_bar.selected_text:
    print(f"Selected: {input_bar.selected_text}")

# Set cursor position
input_bar.cursor_location = (0, 5)  # row 0, column 5

# Programmatically set selection
from textual.widgets.text_area import Selection
input_bar.selection = Selection((0, 0), (0, 5))  # Select "Hello"
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