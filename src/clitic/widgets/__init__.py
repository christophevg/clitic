"""Widgets module for clitic."""

from clitic.widgets.conversation import (
  DEFAULT_ROLE_LABELS,
  Conversation,
  RoleLabelConfig,
)
from clitic.widgets.input_bar import InputBar
from clitic.widgets.syntax_highlight import SyntaxHighlight

__all__ = ["Conversation", "InputBar", "SyntaxHighlight", "RoleLabelConfig", "DEFAULT_ROLE_LABELS"]
