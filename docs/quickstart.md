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

clitic uses a plugin system for extensible content rendering. Register plugins with:

```python
from clitic import App
from clitic.plugins import ContentPlugin

class MyPlugin(ContentPlugin):
    @property
    def name(self) -> str:
        return "my-plugin"

    def can_render(self, content_type: str, content: str):
        return content_type == "my-type"

    def render(self, content: str):
        # Return a Textual widget
        pass

app = App()
app.register_plugin(MyPlugin())
```

## Next Steps

- Read the [API Reference](api/app) for detailed documentation
- Check out the [Plugin Development](api/plugins) guide
- Explore the showcase with `python -m clitic`