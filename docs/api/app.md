# App

The main application class for clitic.

```{eval-rst}
.. autoclass:: clitic.App
   :members:
   :show-inheritance:
```

## Usage Examples

### Basic Application

```python
from clitic import App

app = App(title="My App")

@app.on_submit
def handle_input(text: str):
    print(f"Got: {text}")

app.run()
```

### With Theme

```python
app = App(title="My App", theme_name="dark")
```

### Plugin Registration

```python
from clitic.plugins import ContentPlugin

class MyPlugin(ContentPlugin):
    # ... implementation ...

app = App()
app.register_plugin(MyPlugin())
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | `str` | Application title |
| `theme_name` | `str` | Current theme name |

## Methods

| Method | Description |
|--------|-------------|
| `register_plugin(plugin)` | Register a content plugin |
| `unregister_plugin(plugin)` | Unregister a content plugin |
| `get_plugins()` | Get list of registered plugins |
| `on_submit(handler)` | Decorator for input handlers |