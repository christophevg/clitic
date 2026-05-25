"""
clitic - A Python package for building rich, interactive CLI applications.
"""

from clitic.completion import Completion, CompletionProvider
from clitic.core import App
from clitic.exceptions import (
  CliticError,
  ConfigurationError,
  HistoryError,
  PluginError,
  RenderError,
  SessionError,
)
from clitic.history import DEFAULT_HISTORY_FILE, HistoryEntry, HistoryManager
from clitic.plugins import (
  CodePlugin,
  ContentPlugin,
  Highlighter,
  MarkdownPlugin,
  ModeProvider,
  Renderable,
)
from clitic.session import SessionInfo, SessionManager
from clitic.widgets import Conversation, InputBar, SyntaxHighlight
from clitic.widgets.conversation import BlockInfo

__version__ = "0.1.0"

__all__ = [
  "__version__",
  # Core
  "App",
  # Exceptions
  "CliticError",
  "ConfigurationError",
  "HistoryError",
  "PluginError",
  "RenderError",
  "SessionError",
  # History management
  "DEFAULT_HISTORY_FILE",
  "HistoryEntry",
  "HistoryManager",
  # Plugin base classes
  "CodePlugin",
  "ContentPlugin",
  "Highlighter",
  "MarkdownPlugin",
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
  "SyntaxHighlight",
]
