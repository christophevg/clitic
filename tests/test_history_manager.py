"""Tests for HistoryManager and HistoryEntry.

This module tests the history storage functionality including:
- HistoryEntry dataclass immutability
- HistoryManager initialization and loading
- Navigation methods
- Persistence with JSON Lines format
- Search functionality
- Thread safety
"""

from __future__ import annotations

import json
import threading
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from clitic import HistoryEntry, HistoryError, HistoryManager


class TestHistoryEntry:
  """Tests for HistoryEntry dataclass."""

  def test_frozen_dataclass(self) -> None:
    """HistoryEntry should be immutable."""
    entry = HistoryEntry(
      text="test", timestamp=datetime.now(timezone.utc)
    )
    with pytest.raises(FrozenInstanceError):
      entry.text = "modified"  # type: ignore[misc]

  def test_metadata_default(self) -> None:
    """HistoryEntry should have empty metadata by default."""
    entry = HistoryEntry(
      text="test", timestamp=datetime.now(timezone.utc)
    )
    assert entry.metadata == {}

  def test_repr_truncation(self) -> None:
    """__repr__ should truncate long text."""
    long_text = "x" * 100
    entry = HistoryEntry(text=long_text, timestamp=datetime.now(timezone.utc))
    assert "..." in repr(entry)

  def test_repr_short_text(self) -> None:
    """__repr__ should not truncate short text."""
    entry = HistoryEntry(
      text="short", timestamp=datetime.now(timezone.utc)
    )
    assert "short" in repr(entry)
    assert "..." not in repr(entry)


class TestHistoryManagerInstantiation:
  """Tests for HistoryManager initialization."""

  def test_manager_can_be_instantiated(self, tmp_path: Path) -> None:
    """HistoryManager should be instantiable."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    assert manager is not None

  def test_default_history_file(self) -> None:
    """HistoryManager should use default file path."""
    manager = HistoryManager()
    expected = Path.home() / ".local" / "share" / "clitic" / "history.jsonl"
    assert manager.history_file == expected

  def test_custom_history_file(self, tmp_path: Path) -> None:
    """HistoryManager should use custom file path."""
    custom_path = tmp_path / "custom_history.jsonl"
    manager = HistoryManager(history_file=custom_path)
    assert manager.history_file == custom_path

  def test_max_entries_parameter(self, tmp_path: Path) -> None:
    """HistoryManager should accept max_entries parameter."""
    manager = HistoryManager(
      history_file=tmp_path / "history.jsonl", max_entries=100
    )
    assert manager.max_entries == 100

  def test_loads_existing_history(self, tmp_path: Path) -> None:
    """HistoryManager should load existing history from file."""
    history_file = tmp_path / "history.jsonl"
    # Write existing history
    history_file.write_text(
      '{"text": "first", "timestamp": "2026-01-01T00:00:00+00:00", "metadata": {}}\n'
      '{"text": "second", "timestamp": "2026-01-01T00:01:00+00:00", "metadata": {}}\n'
    )

    manager = HistoryManager(history_file=history_file)
    assert len(manager) == 2

  def test_creates_parent_directory(self, tmp_path: Path) -> None:
    """HistoryManager should create parent directory if needed."""
    nested_path = tmp_path / "nested" / "dir" / "history.jsonl"
    HistoryManager(history_file=nested_path)
    assert nested_path.parent.exists()

  def test_empty_manager_has_zero_entries(self, tmp_path: Path) -> None:
    """Empty HistoryManager should have zero entries."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    assert len(manager) == 0
    assert manager.entry_count == 0


class TestHistoryManagerAdd:
  """Tests for add() method."""

  def test_add_stores_entry(self, tmp_path: Path) -> None:
    """Adding entries should store them correctly."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    assert len(manager) == 2

  def test_add_writes_to_file(self, tmp_path: Path) -> None:
    """Adding entries should write to file."""
    history_file = tmp_path / "history.jsonl"
    manager = HistoryManager(history_file=history_file)
    manager.add("test command")

    content = history_file.read_text()
    assert "test command" in content

  def test_add_rejects_empty_text(self, tmp_path: Path) -> None:
    """add() should reject empty text."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    with pytest.raises(ValueError, match="cannot be empty"):
      manager.add("")

  def test_add_rejects_whitespace_only(self, tmp_path: Path) -> None:
    """add() should reject whitespace-only text."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    with pytest.raises(ValueError, match="cannot be empty"):
      manager.add("   ")

  def test_add_with_metadata(self, tmp_path: Path) -> None:
    """add() should store metadata."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("test", metadata={"source": "cli"})

    entry = manager.get_previous()
    assert entry is not None
    assert entry.metadata == {"source": "cli"}

  def test_add_resets_navigation(self, tmp_path: Path) -> None:
    """add() should reset navigation cursor."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")

    # Navigate back
    manager.get_previous()

    # Add new entry should reset cursor
    manager.add("third")
    assert manager.get_current() is None

  def test_add_trims_to_max_entries(self, tmp_path: Path) -> None:
    """add() should trim entries to max_entries."""
    manager = HistoryManager(
      history_file=tmp_path / "history.jsonl", max_entries=3
    )
    manager.add("first")
    manager.add("second")
    manager.add("third")
    manager.add("fourth")

    assert len(manager) == 3
    # Newest entries should be kept
    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == "fourth"

  def test_add_no_deduplication(self, tmp_path: Path) -> None:
    """add() should store consecutive duplicate commands."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("duplicate")
    manager.add("duplicate")
    manager.add("duplicate")

    assert len(manager) == 3


class TestHistoryManagerNavigation:
  """Tests for navigation methods."""

  def test_get_previous_returns_newest_first(self, tmp_path: Path) -> None:
    """get_previous() should return newest entry first."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    manager.add("third")

    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == "third"

  def test_get_previous_returns_none_at_oldest(self, tmp_path: Path) -> None:
    """get_previous() should return None at oldest entry."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("only")

    manager.get_previous()  # At oldest
    entry = manager.get_previous()
    assert entry is None

  def test_get_next_returns_none_at_current(self, tmp_path: Path) -> None:
    """get_next() should return None at current position."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("test")

    # At current position (-1)
    entry = manager.get_next()
    assert entry is None

  def test_get_current_returns_none_at_current(self, tmp_path: Path) -> None:
    """get_current() should return None at current position."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("test")

    # At current position
    assert manager.get_current() is None

  def test_navigation_sequence(self, tmp_path: Path) -> None:
    """Navigation should work in correct sequence."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    manager.add("third")

    # Navigate backward
    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == "third"

    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == "second"

    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == "first"

    # At oldest, should return None
    assert manager.get_previous() is None

    # Navigate forward
    entry = manager.get_next()
    assert entry is not None
    assert entry.text == "second"

  def test_reset_navigation(self, tmp_path: Path) -> None:
    """reset_navigation() should return to current position."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")

    manager.get_previous()
    manager.reset_navigation()
    assert manager.get_current() is None

  def test_navigation_empty_history(self, tmp_path: Path) -> None:
    """Navigation should return None for empty history."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")

    assert manager.get_previous() is None
    assert manager.get_next() is None
    assert manager.get_current() is None

  def test_get_entry_by_index(self, tmp_path: Path) -> None:
    """get_entry() should return entry by absolute index."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    manager.add("third")

    # Positive index
    entry = manager.get_entry(0)
    assert entry is not None
    assert entry.text == "first"

    # Negative index
    entry = manager.get_entry(-1)
    assert entry is not None
    assert entry.text == "third"

    # Out of bounds
    assert manager.get_entry(10) is None


class TestHistoryManagerPersistence:
  """Tests for file persistence."""

  def test_loads_from_file_on_init(self, tmp_path: Path) -> None:
    """HistoryManager should load from file on initialization."""
    history_file = tmp_path / "history.jsonl"

    # Create history file manually
    history_file.write_text(
      '{"text": "loaded", "timestamp": "2026-01-01T00:00:00+00:00", "metadata": {}}\n'
    )

    manager = HistoryManager(history_file=history_file)
    assert len(manager) == 1

  def test_persists_across_instances(self, tmp_path: Path) -> None:
    """History should persist across instances."""
    history_file = tmp_path / "history.jsonl"

    manager1 = HistoryManager(history_file=history_file)
    manager1.add("first")
    manager1.add("second")

    manager2 = HistoryManager(history_file=history_file)
    assert len(manager2) == 2
    entry = manager2.get_previous()
    assert entry is not None
    assert entry.text == "second"

  def test_handles_malformed_lines(self, tmp_path: Path) -> None:
    """HistoryManager should skip malformed lines."""
    history_file = tmp_path / "history.jsonl"

    # Write valid and invalid lines
    history_file.write_text(
      '{"text": "valid", "timestamp": "2026-01-01T00:00:00+00:00", "metadata": {}}\n'
      "not valid json\n"
      '{"text": "also valid", "timestamp": "2026-01-01T00:01:00+00:00", "metadata": {}}\n'
    )

    manager = HistoryManager(history_file=history_file)
    assert len(manager) == 2

  def test_handles_missing_timestamp(self, tmp_path: Path) -> None:
    """HistoryManager should skip entries without timestamp."""
    history_file = tmp_path / "history.jsonl"

    history_file.write_text(
      '{"text": "no timestamp", "metadata": {}}\n'
      '{"text": "valid", "timestamp": "2026-01-01T00:00:00+00:00", "metadata": {}}\n'
    )

    manager = HistoryManager(history_file=history_file)
    assert len(manager) == 1

  def test_file_format(self, tmp_path: Path) -> None:
    """File should be valid JSON Lines format."""
    history_file = tmp_path / "history.jsonl"
    manager = HistoryManager(history_file=history_file)
    manager.add("test command")

    content = history_file.read_text()
    lines = content.strip().split("\n")

    # Should be valid JSON
    data = json.loads(lines[0])
    assert data["text"] == "test command"
    assert "timestamp" in data
    assert "metadata" in data

  def test_clear_removes_file(self, tmp_path: Path) -> None:
    """clear() should remove history file."""
    history_file = tmp_path / "history.jsonl"
    manager = HistoryManager(history_file=history_file)
    manager.add("test")

    manager.clear()

    assert len(manager) == 0
    assert not history_file.exists()


class TestHistoryManagerSearch:
  """Tests for search methods."""

  def test_search_finds_matches(self, tmp_path: Path) -> None:
    """search() should find matching entries."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("ls -la")
    manager.add("cat file.txt")
    manager.add("ls -lh")

    results = manager.search("ls")
    assert len(results) == 2
    assert all("ls" in e.text for e in results)

  def test_search_case_insensitive(self, tmp_path: Path) -> None:
    """search() should be case-insensitive."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("LS -LA")

    results = manager.search("ls")
    assert len(results) == 1

  def test_search_respects_limit(self, tmp_path: Path) -> None:
    """search() should respect limit parameter."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    for i in range(20):
      manager.add(f"test-{i}")

    results = manager.search("test", limit=5)
    assert len(results) == 5

  def test_search_prefix_matches(self, tmp_path: Path) -> None:
    """search_prefix() should match entry start."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("ls -la")
    manager.add("ls -lh")
    manager.add("cat file.txt")

    results = manager.search_prefix("ls")
    assert len(results) == 2
    assert all(e.text.startswith("ls") for e in results)

  def test_search_empty_query_returns_empty(self, tmp_path: Path) -> None:
    """search() should return empty for empty query."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("test")

    results = manager.search("")
    assert results == []

  def test_search_returns_newest_first(self, tmp_path: Path) -> None:
    """search() should return newest matches first."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("test one")
    manager.add("test two")
    manager.add("test three")

    results = manager.search("test")
    assert len(results) == 3
    assert results[0].text == "test three"


class TestHistoryManagerThreadSafety:
  """Tests for concurrent access."""

  def test_concurrent_adds(self, tmp_path: Path) -> None:
    """Concurrent adds should be safe."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    errors: list[Exception] = []

    def add_entries(thread_id: int) -> None:
      for i in range(100):
        try:
          manager.add(f"entry-{thread_id}-{i}")
        except Exception as e:
          errors.append(e)

    threads = [
      threading.Thread(target=add_entries, args=(i,)) for i in range(10)
    ]
    for t in threads:
      t.start()
    for t in threads:
      t.join()

    assert not errors
    assert len(manager) == 1000

  def test_concurrent_navigation_and_add(self, tmp_path: Path) -> None:
    """Concurrent navigation and add should be safe."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    errors: list[Exception] = []

    def navigate() -> None:
      for _ in range(100):
        try:
          manager.get_previous()
          manager.get_next()
          manager.reset_navigation()
        except Exception as e:
          errors.append(e)

    def add_entries() -> None:
      for i in range(100):
        try:
          manager.add(f"entry-{i}")
        except Exception as e:
          errors.append(e)

    threads = [
      threading.Thread(target=navigate),
      threading.Thread(target=add_entries),
    ]
    for t in threads:
      t.start()
    for t in threads:
      t.join()

    assert not errors


class TestHistoryManagerIteration:
  """Tests for iteration methods."""

  def test_iter_oldest_to_newest(self, tmp_path: Path) -> None:
    """__iter__ should iterate from oldest to newest."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    manager.add("third")

    entries = list(manager)
    assert len(entries) == 3
    assert entries[0].text == "first"
    assert entries[2].text == "third"

  def test_reversed_newest_to_oldest(self, tmp_path: Path) -> None:
    """__reversed__ should iterate from newest to oldest."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("first")
    manager.add("second")
    manager.add("third")

    entries = list(reversed(manager))
    assert len(entries) == 3
    assert entries[0].text == "third"
    assert entries[2].text == "first"


class TestHistoryError:
  """Tests for HistoryError exception."""

  def test_is_clitic_error(self) -> None:
    """HistoryError should be a CliticError."""
    from clitic import CliticError

    assert issubclass(HistoryError, CliticError)

  def test_str_formatting(self) -> None:
    """HistoryError __str__ should format correctly."""
    error = HistoryError(operation="save", message="Disk full")
    assert "save" in str(error)
    assert "Disk full" in str(error)

  def test_repr_formatting(self) -> None:
    """HistoryError __repr__ should format correctly."""
    error = HistoryError(operation="load", message="File not found")
    repr_str = repr(error)
    assert "HistoryError" in repr_str
    assert "load" in repr_str

  def test_operation_only(self) -> None:
    """HistoryError should work with operation only."""
    error = HistoryError(operation="clear")
    assert "clear" in str(error)


class TestHistoryManagerEdgeCases:
  """Tests for edge cases."""

  def test_timestamp_timezone_handling(self, tmp_path: Path) -> None:
    """HistoryManager should handle timezone-naive timestamps."""
    history_file = tmp_path / "history.jsonl"

    # Write entry with naive timestamp
    history_file.write_text(
      '{"text": "naive", "timestamp": "2026-01-01T00:00:00", "metadata": {}}\n'
    )

    manager = HistoryManager(history_file=history_file)
    assert len(manager) == 1

    entry = manager.get_entry(0)
    assert entry is not None
    assert entry.timestamp.tzinfo is not None

  def test_max_entries_zero_unlimited(self, tmp_path: Path) -> None:
    """max_entries=0 should allow unlimited entries."""
    manager = HistoryManager(
      history_file=tmp_path / "history.jsonl", max_entries=0
    )
    for i in range(100):
      manager.add(f"entry-{i}")

    assert len(manager) == 100

  def test_unicode_content(self, tmp_path: Path) -> None:
    """HistoryManager should handle Unicode content."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    manager.add("日本語テスト")
    manager.add("émoji 🎉")

    assert len(manager) == 2
    entry = manager.get_previous()
    assert entry is not None
    assert "🎉" in entry.text

  def test_multiline_text(self, tmp_path: Path) -> None:
    """HistoryManager should handle multiline text."""
    manager = HistoryManager(history_file=tmp_path / "history.jsonl")
    multiline = "line1\nline2\nline3"
    manager.add(multiline)

    entry = manager.get_previous()
    assert entry is not None
    assert entry.text == multiline