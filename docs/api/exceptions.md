# Exceptions

clitic defines a custom exception hierarchy for clear error handling.

```{eval-rst}
.. automodule:: clitic.exceptions
   :members:
   :show-inheritance:
```

## Exception Hierarchy

```
Exception
└── CliticError (base)
    ├── PluginError
    ├── ConfigurationError
    └── RenderError
```

## Usage Examples

### Catching All clitic Errors

```python
from clitic.exceptions import CliticError

try:
    # clitic operations
    pass
except CliticError as e:
    print(f"clitic error: {e}")
```

### Plugin Errors

```python
from clitic.exceptions import PluginError

try:
    plugin.initialize()
except PluginError as e:
    print(f"Plugin {e.plugin_name} failed: {e}")
```

### Configuration Errors

```python
from clitic.exceptions import ConfigurationError

try:
    app.configure(settings)
except ConfigurationError as e:
    print(f"Invalid setting '{e.setting}': {e}")
```

### Render Errors

```python
from clitic.exceptions import RenderError

try:
    renderer.render(content)
except RenderError as e:
    print(f"Failed to render {e.content_type}: {e}")
```

## Exception Details

### CliticError

Base exception for all clitic-specific errors.

### PluginError

Raised when a plugin fails to load, initialize, or execute.

- `plugin_name`: The plugin that encountered the error
- `operation`: The operation that failed

### ConfigurationError

Raised when a configuration setting is invalid.

- `setting`: The setting name
- `expected`: Description of expected format

### RenderError

Raised when content rendering fails.

- `content_type`: The type of content
- `renderer`: The renderer that failed