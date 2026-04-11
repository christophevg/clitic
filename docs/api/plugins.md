# Plugin System

clitic provides a flexible plugin system for extending functionality.

## ContentPlugin

Base class for content rendering plugins.

```{eval-rst}
.. autoclass:: clitic.plugins.ContentPlugin
   :members:
   :show-inheritance:
```

### Creating a Content Plugin

```python
from clitic.plugins import ContentPlugin
from textual.widget import Widget

class MarkdownPlugin(ContentPlugin):
    @property
    def name(self) -> str:
        return "markdown"

    @property
    def priority(self) -> int:
        return 10

    def can_render(self, content_type: str, content: str) -> bool:
        return content_type == "markdown"

    def render(self, content: str) -> Widget:
        # Return a Textual widget with rendered content
        from textual.widgets import Static
        return Static(content)

    async def render_async(self, content: str) -> Widget:
        # Optional async rendering
        return self.render(content)

    def on_register(self, app):
        # Called when registered with app
        pass

    def on_unregister(self, app):
        # Called when unregistered
        pass
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
| 10-49 | Standard renderers |
| 1-9 | Fallback renderers |
| 0 | Default (checked last) |