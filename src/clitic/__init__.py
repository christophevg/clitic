"""
clitic - A Python package for building rich, interactive CLI applications.
"""

from clitic.exceptions import (
  CliticError,
  ConfigurationError,
  PluginError,
  RenderError,
)

__version__ = "0.1.0"

# Public API will be exported here as implementation progresses
# from clitic.core.app import App
# from clitic.widgets.input_bar import InputBar
# from clitic.widgets.conversation import Conversation

__all__ = [
  "__version__",
  # Exceptions
  "CliticError",
  "ConfigurationError",
  "PluginError",
  "RenderError",
  # "App",
  # "InputBar",
  # "Conversation",
]
