"""Base classes for content plugins and input mode providers.

This module defines the abstract base classes and protocols that plugins
must implement to integrate with clitic's rendering and input handling systems.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
  from textual.app import App
  from textual.widget import Widget


class Renderable(Protocol):
  """Protocol for renderable content types.

  Any object that implements __str__ can be used as renderable content,
  allowing flexibility in content types beyond just strings.
  """

  def __str__(self) -> str:
    """Return string representation of the content."""
    ...


class Highlighter(Protocol):
  """Protocol for syntax highlighters.

  Highlighters transform plain text into syntax-highlighted strings,
  typically using Rich markup or similar formatting.
  """

  def highlight(self, text: str) -> str:
    """Apply syntax highlighting to text.

    Args:
        text: Plain text to highlight.

    Returns:
        Highlighted text with markup (e.g., Rich markup).
    """
    ...


class ContentPlugin(ABC):
  """Abstract base class for content renderers.

  Content plugins are responsible for rendering specific types of content
  in the conversation display. Each plugin declares what content types it
  can handle and provides both synchronous and asynchronous rendering.

  Attributes:
      name: Human-readable name of the plugin.
      priority: Priority for plugin ordering (higher = preferred).
  """

  @property
  @abstractmethod
  def name(self) -> str:
    """Return the human-readable name of this plugin."""
    ...

  @property
  def priority(self) -> int:
    """Return the priority for this plugin.

    Higher priority plugins are checked first when determining which
    plugin should render content. Default is 0.

    Returns:
        Priority value (higher = more preferred).
    """
    return 0

  @abstractmethod
  def can_render(self, content_type: str, content: str | Renderable) -> bool:
    """Check if this plugin can render the given content.

    Args:
        content_type: MIME type or identifier for the content.
        content: The content to potentially render.

    Returns:
        True if this plugin can render the content, False otherwise.
    """
    ...

  @abstractmethod
  def render(self, content: str | Renderable) -> "Widget":
    """Render content to a Textual Widget.

    Args:
        content: The content to render.

    Returns:
        A Textual Widget displaying the rendered content.

    Raises:
        RenderError: If rendering fails.
    """
    ...

  async def render_async(self, content: str | Renderable) -> "Widget":
    """Asynchronously render content to a Textual Widget.

    Default implementation calls the synchronous render method.
    Subclasses may override for async rendering (e.g., fetching resources).

    Args:
        content: The content to render.

    Returns:
        A Textual Widget displaying the rendered content.

    Raises:
        RenderError: If rendering fails.
    """
    return self.render(content)

  def on_register(self, app: "App") -> None:  # noqa: B027
    """Lifecycle hook called when plugin is registered with an app.

    Override this method to perform initialization that requires access
    to the app instance (e.g., loading styles, subscribing to events).

    Args:
        app: The Textual App instance.
    """
    pass

  def on_unregister(self, app: "App") -> None:  # noqa: B027
    """Lifecycle hook called when plugin is unregistered from an app.

    Override this method to perform cleanup (e.g., unsubscribing from
    events, releasing resources).

    Args:
        app: The Textual App instance.
    """
    pass


class ModeProvider(ABC):
  """Abstract base class for input mode providers.

  Mode providers detect and handle different input modes (e.g., markdown,
  code blocks, plain text). They provide syntax highlighting and transform
  input text when entering or exiting the mode.

  Attributes:
      name: Human-readable name of the mode.
      indicator: Short indicator displayed in the input bar.
      priority: Priority for mode detection (higher = preferred).
  """

  @property
  @abstractmethod
  def name(self) -> str:
    """Return the human-readable name of this mode."""
    ...

  @property
  @abstractmethod
  def indicator(self) -> str:
    """Return the short indicator for this mode.

    This is displayed in the input bar to show the current mode.
    """
    ...

  @property
  def priority(self) -> int:
    """Return the priority for this mode provider.

    Higher priority providers are checked first when detecting the
    current input mode. Default is 0.

    Returns:
        Priority value (higher = more preferred).
    """
    return 0

  @abstractmethod
  def detect(self, text: str, cursor_position: int) -> bool:
    """Detect if this mode should be active.

    Args:
        text: Current input text.
        cursor_position: Current cursor position in the text.

    Returns:
        True if this mode should be active, False otherwise.
    """
    ...

  @abstractmethod
  def get_highlighter(self) -> Highlighter | None:
    """Get the syntax highlighter for this mode.

    Returns:
        A Highlighter instance, or None if no highlighting is available.
    """
    ...

  def on_enter(self, text: str) -> str:
    """Lifecycle hook called when entering this mode.

    Override to transform text when the mode becomes active.
    Default returns text unchanged.

    Args:
        text: Current input text.

    Returns:
        Transformed text (default: unchanged).
    """
    return text

  def on_exit(self, text: str) -> str:
    """Lifecycle hook called when exiting this mode.

    Override to transform text when leaving the mode.
    Default returns text unchanged.

    Args:
        text: Current input text.

    Returns:
        Transformed text (default: unchanged).
    """
    return text
