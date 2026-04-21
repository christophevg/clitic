"""Plugins module for clitic.

This module provides the base classes for content renderers and input
mode providers, along with built-in plugins for common content types.
"""

from clitic.plugins.base import (
  ContentPlugin,
  Highlighter,
  ModeProvider,
  Renderable,
)
from clitic.plugins.markdown import MarkdownPlugin

__all__ = [
  "ContentPlugin",
  "Highlighter",
  "MarkdownPlugin",
  "ModeProvider",
  "Renderable",
]