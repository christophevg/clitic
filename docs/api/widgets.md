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
| Home / Ctrl+A | Move to line start |
| End / Ctrl+E | Move to line end |
| Shift+arrows | Extend selection |
| Shift+Home / Shift+End | Select to line start/end |
| **F7** or **Ctrl+Shift+A** | **Select all** |
| Ctrl+C | Copy selection |
| Ctrl+V | Paste from clipboard |
| Ctrl+X | Cut selection |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

**Note:** `Ctrl+A` moves to line start (like Home). Use **F7** or **Ctrl+Shift+A** to select all text.

**macOS Note:** The Terminal app intercepts `Cmd+A` for its own "Select All". Use **F7** or **Ctrl+Shift+A** instead. You can also configure your terminal to pass `Cmd+A` through to the application in terminal preferences. |

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

## Conversation

The `Conversation` widget is a scrollable content container for displaying conversation messages with virtual rendering for optimal performance.

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

### Key Features

- **Virtual rendering**: O(1) per-line rendering, supports 100,000+ lines
- **Auto-scroll**: Automatically scrolls to new content, pauses when user scrolls up
- **Block management**: Each message is a block with unique ID, metadata, and timestamp
- **Session tracking**: Unique session ID for persistence support
- **Block retrieval**: O(1) lookup by block ID or sequence index

### Constructor

```python
Conversation(
    session_uuid: str | None = None,  # Optional session UUID (auto-generated if None)
    auto_scroll: bool = True,          # Auto-scroll to new content
    name: str | None = None,           # Widget name
    id: str | None = None,             # Widget ID
    classes: str | None = None,        # CSS classes
    disabled: bool = False,            # Whether disabled
)
```

### Methods

| Method | Description |
|--------|-------------|
| `append(role, content, metadata=None)` | Add a block, returns block ID |
| `clear()` | Clear all blocks (sequence counter continues) |
| `get_block(block_id)` | Get block by ID, returns `BlockInfo \| None` |
| `get_block_at_index(index)` | Get block by position, returns `BlockInfo \| None` |
| `get_block_id_at_line(line)` | Get block ID at line number |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `block_count` | `int` | Number of blocks in conversation |
| `session_id` | `str` | Unique session UUID (read-only) |
| `auto_scroll` | `bool` | Whether auto-scroll is enabled |

### BlockInfo

When you call `get_block()` or `get_block_at_index()`, you receive a `BlockInfo` object:

```python
@dataclass(frozen=True)
class BlockInfo:
    block_id: str              # Unique identifier: "{session_uuid}-{sequence}"
    role: str                  # Message role (user, assistant, system, tool)
    content: str               # Text content
    metadata: dict[str, Any]   # Custom metadata (immutable)
    timestamp: datetime        # UTC-aware timestamp
    sequence: int              # 0-indexed position

    @property
    def relative_timestamp(self) -> str:
        """Human-readable time: 'just now', '2 mins ago', '1 hour ago', etc."""
```

### Example: Chat with Metadata

```python
from textual.app import App, ComposeResult
from clitic import Conversation

class ChatApp(App):
    def compose(self) -> ComposeResult:
        yield Conversation(id="chat")

    def add_message(self, role: str, text: str, metadata: dict = None) -> None:
        conversation = self.query_one(Conversation)
        block_id = conversation.append(role, text, metadata=metadata)
        
        # Retrieve block info
        block = conversation.get_block(block_id)
        print(f"Block {block.sequence}: {block.relative_timestamp}")
        
    def show_session(self) -> None:
        conversation = self.query_one(Conversation)
        print(f"Session ID: {conversation.session_id}")
```

### Example: Block Navigation

```python
conversation = self.query_one(Conversation)

# Navigate through blocks
for i in range(conversation.block_count):
    block = conversation.get_block_at_index(i)
    print(f"[{block.role}] {block.content[:50]}...")

# Get the most recent block
if conversation.block_count > 0:
    last_block = conversation.get_block_at_index(conversation.block_count - 1)
    print(f"Last message: {last_block.relative_timestamp}")
```

### Auto-Scroll Behavior

- **Enabled by default**: New content scrolls into view
- **Paused when scrolling up**: User can read history
- **Resumed when at bottom**: Auto-scroll reactivates
- **Visual indicator**: CSS class `paused` added when auto-scroll is off

```python
# Disable auto-scroll at creation
conversation = Conversation(auto_scroll=False)

# Toggle programmatically
conversation.auto_scroll = False  # Pause
conversation.auto_scroll = True   # Resume
```