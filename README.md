# clitic

A Python package for building rich, interactive CLI applications.

## Overview

clitic provides reusable components for building terminal user interfaces (TUIs) with:
- Multiline input with syntax highlighting and history
- Scrollable content areas with pluggable renderers
- Markdown, diff, and terminal content rendering
- CSS-like styling and theming
- Responsive layouts

Built on Textual for the TUI framework, with Rich for rendering.

## Installation

```bash
pip install clitic
```

## Quick Start

```python
from clitic import App, InputBar, Conversation

app = App(title="My CLI Tool")

@app.on_submit
def handle_input(text: str):
    conversation.append("user", text)
    # Process input...

conversation = Conversation()
input_bar = InputBar(history_file="~/.my_cli_history.jsonl")

app.run()
```

## Features

- **InputBar**: Multiline input with history navigation, completion, and mode switching
- **Conversation**: Scrollable content container with expandable blocks
- **Tree/Table**: Collapsible tree and table widgets
- **Plugins**: Markdown, diff, and terminal content renderers
- **Theming**: Dark and light themes with customization
- **Responsive**: Layouts adapt to terminal width

## License

MIT License