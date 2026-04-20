"""History module for clitic.

This module provides durable command history storage with JSON Lines format.
"""

from clitic.history.manager import DEFAULT_HISTORY_FILE, HistoryEntry, HistoryManager

__all__ = [
  "HistoryEntry",
  "HistoryManager",
  "DEFAULT_HISTORY_FILE",
]
