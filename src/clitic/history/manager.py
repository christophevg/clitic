"""History manager for command history storage.

This module provides durable, append-only JSON Lines storage for input history,
enabling navigation through previous commands.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from clitic.exceptions import HistoryError

logger = logging.getLogger(__name__)

# Default history file location: ~/.local/share/clitic/history.jsonl
DEFAULT_HISTORY_FILE = Path.home() / ".local" / "share" / "clitic" / "history.jsonl"


@dataclass(frozen=True)
class HistoryEntry:
  """Immutable history entry representing a single input command.

  Attributes:
    text: The input text that was submitted.
    timestamp: Timezone-aware UTC datetime when the entry was created.
    metadata: Optional metadata dictionary.

  Example:
    >>> entry = HistoryEntry(
    ...     text="ls -la",
    ...     timestamp=datetime.now(timezone.utc),
    ...     metadata={"source": "cli"}
    ... )
    >>> entry.text
    'ls -la'
  """

  text: str
  timestamp: datetime
  metadata: dict[str, Any] = field(default_factory=dict)

  def __repr__(self) -> str:
    """Return a concise representation for debugging."""
    text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
    return f"HistoryEntry(text={text_preview!r}, timestamp={self.timestamp.isoformat()})"


class HistoryManager:
  """Manages command history with JSON Lines storage.

  Provides durable storage of input history with append-only writes
  for crash safety. History is loaded on initialization and can be
  navigated sequentially.

  Thread Safety:
    All public methods are thread-safe. Multiple threads can safely
    call add() and navigation methods concurrently.

  Example:
    >>> manager = HistoryManager()
    >>> manager.add("ls -la")
    >>> manager.add("cat file.txt")
    >>> len(manager)
    2
    >>> manager.get_previous()  # Navigate backward
    HistoryEntry(text='cat file.txt', ...)
    >>> manager.get_previous()  # Navigate further back
    HistoryEntry(text='ls -la', ...)
    >>> manager.reset_navigation()  # Return to current
  """

  def __init__(
    self,
    history_file: Path | None = None,
    max_entries: int = 10000,
  ) -> None:
    """Initialize the HistoryManager.

    Args:
      history_file: Optional path to history file. Defaults to
        ~/.local/share/clitic/history.jsonl
      max_entries: Maximum number of entries to keep in memory.
        Older entries are trimmed when limit is exceeded.
        Set to 0 for unlimited. Default: 10000.

    Raises:
      HistoryError: If history file exists but cannot be read.
    """
    self._history_file = history_file or DEFAULT_HISTORY_FILE
    self._max_entries = max_entries
    self._entries: list[HistoryEntry] = []
    self._cursor: int = -1  # -1 = current position (end)
    self._lock = threading.RLock()

    self._load_from_file()

  @property
  def history_file(self) -> Path:
    """Path to the history file."""
    return self._history_file

  @property
  def max_entries(self) -> int:
    """Maximum number of entries kept in memory."""
    return self._max_entries

  @property
  def entry_count(self) -> int:
    """Number of entries currently in memory."""
    with self._lock:
      return len(self._entries)

  def get_previous(self) -> HistoryEntry | None:
    """Navigate to the previous (older) history entry.

    Returns:
      The previous entry if available, None if at the oldest entry.

    Thread Safety:
      Thread-safe. Acquires lock internally.
    """
    with self._lock:
      if not self._entries or self._cursor == 0:
        return None

      if self._cursor == -1:
        # Move from current position to last entry
        self._cursor = len(self._entries) - 1
      else:
        self._cursor -= 1

      return self._entries[self._cursor]

  def get_next(self) -> HistoryEntry | None:
    """Navigate to the next (newer) history entry.

    Returns:
      The next entry if available, None if at the current position.

    Thread Safety:
      Thread-safe. Acquires lock internally.
    """
    with self._lock:
      if not self._entries or self._cursor == -1:
        return None

      self._cursor += 1
      if self._cursor >= len(self._entries):
        self._cursor = -1  # Back to current position
        return None

      return self._entries[self._cursor]

  def get_current(self) -> HistoryEntry | None:
    """Get the current entry at the cursor position.

    Returns:
      The current entry if cursor is within history, None if at
      the current position (end).
    """
    with self._lock:
      if self._cursor == -1 or not self._entries:
        return None
      return self._entries[self._cursor]

  def get_entry(self, index: int) -> HistoryEntry | None:
    """Get an entry by absolute index.

    Args:
      index: Zero-based index (0 = oldest, -1 = newest).

    Returns:
      The entry at the index, or None if out of bounds.
    """
    with self._lock:
      if not self._entries:
        return None

      # Support negative indexing
      if index < 0:
        index = len(self._entries) + index

      if 0 <= index < len(self._entries):
        return self._entries[index]
      return None

  def reset_navigation(self) -> None:
    """Reset navigation cursor to the current position.

    Call this after navigating to return to "current input" mode.
    The next get_previous() will start from the newest entry.
    """
    with self._lock:
      self._cursor = -1

  def add(
    self,
    text: str,
    metadata: dict[str, Any] | None = None,
  ) -> None:
    """Add a new entry to the history.

    Appends the entry to the history file immediately (durable write)
    and adds it to in-memory storage. Resets the navigation cursor.

    Args:
      text: The input text to store. Must not be empty.
      metadata: Optional metadata dictionary.

    Raises:
      ValueError: If text is empty or whitespace only.
      HistoryError: If write to history file fails.

    Thread Safety:
      Thread-safe. Acquires lock internally.
    """
    if not text.strip():
      raise ValueError("History entry text cannot be empty")

    entry = HistoryEntry(
      text=text,
      timestamp=datetime.now(timezone.utc),
      metadata=metadata or {},
    )

    with self._lock:
      self._append_to_file(entry)
      self._entries.append(entry)

      # Trim if exceeds max_entries
      if self._max_entries > 0 and len(self._entries) > self._max_entries:
        self._entries = self._entries[-self._max_entries :]

      # Reset cursor to end
      self._cursor = -1

  def clear(self) -> None:
    """Clear all history entries.

    Removes all entries from memory and deletes the history file.

    Raises:
      HistoryError: If file deletion fails.
    """
    with self._lock:
      self._entries.clear()
      self._cursor = -1

      if self._history_file.exists():
        try:
          self._history_file.unlink()
        except OSError as e:
          raise HistoryError(
            operation="clear",
            message=f"Failed to delete history file: {e}",
          ) from e

  def search(
    self,
    query: str,
    limit: int = 10,
  ) -> list[HistoryEntry]:
    """Search history for entries containing the query (case-insensitive).

    Args:
      query: Search query string.
      limit: Maximum number of results. Default: 10.

    Returns:
      List of matching entries, newest first.
    """
    with self._lock:
      if not query.strip():
        return []

      query_lower = query.lower()
      results: list[HistoryEntry] = []

      # Search from newest to oldest
      for entry in reversed(self._entries):
        if query_lower in entry.text.lower():
          results.append(entry)
          if len(results) >= limit:
            break

      return results

  def search_prefix(
    self,
    prefix: str,
    limit: int = 10,
  ) -> list[HistoryEntry]:
    """Search history for entries starting with the prefix (case-insensitive).

    Used for tab-completion style history search.

    Args:
      prefix: Prefix string to match.
      limit: Maximum number of results. Default: 10.

    Returns:
      List of matching entries, newest first.
    """
    with self._lock:
      if not prefix.strip():
        return []

      prefix_lower = prefix.lower()
      results: list[HistoryEntry] = []

      # Search from newest to oldest
      for entry in reversed(self._entries):
        if entry.text.lower().startswith(prefix_lower):
          results.append(entry)
          if len(results) >= limit:
            break

      return results

  def __len__(self) -> int:
    """Return the number of history entries."""
    with self._lock:
      return len(self._entries)

  def __iter__(self) -> Iterator[HistoryEntry]:
    """Iterate over entries from oldest to newest."""
    with self._lock:
      return iter(self._entries.copy())

  def __reversed__(self) -> Iterator[HistoryEntry]:
    """Iterate over entries from newest to oldest."""
    with self._lock:
      return iter(reversed(self._entries.copy()))

  def _load_from_file(self) -> None:
    """Load history from the JSONL file.

    Called during initialization. Creates parent directories if needed.
    Skips malformed lines but logs warnings.

    Raises:
      HistoryError: If file cannot be read.
    """
    if not self._history_file.exists():
      # Ensure parent directory exists
      self._history_file.parent.mkdir(parents=True, exist_ok=True)
      return

    entries: list[HistoryEntry] = []

    try:
      with open(self._history_file, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
          line = line.strip()
          if not line:
            continue

          try:
            data = json.loads(line)
            timestamp = datetime.fromisoformat(data["timestamp"])
            if timestamp.tzinfo is None:
              timestamp = timestamp.replace(tzinfo=timezone.utc)

            entry = HistoryEntry(
              text=data["text"],
              timestamp=timestamp,
              metadata=data.get("metadata", {}),
            )
            entries.append(entry)
          except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log warning but continue loading
            logger.warning(f"Skipping malformed history entry at line {line_num}: {e}")

      self._entries = entries[-self._max_entries :] if self._max_entries > 0 else entries

    except OSError as e:
      raise HistoryError(
        operation="load",
        message=f"Failed to read history file: {e}",
      ) from e

  def _append_to_file(self, entry: HistoryEntry) -> None:
    """Append an entry to the history file.

    Creates the file if it doesn't exist. Uses atomic write pattern
    with flush and fsync for durability.

    Raises:
      HistoryError: If write fails.
    """
    data = {
      "text": entry.text,
      "timestamp": entry.timestamp.isoformat(),
      "metadata": entry.metadata,
    }

    try:
      # Ensure parent directory exists
      self._history_file.parent.mkdir(parents=True, exist_ok=True)

      # Append to file with flush/fsync for durability
      with open(self._history_file, "a", encoding="utf-8") as f:
        json_line = json.dumps(data, ensure_ascii=False)
        f.write(json_line + "\n")
        f.flush()
        os.fsync(f.fileno())

    except OSError as e:
      raise HistoryError(
        operation="save",
        message=f"Failed to write history entry: {e}",
      ) from e
