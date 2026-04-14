"""
clitic - A Python package for building rich, interactive CLI applications.
"""

from clitic.completion import Completion, CompletionProvider
from clitic.core import App
from clitic.exceptions import (
  CliticError,
  ConfigurationError,
  PluginError,
  RenderError,
  SessionError,
)
from clitic.plugins import (
  ContentPlugin,
  Highlighter,
  ModeProvider,
  Renderable,
)
from clitic.session import SessionInfo, SessionManager
from clitic.widgets import Conversation, InputBar
from clitic.widgets.conversation import BlockInfo

__version__ = "0.1.0"

__all__ = [
  "__version__",
  # Core
  "App",
  # Exceptions
  "CliticError",
  "ConfigurationError",
  "PluginError",
  "RenderError",
  "SessionError",
  # Plugin base classes
  "ContentPlugin",
  "Highlighter",
  "ModeProvider",
  "Renderable",
  # Completion base classes
  "Completion",
  "CompletionProvider",
  # Session management
  "SessionInfo",
  "SessionManager",
  # Widgets
  "BlockInfo",
  "Conversation",
  "InputBar",
]
