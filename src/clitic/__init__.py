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
)
from clitic.plugins import (
  ContentPlugin,
  Highlighter,
  ModeProvider,
  Renderable,
)

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
  # Plugin base classes
  "ContentPlugin",
  "Highlighter",
  "ModeProvider",
  "Renderable",
  # Completion base classes
  "Completion",
  "CompletionProvider",
]
