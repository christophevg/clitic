# Quick Start

This guide will help you get started with clitic in under 5 minutes.

## Basic Application

The simplest clitic application creates an App instance and runs it:

```python
from clitic import App

app = App(title="My CLI Tool")

@app.on_submit
def handle_input(text: str):
    print(f"Received: {text}")

if __name__ == "__main__":
    app.run()
```

## Key Concepts

### App

The `App` class is the main entry point for clitic applications. It extends Textual's App with:

- Plugin management via `register_plugin()`
- Input handling via the `@app.on_submit` decorator
- Theme support (dark/light)

```python
from clitic import App

# Create app with custom settings
app = App(title="My App", theme_name="dark")

# Access app properties
print(f"Title: {app.title}")
print(f"Theme: {app.theme_name}")
```

### Event Handling

Register input handlers using the `@app.on_submit` decorator:

```python
@app.on_submit
def handle_input(text: str):
    # Process the submitted text
    pass

# Multiple handlers are called in registration order
@app.on_submit
def log_input(text: str):
    print(f"Logged: {text}")
```

### Plugins

clitic uses a plugin system for extensible content rendering. The built-in `MarkdownPlugin` enables rich content display:

```python
from textual.app import ComposeResult
from clitic import App, Conversation, InputBar
from clitic.plugins import MarkdownPlugin

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Conversation(id="messages")
        yield InputBar(placeholder="Type your message...")

    def on_mount(self) -> None:
        # Register Markdown plugin
        self.register_plugin(MarkdownPlugin())

        conversation = self.query_one(Conversation)

        # Pass plugins to Conversation
        conversation._plugins = self.get_plugins()

        # Add markdown content
        conversation.append(
            "assistant",
            "# Welcome\n\nThis is **bold** text.\n\n```python\nprint('Hello')\n```",
            metadata={"content_type": "text/markdown"}
        )

MyApp().run()
```

### Content Types

Add content to Conversation with optional `content_type` metadata:

```python
# Plain text (default)
conversation.append("user", "Hello!")

# Markdown content
conversation.append(
    "assistant",
    "# Header\n\n- Item 1\n- Item 2",
    metadata={"content_type": "text/markdown"}
)

# Custom content types (with custom plugins)
conversation.append(
    "system",
    '{"status": "ok"}',
    metadata={"content_type": "application/json"}
)
```

### Creating Custom Plugins

Extend `ContentPlugin` to create custom content renderers:

```python
from clitic.plugins import ContentPlugin
from rich.text import Text

class CodePlugin(ContentPlugin):
    @property
    def name(self) -> str:
        return "Code"

    @property
    def priority(self) -> int:
        return 5

    def can_render(self, content_type: str, content: str) -> bool:
        return content_type.startswith("code/")

    def render(self, content: str):
        # Return Rich renderable
        return Text(content, style="cyan")

# Register with app
app.register_plugin(CodePlugin())
```

## Next Steps

- Read the [API Reference](api/app) for detailed documentation
- Check out the [Plugin Development](api/plugins) guide
- Explore the showcase with `python -m clitic`