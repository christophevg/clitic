# Plugin System

clitic provides a flexible plugin system for extending functionality.

## ContentPlugin

Base class for content rendering plugins. Content plugins allow you to render different content types (Markdown, code, etc.) in the Conversation widget.

```{eval-rst}
.. autoclass:: clitic.plugins.ContentPlugin
   :members:
   :show-inheritance:
```

### Built-in Plugins

#### MarkdownPlugin

clitic includes a built-in Markdown plugin that renders Markdown content using Rich's Markdown renderer:

```python
from clitic import App, Conversation
from clitic.plugins import MarkdownPlugin

app = App(title="My App")
app.register_plugin(MarkdownPlugin())

# Pass plugins to Conversation
conversation = Conversation(plugins=app.get_plugins())
conversation.append(
    "assistant",
    "# Hello\n\nThis is **bold** text.",
    metadata={"content_type": "text/markdown"}
)
```

The MarkdownPlugin handles these content types:
- `text/markdown` (standard MIME type)
- `markdown` (short form)
- `markdown/*` (any variant)

### Creating a Custom Content Plugin

```python
from clitic.plugins import ContentPlugin
from rich.text import Text
from rich.markdown import Markdown

class MyPlugin(ContentPlugin):
    @property
    def name(self) -> str:
        """Human-readable name of the plugin."""
        return "MyPlugin"

    @property
    def priority(self) -> int:
        """Priority for plugin ordering (higher = preferred)."""
        return 10

    def can_render(self, content_type: str, content: str) -> bool:
        """Check if this plugin can render the given content type."""
        return content_type == "my-type"

    def render(self, content: str):
        """Render content to a Rich renderable.

        Returns:
            A Rich renderable (e.g., Text, Markdown, Table)
        """
        # Return Rich renderable for the content
        return Text(f"[MyPlugin] {content}")

    async def render_async(self, content: str):
        """Optional async rendering (defaults to sync render)."""
        return self.render(content)

    def on_register(self, app):
        """Called when registered with app."""
        pass

    def on_unregister(self, app):
        """Called when unregistered."""
        pass
```

### Using Plugins with Conversation

```python
from clitic import App, Conversation
from clitic.plugins import MarkdownPlugin

# Create app and register plugins
app = App(title="My App")
app.register_plugin(MarkdownPlugin())

# Pass plugins to Conversation
conversation = Conversation(plugins=app.get_plugins())

# Add content with content_type metadata
conversation.append(
    "assistant",
    "# Welcome\n\n- Item 1\n- Item 2\n\n```python\nprint('Hello')\n```",
    metadata={"content_type": "text/markdown"}
)
```

## ModeProvider

Base class for input mode providers.

```{eval-rst}
.. autoclass:: clitic.plugins.ModeProvider
   :members:
   :show-inheritance:
```

### Creating a Mode Provider

```python
from clitic.plugins import ModeProvider, Highlighter

class ShellModeProvider(ModeProvider):
    @property
    def name(self) -> str:
        return "shell"

    @property
    def indicator(self) -> str:
        return "$"

    @property
    def priority(self) -> int:
        return 5

    def detect(self, text: str, cursor_position: int) -> bool:
        # Return True if this mode should activate
        return text.startswith("$ ")

    def get_highlighter(self) -> Highlighter | None:
        return ShellHighlighter()

    def on_enter(self, text: str) -> str:
        # Transform text on mode entry
        return text

    def on_exit(self, text: str) -> str:
        # Transform text on mode exit
        return text
```

## Protocols

### Renderable

```{eval-rst}
.. autoclass:: clitic.plugins.Renderable
```

### Highlighter

```{eval-rst}
.. autoclass:: clitic.plugins.Highlighter
```

## Plugin Priority

Plugins are checked in priority order (highest first). Use the `priority` property to control ordering:

| Priority | Use Case |
|----------|----------|
| 100+ | Custom overrides |
| 50-99 | Specialized renderers |
| 10-49 | Standard renderers (MarkdownPlugin uses 10) |
| 1-9 | Fallback renderers |
| 0 | Default (checked last) |

## Plugin Architecture

### Content Flow

When content is added to a Conversation with `content_type` metadata:

1. Conversation checks registered plugins for a match
2. Plugins are sorted by priority (highest first)
3. First plugin with `can_render(content_type, content) == True` is selected
4. Plugin's `render()` method converts content to Rich renderable
5. Rich renderable is converted to Strips for virtual rendering
6. If no plugin matches or rendering fails, falls back to plain text

### Error Handling

If a plugin's `render()` method raises an exception, the Conversation falls back to plain text rendering and logs the error. This ensures the application remains functional even with broken plugins.

### Performance

Plugin content is pre-rendered to Strips when added to the Conversation, maintaining O(1) virtual rendering performance. The Strips are cached and only re-rendered on resize events.