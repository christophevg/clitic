"""Tests for InputBar history navigation integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from textual.events import Key

from clitic import HistoryManager, InputBar


class TestInputBarHistoryNavigation:
  """Tests for InputBar history navigation."""

  def test_history_parameter_accepted(self, tmp_path: Path) -> None:
    """InputBar should accept history parameter."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    input_bar = InputBar(history=history)
    assert input_bar._history is history

  def test_submit_adds_to_history(self, tmp_path: Path) -> None:
    """Submitting text should add to history."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    input_bar = InputBar(history=history)

    input_bar.text = "first command"
    input_bar.submit()

    assert len(history) == 1
    entry = history.get_previous()
    assert entry is not None
    assert entry.text == "first command"

  def test_submit_empty_text_not_added_to_history(self, tmp_path: Path) -> None:
    """Submitting empty text should not add to history."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    input_bar = InputBar(history=history)

    input_bar.text = "   "  # Whitespace only
    input_bar.submit()

    assert len(history) == 0

  def test_multiple_submits_add_to_history(self, tmp_path: Path) -> None:
    """Multiple submits should add multiple entries to history."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    input_bar = InputBar(history=history)

    input_bar.text = "first"
    input_bar.submit()

    input_bar.text = "second"
    input_bar.submit()

    input_bar.text = "third"
    input_bar.submit()

    assert len(history) == 3

    # Navigate history (newest first)
    entry = history.get_previous()
    assert entry is not None
    assert entry.text == "third"

    entry = history.get_previous()
    assert entry is not None
    assert entry.text == "second"

  def test_submit_resets_history_navigation(self, tmp_path: Path) -> None:
    """Submitting should reset history navigation state."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    input_bar = InputBar(history=history)

    # Add some history
    history.add("first")
    history.add("second")

    # Navigate back
    history.get_previous()

    # Submit should reset navigation
    input_bar.text = "new command"
    input_bar.submit()

    # History cursor should be at current position
    assert input_bar._history_cursor == -1
    assert input_bar._draft == ""

  def test_history_without_manager(self) -> None:
    """InputBar without history manager should work normally."""
    input_bar = InputBar()

    # Should not crash when submitting
    input_bar.text = "test"
    input_bar.submit()

    # No history to navigate
    assert input_bar._history is None


class TestInputBarHistoryKeyHandling:
  """Tests for InputBar history key handling."""

  def test_up_at_start_with_history(self, tmp_path: Path) -> None:
    """Up arrow at cursor start should navigate history."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("previous command")

    input_bar = InputBar(history=history)
    input_bar.text = ""

    # Create key event for Up arrow
    event = MagicMock(spec=Key)
    event.key = "up"

    # At start of text, should navigate history
    input_bar.on_key(event)

    assert input_bar.text == "previous command"

  def test_up_not_at_start_ignored(self, tmp_path: Path) -> None:
    """Up arrow not at cursor start should be ignored."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("previous command")

    input_bar = InputBar(history=history)
    input_bar.text = "some text"
    # Move cursor to end (not at start)
    input_bar.move_cursor(input_bar.document.end)

    # Create key event for Up arrow
    event = MagicMock(spec=Key)
    event.key = "up"
    event.stop = MagicMock()
    event.prevent_default = MagicMock()

    input_bar.on_key(event)

    # Should not change text
    assert input_bar.text == "some text"
    # Event should not be stopped
    event.stop.assert_not_called()

  def test_down_at_end_with_history(self, tmp_path: Path) -> None:
    """Down arrow at cursor end should navigate forward."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("first")
    history.add("second")

    input_bar = InputBar(history=history)
    input_bar.text = ""

    # Navigate back first
    history.get_previous()  # second
    history.get_previous()  # first

    # Navigate forward with Down
    event = MagicMock(spec=Key)
    event.key = "down"
    event.stop = MagicMock()
    event.prevent_default = MagicMock()

    # Cursor at end (empty text)
    input_bar.on_key(event)

    assert input_bar.text == "second"

  def test_down_not_at_end_ignored(self, tmp_path: Path) -> None:
    """Down arrow not at cursor end should be ignored."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("command")

    input_bar = InputBar(history=history)
    input_bar.text = "text"
    # Cursor at position 0 (start, not end)

    # Create key event for Down arrow
    event = MagicMock(spec=Key)
    event.key = "down"
    event.stop = MagicMock()
    event.prevent_default = MagicMock()

    input_bar.on_key(event)

    # Should not change text
    assert input_bar.text == "text"
    event.stop.assert_not_called()

  def test_up_down_without_history_manager(self) -> None:
    """Up/Down without history manager should do nothing."""
    input_bar = InputBar()
    input_bar.text = ""

    # Create key event for Up arrow
    event = MagicMock(spec=Key)
    event.key = "up"
    event.stop = MagicMock()
    event.prevent_default = MagicMock()

    input_bar.on_key(event)

    # Text should remain empty
    assert input_bar.text == ""
    event.stop.assert_not_called()

  def test_draft_preserved_when_navigating(self, tmp_path: Path) -> None:
    """Current text should be preserved as draft when navigating history."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("previous")

    input_bar = InputBar(history=history)
    input_bar.text = "my draft"

    # Navigate up (at start - empty text scenario, but let's simulate)
    # First, set cursor to start
    input_bar.move_cursor((0, 0))

    event = MagicMock(spec=Key)
    event.key = "up"
    event.stop = MagicMock()
    event.prevent_default = MagicMock()

    input_bar.on_key(event)

    # Draft should be saved (only on first navigation)
    # In this case, text was replaced with history
    assert input_bar._draft == "my draft"


class TestInputBarHistoryIntegration:
  """Integration tests for InputBar with HistoryManager."""

  def test_history_persists_across_submits(self, tmp_path: Path) -> None:
    """History should persist across multiple submits."""
    history_file = tmp_path / "history.jsonl"

    # First InputBar session
    history1 = HistoryManager(history_file=history_file)
    input_bar1 = InputBar(history=history1)

    input_bar1.text = "command 1"
    input_bar1.submit()
    input_bar1.text = "command 2"
    input_bar1.submit()

    # Create new history manager (simulating restart)
    history2 = HistoryManager(history_file=history_file)
    input_bar2 = InputBar(history=history2)

    # History should be preserved
    assert len(history2) == 2

    # Navigate to see commands
    entry = history2.get_previous()
    assert entry is not None
    assert entry.text == "command 2"

    entry = history2.get_previous()
    assert entry is not None
    assert entry.text == "command 1"

  def test_disabled_input_bar_ignores_keys(self, tmp_path: Path) -> None:
    """Disabled InputBar should not process history keys."""
    history = HistoryManager(history_file=tmp_path / "history.jsonl")
    history.add("command")

    input_bar = InputBar(history=history, disabled=True)

    event = MagicMock(spec=Key)
    event.key = "up"

    input_bar.on_key(event)

    # Text should remain empty (not loaded from history)
    assert input_bar.text == ""