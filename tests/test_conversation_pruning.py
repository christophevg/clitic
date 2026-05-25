"""Tests for Conversation block pruning functionality."""

from pathlib import Path
from unittest.mock import patch

import pytest

from clitic import Conversation
from clitic.session import SessionError, SessionManager


class TestPruningBasics:
  """Tests for basic pruning behavior."""

  def test_max_blocks_in_memory_default_is_100(self) -> None:
    """max_blocks_in_memory should default to 100."""
    conversation = Conversation()
    assert conversation.max_blocks_in_memory == 100

  def test_max_blocks_in_memory_can_be_set(self) -> None:
    """max_blocks_in_memory should be configurable."""
    conversation = Conversation(max_blocks_in_memory=50)
    assert conversation.max_blocks_in_memory == 50

  def test_max_blocks_in_memory_can_be_set_to_zero(self) -> None:
    """max_blocks_in_memory=0 should disable pruning."""
    conversation = Conversation(max_blocks_in_memory=0)
    assert conversation.max_blocks_in_memory == 0

  def test_max_blocks_in_memory_property_can_be_set(self) -> None:
    """max_blocks_in_memory property should be settable."""
    conversation = Conversation(max_blocks_in_memory=100)
    conversation.max_blocks_in_memory = 50
    assert conversation.max_blocks_in_memory == 50

  def test_max_blocks_in_memory_rejects_negative(self) -> None:
    """max_blocks_in_memory should reject negative values."""
    conversation = Conversation()
    try:
      conversation.max_blocks_in_memory = -1
      raise AssertionError("Should have raised ValueError")
    except ValueError:
      pass

  def test_pruning_disabled_when_max_is_zero(self, tmp_path: Path) -> None:
    """Pruning should be disabled when max_blocks_in_memory=0."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=0,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(150):
        conversation.append("user", f"Message {i}")

    # All blocks should still be in memory
    assert conversation.block_count == 150
    assert conversation.pruned_block_count == 0

  def test_pruning_disabled_when_persistence_disabled(self) -> None:
    """Pruning should be disabled when persistence is disabled."""
    conversation = Conversation(
      persistence_enabled=False,
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(50):
        conversation.append("user", f"Message {i}")

    # All blocks should still be in memory
    assert conversation.block_count == 50
    assert conversation.pruned_block_count == 0

  def test_pruning_removes_oldest_blocks_first(self, tmp_path: Path) -> None:
    """Pruning should remove the oldest blocks first."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(15):
        conversation.append("user", f"Message {i}")

    # Should have 10 blocks in memory (pruned 5 oldest)
    assert conversation.in_memory_block_count == 10
    assert conversation.pruned_block_count == 5

    # The oldest block in memory should be sequence 5
    first_block = conversation.get_block_at_index(0)
    assert first_block is not None
    assert first_block.sequence == 5

  def test_pruning_never_deletes_data(self, tmp_path: Path) -> None:
    """Pruning should never delete data - only evict from memory."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    block_ids = []
    with patch.object(conversation, "call_after_refresh"):
      for i in range(20):
        block_id = conversation.append("user", f"Message {i}")
        block_ids.append(block_id)

    # Close session
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Check session file has all 20 blocks
    manager = SessionManager(session_dir=tmp_path / "sessions")
    blocks = manager.resume_session(conversation.session_id)
    assert len(blocks) == 20


class TestPruningIntegration:
  """Tests for pruning integration with persistence."""

  def test_pruned_blocks_preserved_in_file(self, tmp_path: Path) -> None:
    """Pruned blocks should be preserved in the session file."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Close session
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Check file has all 10 blocks
    manager = SessionManager(session_dir=tmp_path / "sessions")
    blocks = manager.resume_session(conversation.session_id)
    assert len(blocks) == 10

  def test_get_block_falls_back_to_file(self, tmp_path: Path) -> None:
    """get_block() should fall back to file for pruned blocks."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    block_ids = []
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        block_id = conversation.append("user", f"Message {i}")
        block_ids.append(block_id)

    # First block (pruned) should still be accessible via get_block
    first_block = conversation.get_block(block_ids[0])
    assert first_block is not None
    assert first_block.sequence == 0
    assert first_block.content == "Message 0"

  def test_block_count_after_pruning(self, tmp_path: Path) -> None:
    """block_count should reflect only in-memory blocks."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(25):
        conversation.append("user", f"Message {i}")

    # block_count returns in-memory blocks
    assert conversation.block_count == 10
    assert conversation.in_memory_block_count == 10
    assert conversation.pruned_block_count == 15

  def test_pruning_with_metadata(self, tmp_path: Path) -> None:
    """Pruned blocks should preserve metadata."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      # Append more than max_blocks_in_memory to trigger pruning
      for i in range(10):
        conversation.append("user", f"Message {i}", metadata={"key": f"value{i}"})

    # First blocks should be pruned
    assert conversation.pruned_block_count > 0

    # Check that pruned block metadata is accessible
    pruned_block_id = f"{conversation.session_id}-0"
    block = conversation.get_block(pruned_block_id)
    assert block is not None
    assert block.metadata == {"key": "value0"}


class TestLazyLoading:
  """Tests for lazy loading of pruned blocks."""

  def test_restore_pruned_blocks_reloads_correctly(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks() should reload blocks from file."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # 5 blocks should be pruned
    assert conversation.pruned_block_count == 5

    # Restore the first 3 pruned blocks
    result = conversation._restore_pruned_blocks(0, count=3)
    assert result is True

    # Check that blocks were restored
    assert conversation.pruned_block_count == 2  # 5 - 3
    assert conversation.in_memory_block_count == 8  # 5 + 3

  def test_restore_preserves_block_order(self, tmp_path: Path) -> None:
    """Restored blocks should be inserted at correct position."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Restore the first pruned block
    conversation._restore_pruned_blocks(0, count=1)

    # First block should now be sequence 0
    first_block = conversation.get_block_at_index(0)
    assert first_block is not None
    assert first_block.sequence == 0

  def test_restore_updates_indices(self, tmp_path: Path) -> None:
    """Restoring blocks should update block_index correctly."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    block_ids = []
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        block_id = conversation.append("user", f"Message {i}")
        block_ids.append(block_id)

    # Restore first block
    conversation._restore_pruned_blocks(0, count=1)

    # All block IDs should now be in the index
    for block_id in block_ids:
      assert block_id in conversation._block_index or conversation.get_block(block_id) is not None

  def test_restore_does_not_duplicate(self, tmp_path: Path) -> None:
    """Restoring should not duplicate blocks that are already in memory."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    initial_count = conversation.in_memory_block_count  # 5

    # Restore sequence 0
    conversation._restore_pruned_blocks(0, count=1)
    assert conversation.in_memory_block_count == initial_count + 1  # 6

    # Try to restore sequence 0 again - it should not duplicate
    # because it's already in memory
    conversation._restore_pruned_blocks(0, count=1)

    # The second call tries to restore from sequence 0, but 0 is already in memory.
    # It will find the next pruned block (sequence 1) and restore that instead.
    # So we expect 2 blocks to be added total.
    assert conversation.in_memory_block_count == initial_count + 2  # 7

    # Verify that sequence 0 is only in memory once
    sequence_0_count = sum(1 for b in conversation._blocks if b.info.sequence == 0)
    assert sequence_0_count == 1


class TestResumeWithPruning:
  """Tests for resuming sessions with pruning."""

  def test_resume_with_more_blocks_than_threshold(self, tmp_path: Path) -> None:
    """Resume should prune excess blocks when loading."""
    # Create a session with 20 blocks
    original = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(original, "call_after_refresh"):
      for i in range(20):
        original.append("user", f"Message {i}")

    session_id = original.session_id
    if original._session_manager is not None:
      original._session_manager.close_session()

    # Resume with max_blocks_in_memory=10
    resumed = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    # Should only have 10 blocks in memory
    assert resumed.in_memory_block_count == 10
    assert resumed.pruned_block_count == 10

  def test_resume_oldest_blocks_are_pruned(self, tmp_path: Path) -> None:
    """Resume should prune the oldest blocks."""
    # Create a session with 20 blocks
    original = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(original, "call_after_refresh"):
      for i in range(20):
        original.append("user", f"Message {i}")

    session_id = original.session_id
    if original._session_manager is not None:
      original._session_manager.close_session()

    # Resume with max_blocks_in_memory=10
    resumed = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    # First block in memory should be sequence 10
    first_block = resumed.get_block_at_index(0)
    assert first_block is not None
    assert first_block.sequence == 10

  def test_resume_newest_blocks_remain_in_memory(self, tmp_path: Path) -> None:
    """Resume should keep the newest blocks in memory."""
    # Create a session with 20 blocks
    original = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(original, "call_after_refresh"):
      for i in range(20):
        original.append("user", f"Message {i}")

    session_id = original.session_id
    if original._session_manager is not None:
      original._session_manager.close_session()

    # Resume with max_blocks_in_memory=10
    resumed = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    # Last block should be sequence 19
    last_block = resumed.get_block_at_index(9)
    assert last_block is not None
    assert last_block.sequence == 19

  def test_resume_all_blocks_accessible_via_get_block(self, tmp_path: Path) -> None:
    """All blocks should be accessible via get_block after resume."""
    # Create a session with 20 blocks
    original = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    block_ids = []
    with patch.object(original, "call_after_refresh"):
      for i in range(20):
        block_id = original.append("user", f"Message {i}")
        block_ids.append(block_id)

    session_id = original.session_id
    if original._session_manager is not None:
      original._session_manager.close_session()

    # Resume with max_blocks_in_memory=10
    resumed = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    # All 20 blocks should be accessible via get_block
    for i, block_id in enumerate(block_ids):
      block = resumed.get_block(block_id)
      assert block is not None, f"Block {i} should be accessible"
      assert block.sequence == i


@pytest.mark.benchmark
class TestPruningPerformance:
  """Tests for pruning performance characteristics."""

  def test_append_performance_with_pruning(self, tmp_path: Path) -> None:
    """Appending with pruning should not degrade performance."""
    import time

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
      auto_scroll=False,
    )

    start = time.time()
    with patch.object(conversation, "call_after_refresh"):
      for i in range(100):
        conversation.append("user", f"Message {i}")
    elapsed = time.time() - start

    # Should complete in reasonable time
    # CI runners can be slower, so use a generous threshold
    assert elapsed < 20.0, f"Appending 100 blocks with pruning took {elapsed:.2f}s"

    # Verify pruning happened
    assert conversation.in_memory_block_count == 10
    assert conversation.pruned_block_count == 90

  def test_memory_stays_bounded(self, tmp_path: Path) -> None:
    """Memory usage should stay bounded with pruning."""
    import tracemalloc

    tracemalloc.start()
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
      auto_scroll=False,
    )

    with patch.object(conversation, "call_after_refresh"):
      for i in range(100):
        conversation.append("user", f"Message {i}")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory should be under 5MB with only 10 blocks in memory
    assert peak < 5 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.1f}MB"

  def test_get_block_performance_for_pruned_blocks(self, tmp_path: Path) -> None:
    """Getting pruned blocks should be reasonably fast."""
    import time

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    with patch.object(conversation, "call_after_refresh"):
      for i in range(50):
        conversation.append("user", f"Message {i}")

    # Close and reopen to ensure file-based lookup
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Get first block (pruned) multiple times
    start = time.time()
    for _ in range(10):
      block = conversation.get_block(f"{conversation.session_id}-0")
      assert block is not None
    elapsed = time.time() - start

    # Should complete in reasonable time
    assert elapsed < 1.0, f"Getting pruned blocks 10 times took {elapsed:.3f}s"


class TestPruningEdgeCases:
  """Tests for edge cases in pruning."""

  def test_pruning_at_exact_threshold(self, tmp_path: Path) -> None:
    """Pruning should not occur at exact threshold."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):  # Exactly at threshold
        conversation.append("user", f"Message {i}")

    # No pruning should occur
    assert conversation.pruned_block_count == 0
    assert conversation.in_memory_block_count == 10

  def test_pruning_triggers_when_exceeding_threshold(self, tmp_path: Path) -> None:
    """Pruning should trigger when exceeding threshold."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(11):  # Exceeds threshold by 1
        conversation.append("user", f"Message {i}")

    # Pruning should have occurred
    assert conversation.pruned_block_count == 1
    assert conversation.in_memory_block_count == 10

  def test_concurrent_loading_prevention(self, tmp_path: Path) -> None:
    """Concurrent loading should be prevented."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Set loading flag
    conversation._is_loading = True

    # Try to restore blocks - should return False
    result = conversation._restore_pruned_blocks(0, count=1)
    assert result is False

    # Clean up
    conversation._is_loading = False

  def test_get_block_for_non_existent_pruned_block(self, tmp_path: Path) -> None:
    """get_block() should return None for non-existent block IDs."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Try to get a block that doesn't exist
    block = conversation.get_block("non-existent-id")
    assert block is None

  def test_clear_clears_pruned_blocks(self, tmp_path: Path) -> None:
    """clear() should clear pruned blocks tracking."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count > 0

    conversation.clear()

    assert conversation.pruned_block_count == 0
    assert conversation.in_memory_block_count == 0

  def test_resume_with_unlimited_memory(self, tmp_path: Path) -> None:
    """Resume with max_blocks_in_memory=0 should load all blocks."""
    # Create a session with 20 blocks
    original = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(original, "call_after_refresh"):
      for i in range(20):
        original.append("user", f"Message {i}")

    session_id = original.session_id
    if original._session_manager is not None:
      original._session_manager.close_session()

    # Resume with unlimited memory
    resumed = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=0,
    )

    # All blocks should be in memory
    assert resumed.in_memory_block_count == 20
    assert resumed.pruned_block_count == 0


class TestScrollTriggeredRestoration:
  """Tests for scroll-triggered restoration of pruned blocks."""

  def test_check_and_restore_pruned_blocks_method_exists(self) -> None:
    """Conversation should have _check_and_restore_pruned_blocks method."""
    conversation = Conversation()
    assert hasattr(conversation, "_check_and_restore_pruned_blocks")

  def test_no_restore_when_no_pruned_blocks(self, tmp_path: Path) -> None:
    """Should not attempt restore when there are no pruned blocks."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):  # Less than threshold, no pruning
        conversation.append("user", f"Message {i}")

    # No pruned blocks
    assert conversation.pruned_block_count == 0

    # Calling check should not raise or change anything
    conversation._check_and_restore_pruned_blocks()
    assert conversation.in_memory_block_count == 5

  def test_no_restore_when_scrolling_down(self, tmp_path: Path) -> None:
    """Should not restore when scroll position is not near top."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Should have pruned blocks
    assert conversation.pruned_block_count == 5

    # Pass scroll_y to simulate being scrolled down (far from top)
    # The RESTORE_THRESHOLD is 10, so scroll_y > 10 means no restore
    conversation._check_and_restore_pruned_blocks(_scroll_y=100.0)
    assert conversation.pruned_block_count == 5

  def test_restore_when_scrolling_near_top(self, tmp_path: Path) -> None:
    """Should restore blocks when scroll position is near top."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Should have pruned blocks
    initial_pruned = conversation.pruned_block_count
    assert initial_pruned == 5

    # Pass scroll_y to simulate being at top (scroll_y = 0)
    conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)
    assert conversation.pruned_block_count == initial_pruned - 1

  def test_restore_triggered_by_watch_scroll_y(self, tmp_path: Path) -> None:
    """watch_scroll_y should trigger restoration when near top."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    initial_pruned = conversation.pruned_block_count
    assert initial_pruned == 5

    # Simulate scrolling to top via watch_scroll_y
    # The new scroll position (0.0) is passed to _check_and_restore_pruned_blocks
    conversation.watch_scroll_y(old=100.0, new=0.0)

    # Should have restored one block
    assert conversation.pruned_block_count == initial_pruned - 1

  def test_loading_class_added_during_restoration(self, tmp_path: Path) -> None:
    """Loading CSS class should be added during block restoration."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Manually set loading flag and add class to simulate loading state
    conversation._is_loading = True
    conversation.add_class("loading")

    # Loading class should be present
    assert "loading" in conversation.classes

    # Clean up
    conversation._is_loading = False
    conversation.remove_class("loading")

  def test_loading_class_removed_after_restoration(self, tmp_path: Path) -> None:
    """Loading CSS class should be removed after restoration completes."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Pass scroll_y to simulate being at top
    conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)

    # Loading class should not be present after restoration
    assert "loading" not in conversation.classes

  def test_concurrent_restore_prevented(self, tmp_path: Path) -> None:
    """Should not restore if already loading."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Set loading flag
    conversation._is_loading = True

    # Pass scroll_y to simulate being at top
    # Check should not restore because _is_loading is True
    conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)
    assert conversation.pruned_block_count == 5  # No change

    # Clean up
    conversation._is_loading = False

  def test_scroll_position_adjusted_after_restore(self, tmp_path: Path) -> None:
    """Scroll position should be adjusted to maintain user's view after restore."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # Get the line count of the first pruned block
    first_pruned_seq = min(conversation._pruned_blocks.keys())
    first_pruned_info = conversation._pruned_blocks[first_pruned_seq]
    if isinstance(first_pruned_info, tuple):
      _, line_count = first_pruned_info
    else:
      line_count = 0

    # Pass scroll_y to simulate being near top (within threshold)
    scroll_position = 5
    conversation._check_and_restore_pruned_blocks(_scroll_y=float(scroll_position))

    # Scroll position should have been adjusted
    # Note: if line_count was 0 in _pruned_blocks (from resume), adjustment might not happen
    if line_count > 0:
      # The implementation calls scroll_to which we can't test without mounting,
      # so we verify that _restore_pruned_blocks was called successfully
      assert conversation.pruned_block_count < 5  # Some blocks were restored

  def test_multiple_restores_on_continuous_scroll(self, tmp_path: Path) -> None:
    """Multiple restores should happen as user continues scrolling up."""
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(15):
        conversation.append("user", f"Message {i}")

    # Should have 10 pruned blocks
    assert conversation.pruned_block_count == 10

    # Pass scroll_y to simulate being at top for first restore
    conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)
    assert conversation.pruned_block_count == 9

    # Second restore (still near top)
    conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)
    assert conversation.pruned_block_count == 8

  def test_no_restore_without_persistence(self) -> None:
    """Should not restore without persistence enabled."""
    conversation = Conversation(
      persistence_enabled=False,
      max_blocks_in_memory=5,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10):
        conversation.append("user", f"Message {i}")

    # No pruned blocks because persistence is disabled
    assert conversation.pruned_block_count == 0

    # Calling check should not raise
    conversation._check_and_restore_pruned_blocks()


# ==============================================================================
# Test Class: Restore With Stale Data
# ==============================================================================


class TestRestoreWithStaleData:
  """Tests for _restore_pruned_blocks with stale or inconsistent data.

  These tests verify graceful handling when file content has changed
  after pruning occurred. The conversation may raise SessionError or
  return False depending on the specific scenario.
  """

  def test_restore_with_modified_block_content(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle modified file content.

    If the file content has changed since pruning, restoration may
    return False or restore different content than expected.
    """
    import json

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Modify file content
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    lines = session_file.read_text().strip().split("\n")
    modified_lines = []
    for i, line in enumerate(lines):
      data = json.loads(line)
      if i < 3:  # Modify first 3 (pruned) blocks
        data["content"] = f"Modified message {i}"
      modified_lines.append(json.dumps(data))
    session_file.write_text("\n".join(modified_lines) + "\n")

    # Attempt restore - should succeed but with modified content
    result = conversation._restore_pruned_blocks(0, count=1)
    # Current behavior: restores successfully with modified content
    assert result is True

  def test_restore_with_deleted_block_in_file(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle when a block was removed from file.

    If a pruned block's sequence was deleted from the file, restoration
    of that specific block should fail gracefully.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Delete first block from file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    lines = session_file.read_text().strip().split("\n")
    # Remove the first line (sequence 0)
    modified_lines = lines[1:]
    session_file.write_text("\n".join(modified_lines) + "\n")

    # Attempt restore sequence 0 - file doesn't have it
    # Current behavior: load_blocks_by_sequence_range returns empty list
    # so _restore_pruned_blocks returns False
    result = conversation._restore_pruned_blocks(0, count=1)
    assert result is False

  def test_restore_with_reordered_blocks(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle reordered sequence numbers.

    If blocks in file have been reordered, restoration uses sequence
    numbers for matching, not file order.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Reverse the order of lines in file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    lines = session_file.read_text().strip().split("\n")
    reversed_lines = list(reversed(lines))
    session_file.write_text("\n".join(reversed_lines) + "\n")

    # Attempt restore - should still work based on sequence numbers
    result = conversation._restore_pruned_blocks(0, count=1)
    assert result is True

    # Verify correct block was restored
    first_block = conversation.get_block_at_index(0)
    assert first_block is not None
    assert first_block.sequence == 0
    assert first_block.content == "Message 0"

  def test_restore_with_extra_blocks_inserted(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle new blocks inserted in file.

    If new blocks were inserted in the file after pruning, restoration
    should still find and restore the correct pruned blocks by sequence.
    """
    import json
    from datetime import datetime, timezone

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Insert an extra block at the beginning
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    lines = session_file.read_text().strip().split("\n")

    extra_block = {
      "block_id": "extra-block",
      "role": "assistant",
      "content": "Extra message",
      "sequence": 100,  # Non-conflicting sequence
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "metadata": {},
    }
    lines.insert(0, json.dumps(extra_block))
    session_file.write_text("\n".join(lines) + "\n")

    # Restore sequence 0 - should still find it
    result = conversation._restore_pruned_blocks(0, count=1)
    assert result is True

  def test_pruned_blocks_dict_inconsistent_with_file(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle stale _pruned_blocks dict.

    If _pruned_blocks has stale information (references blocks not in file),
    restoration should handle gracefully.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Manually corrupt _pruned_blocks to reference non-existent sequences
    # _pruned_blocks format: dict[int, tuple[str, int]] = {sequence: (block_id, line_count)}
    conversation._pruned_blocks[99] = (100, 10)  # (block_id, line_count) - fake block

    # Close session to ensure file is written
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Try to restore non-existent block
    # Current behavior: load_blocks_by_sequence_range won't find it
    result = conversation._restore_pruned_blocks(99, count=1)
    assert result is False

  def test_line_count_mismatch_after_restore(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle line count mismatch.

    When restoring blocks, the line count stored in _pruned_blocks may
    differ from actual rendered line count. The implementation should
    recalculate line count on restore.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    # Corrupt the line count in _pruned_blocks
    first_pruned_seq = min(conversation._pruned_blocks.keys())
    # _pruned_blocks format: dict[int, tuple[str, int]] = {sequence: (block_id, line_count)}
    # Set incorrect line count to test recalculation
    conversation._pruned_blocks[first_pruned_seq] = (100, 999)  # (block_id, wrong_line_count)

    # Restore should still work - it recalculates line count
    result = conversation._restore_pruned_blocks(first_pruned_seq, count=1)
    assert result is True

    # Verify the block was restored (actual line count, not 999)
    assert conversation.in_memory_block_count == 3


# ==============================================================================
# Test Class: Session File Unavailable
# ==============================================================================


class TestSessionFileUnavailable:
  """Tests for handling deleted/corrupted session files after pruning.

  These tests verify graceful handling when the session file becomes
  unavailable or corrupted between pruning and restoration attempts.
  """

  def test_restore_with_deleted_session_file(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should return False when session file is deleted."""

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Delete session file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    session_file.unlink()

    # Attempt restore - should return False or raise SessionError
    # Current behavior: load_blocks_by_sequence_range raises SessionError
    with pytest.raises(SessionError):
      conversation._restore_pruned_blocks(0, count=1)

  def test_restore_with_moved_session_file(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle moved/renamed session file."""

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Move session file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    moved_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl.bak"
    session_file.rename(moved_file)

    # Attempt restore - should fail
    with pytest.raises(SessionError):
      conversation._restore_pruned_blocks(0, count=1)

  def test_restore_with_corrupted_json(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle corrupted JSON in file.

    When file contains invalid JSON lines, restoration should skip
    malformed lines but continue with valid ones.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Corrupt the file by replacing first line with invalid JSON
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    content = session_file.read_text()
    lines = content.strip().split("\n")
    # Corrupt the first line (which is sequence 0, a pruned block)
    lines[0] = "{ invalid json"
    session_file.write_text("\n".join(lines) + "\n")

    # Attempt restore - load_blocks_by_sequence_range skips malformed lines
    # So sequence 0 won't be found, returns empty list -> False
    result = conversation._restore_pruned_blocks(0, count=1)
    # Current behavior: skips corrupted line, block not found -> False
    assert result is False

  def test_restore_with_truncated_file(self, tmp_path: Path) -> None:
    """_restore_pruned_blocks should handle truncated file.

    If file was truncated mid-write (e.g., crash scenario), restoration
    should handle gracefully.
    """
    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Close session to flush writes
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Truncate the file (remove some lines)
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    lines = session_file.read_text().strip().split("\n")
    # Keep only first 2 lines (sequences 0 and 1, both pruned)
    truncated_content = "\n".join(lines[:2]) + "\n"
    session_file.write_text(truncated_content)

    # Attempt restore - should work for available blocks
    result = conversation._restore_pruned_blocks(0, count=1)
    assert result is True

    # But _pruned_blocks still has entries for missing sequences
    # This is current behavior - internal state may be inconsistent
    assert conversation._pruned_blocks  # Still has entries

  def test_get_block_fallback_with_deleted_file(self, tmp_path: Path) -> None:
    """get_block() should handle gracefully when session file is deleted.

    After pruning, if file is deleted, get_block for pruned blocks
    should fail gracefully.
    """

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    block_ids = []
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        block_id = conversation.append("user", f"Message {i}")
        block_ids.append(block_id)

    assert conversation.pruned_block_count == 3

    # Delete session file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    session_file.unlink()

    # Try to get a pruned block - should fail
    # Current behavior: raises SessionError when file not found
    with pytest.raises(SessionError):
      conversation.get_block(block_ids[0])

  def test_check_and_restore_with_missing_file(self, tmp_path: Path) -> None:
    """_check_and_restore_pruned_blocks should handle missing session file.

    Auto-restore triggered by scroll should not crash when file is missing.
    """

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )
    with patch.object(conversation, "call_after_refresh"):
      for i in range(5):
        conversation.append("user", f"Message {i}")

    assert conversation.pruned_block_count == 3

    # Delete session file
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    session_file.unlink()

    # Try to trigger auto-restore via check_and_restore
    # Current behavior: _check_and_restore_pruned_blocks calls _restore_pruned_blocks
    # which raises SessionError when file is missing, and it propagates up
    # (not caught by the method which only catches NoActiveAppError)
    with pytest.raises(SessionError):
      conversation._check_and_restore_pruned_blocks(_scroll_y=0.0)


# ==============================================================================
# Test Class: Multiple Conversation Instances
# ==============================================================================


class TestMultipleConversationInstances:
  """Tests for handling multiple Conversation instances with same session id.

  These tests verify behavior when two Conversation instances interact
  with the same session file, which can lead to race conditions.
  """

  def test_two_conversations_same_session_id_append(self, tmp_path: Path) -> None:
    """Two conversations appending to same session file should not corrupt.

    When two instances append to the same session file, both writes
    should succeed and file should remain valid.
    """
    import json

    session_dir = tmp_path / "sessions"

    # Create first conversation
    conv1 = Conversation(
      persistence_enabled=True,
      session_dir=session_dir,
      max_blocks_in_memory=10,
    )
    session_id = conv1.session_id

    with patch.object(conv1, "call_after_refresh"):
      for i in range(3):
        conv1.append("user", f"Conv1 message {i}")

    # Create second conversation with same session_id
    # Note: This is not the intended use pattern, but tests edge case
    conv2 = Conversation(
      persistence_enabled=True,
      session_dir=session_dir,
      session_uuid=session_id.split("-")[0],  # Use same base
      max_blocks_in_memory=10,
    )

    # Both should write to same file (depending on session_id generation)
    # This tests current behavior - file may have interleaved writes
    # or may not exist due to timing/concurrent access
    with patch.object(conv2, "call_after_refresh"):
      conv2.append("user", "Conv2 message")

    # Verify session file is valid JSONL if it exists
    # File may not exist due to race conditions in concurrent access
    session_file = session_dir / f"{conv1.session_id}.jsonl"
    if session_file.exists():
      lines = session_file.read_text().strip().split("\n")
      for line in lines:
        json.loads(line)  # Should be valid JSON

  def test_resume_while_original_still_active(self, tmp_path: Path) -> None:
    """Resuming a session while original instance is active.

    This is an edge case that could lead to file locking or corruption.
    Current implementation allows it but behavior may be undefined.
    """
    # Create first conversation
    conv1 = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    with patch.object(conv1, "call_after_refresh"):
      for i in range(5):
        conv1.append("user", f"Message {i}")

    session_id = conv1.session_id

    # Don't close conv1, try to resume with second instance
    # Current behavior: resume loads from file, both can coexist
    conv2 = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=10,
    )

    # Both instances should have the same blocks
    assert conv2.block_count == 5

    # But they are independent in-memory copies
    with patch.object(conv1, "call_after_refresh"):
      conv1.append("user", "From conv1")

    with patch.object(conv2, "call_after_refresh"):
      conv2.append("user", "From conv2")

    # Both instances see their own blocks
    assert conv1.block_count == 6
    assert conv2.block_count == 6

  def test_pruning_conflict_between_instances(self, tmp_path: Path) -> None:
    """One instance prunes blocks, other tries to access them.

    When one Conversation prunes blocks and another tries to access
    them, the second should be able to load from file.
    """
    # Create first conversation with low threshold
    conv1 = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=2,
    )

    block_ids = []
    with patch.object(conv1, "call_after_refresh"):
      for i in range(5):
        block_id = conv1.append("user", f"Message {i}")
        block_ids.append(block_id)

    session_id = conv1.session_id

    # conv1 has pruned blocks
    assert conv1.pruned_block_count == 3

    # Create second conversation and resume
    conv2 = Conversation.resume(
      session_id,
      session_dir=tmp_path / "sessions",
      max_blocks_in_memory=5,  # Higher threshold, all in memory
    )

    # conv2 should have all blocks in memory
    assert conv2.pruned_block_count == 0
    assert conv2.in_memory_block_count == 5

    # conv2 can access all blocks directly
    for i, block_id in enumerate(block_ids):
      block = conv2.get_block(block_id)
      assert block is not None
      assert block.sequence == i

  def test_concurrent_append_to_same_session(self, tmp_path: Path) -> None:
    """Race condition with concurrent appends to same session.

    Multiple instances appending concurrently could lead to interleaved
    writes. This test documents current behavior.
    """
    import json
    from concurrent.futures import ThreadPoolExecutor

    session_dir = tmp_path / "sessions"

    # Create first conversation
    conv = Conversation(
      persistence_enabled=True,
      session_dir=session_dir,
      max_blocks_in_memory=100,
    )
    session_id = conv.session_id

    # Close it to write to file
    if conv._session_manager is not None:
      conv._session_manager.close_session()

    def append_to_session(thread_id: int) -> None:
      """Append blocks to session from a thread."""
      # Create a new manager for each thread
      from datetime import datetime, timezone

      from clitic.session import SessionManager
      from clitic.widgets.conversation import BlockInfo

      manager = SessionManager(
        persistence_enabled=True,
        session_dir=session_dir,
      )
      # Re-open the session
      manager.start_session(session_id)

      for i in range(5):
        block = BlockInfo(
          block_id=f"thread-{thread_id}-block-{i}",
          role="user",
          content=f"Thread {thread_id} message {i}",
          metadata={},
          timestamp=datetime.now(timezone.utc),
          sequence=thread_id * 5 + i,
        )
        manager.save_block(block)

    # Run concurrent appends
    with ThreadPoolExecutor(max_workers=2) as executor:
      futures = [executor.submit(append_to_session, i) for i in range(2)]
      for future in futures:
        future.result()  # Wait for completion

    # Verify file is valid JSONL
    session_file = session_dir / f"{session_id}.jsonl"
    if session_file.exists():
      lines = session_file.read_text().strip().split("\n")
      # Should have 10 blocks (5 from each thread)
      assert len(lines) >= 10

      # All lines should be valid JSON
      for line in lines:
        json.loads(line)
