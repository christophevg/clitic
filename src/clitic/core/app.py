"""Core App class for clitic applications.

This module provides the main App class that extends Textual's App,
adding plugin management and input handling capabilities.
"""

from typing import TYPE_CHECKING, Callable

from textual.app import App as TextualApp

if TYPE_CHECKING:
  from clitic.plugins import ContentPlugin


# Type alias for submit handlers
SubmitHandler = Callable[[str], None]


class App(TextualApp):
  """Main application class for clitic.

  Extends Textual's App with plugin management and input submission handling.
  This is the foundation for building rich CLI applications with clitic.

  Args:
      title: The title of the application (displayed in title bar).
      theme_name: The theme to use for styling (default: "dark").

  Example:
      ```python
      from clitic import App

      app = App(title="My App")

      @app.on_submit
      def handle_input(text: str):
          print(f"Got: {text}")

      app.run()
      ```
  """

  def __init__(self, title: str = "clitic", theme_name: str = "dark") -> None:
    """Initialize the App.

    Args:
        title: The title of the application.
        theme_name: The theme to use (default: "dark").
    """
    super().__init__()
    self.title = title
    self._theme_name: str = theme_name
    self._plugins: list[ContentPlugin] = []
    self._submit_handlers: list[SubmitHandler] = []

  @property
  def theme_name(self) -> str:
    """Return the current theme name."""
    return self._theme_name

  def register_plugin(self, plugin: ContentPlugin) -> None:
    """Register a content plugin with the application.

    The plugin's on_register hook is called after registration,
    allowing it to initialize with access to the app instance.

    Args:
        plugin: The ContentPlugin instance to register.

    Example:
        ```python
        app = App(title="My App")
        plugin = MyCustomPlugin()
        app.register_plugin(plugin)
        ```
    """
    self._plugins.append(plugin)
    plugin.on_register(self)

  def unregister_plugin(self, plugin: ContentPlugin) -> None:
    """Unregister a content plugin from the application.

    The plugin's on_unregister hook is called before removal,
    allowing it to perform cleanup.

    Args:
        plugin: The ContentPlugin instance to unregister.
    """
    plugin.on_unregister(self)
    if plugin in self._plugins:
      self._plugins.remove(plugin)

  def on_submit(self, handler: SubmitHandler) -> SubmitHandler:
    """Decorator to register a handler for input submission.

    Multiple handlers can be registered; they will be called in
    the order they were registered.

    Args:
        handler: Function to call when input is submitted.

    Returns:
        The handler function (allows chaining decorators).

    Example:
        ```python
        app = App(title="My App")

        @app.on_submit
        def handle_input(text: str):
            print(f"Received: {text}")
        ```
    """
    self._submit_handlers.append(handler)
    return handler

  def _trigger_submit(self, text: str) -> None:
    """Trigger all registered submit handlers.

    This method is called internally when input is submitted.

    Args:
        text: The submitted input text.
    """
    for handler in self._submit_handlers:
      handler(text)

  def get_plugins(self) -> list[ContentPlugin]:
    """Return a copy of the registered plugins list.

    Returns:
        List of registered ContentPlugin instances.
    """
    return self._plugins.copy()
