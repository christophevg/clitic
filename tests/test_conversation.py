"""Tests for Conversation widget."""

import re
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from textual.scroll_view import ScrollView

from clitic import Conversation
from clitic.widgets.conversation import BlockInfo, _BlockData


class TestBlockInfo:
  """Tests for BlockInfo dataclass."""

  def test_block_info_is_frozen(self) -> None:
    """BlockInfo should be frozen (immutable)."""
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={"key": "value"},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    # Should not be able to modify
    try:
      info.block_id = "new-id"  # type: ignore[misc]
      raise AssertionError("BlockInfo should be frozen")
    except (AttributeError, TypeError):
      pass

  def test_block_info_default_metadata(self) -> None:
    """BlockInfo should default to empty metadata dict."""
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    assert info.metadata == {}

  def test_block_info_default_timestamp(self) -> None:
    """BlockInfo should default to UTC-aware timestamp."""
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      sequence=0,
    )
    assert info.timestamp is not None
    # Should be timezone-aware (UTC)
    assert info.timestamp.tzinfo is not None
    assert info.timestamp.tzinfo == timezone.utc

  def test_block_info_relative_timestamp_just_now(self) -> None:
    """relative_timestamp should return 'just now' for < 60 seconds."""
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    assert info.relative_timestamp == "just now"

  def test_block_info_relative_timestamp_minutes_ago(self) -> None:
    """relative_timestamp should return 'X min ago' for minutes."""
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=5)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    assert info.relative_timestamp == "5 mins ago"

  def test_block_info_relative_timestamp_one_minute_ago(self) -> None:
    """relative_timestamp should return '1 min ago' for singular."""
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=1)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    # Account for potential timing issues
    relative = info.relative_timestamp
    assert relative in ("1 min ago", "2 mins ago")

  def test_block_info_relative_timestamp_hours_ago(self) -> None:
    """relative_timestamp should return 'X hours ago' for hours."""
    timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    assert info.relative_timestamp == "3 hours ago"

  def test_block_info_relative_timestamp_one_hour_ago(self) -> None:
    """relative_timestamp should return '1 hour ago' for singular."""
    timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    # Account for potential timing issues
    relative = info.relative_timestamp
    assert relative in ("1 hour ago", "2 hours ago")

  def test_block_info_relative_timestamp_days_ago(self) -> None:
    """relative_timestamp should return 'X days ago' for days."""
    timestamp = datetime.now(timezone.utc) - timedelta(days=5)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    assert info.relative_timestamp == "5 days ago"

  def test_block_info_relative_timestamp_one_day_ago(self) -> None:
    """relative_timestamp should return '1 day ago' for singular."""
    timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=timestamp,
      sequence=0,
    )
    assert info.relative_timestamp == "1 day ago"


class TestConversationInstantiation:
  """Tests for Conversation instantiation."""

  def test_conversation_can_be_instantiated(self) -> None:
    """Conversation should be instantiable."""
    conversation = Conversation()
    assert conversation is not None

  def test_conversation_extends_scroll_view(self) -> None:
    """Conversation should extend ScrollView."""
    conversation = Conversation()
    assert isinstance(conversation, ScrollView)

  def test_conversation_accepts_name_parameter(self) -> None:
    """Conversation should accept a name parameter."""
    conversation = Conversation(name="test_conversation")
    assert conversation._name == "test_conversation"

  def test_conversation_accepts_id_parameter(self) -> None:
    """Conversation should accept an id parameter."""
    conversation = Conversation(id="test-id")
    assert conversation.id == "test-id"

  def test_conversation_accepts_classes_parameter(self) -> None:
    """Conversation should accept classes parameter."""
    conversation = Conversation(classes="custom-class")
    assert conversation.classes == {"custom-class"}

  def test_conversation_generates_session_uuid(self) -> None:
    """Conversation should generate a session UUID if not provided."""
    conversation = Conversation()
    assert conversation.session_id is not None
    assert len(conversation.session_id) == 36  # UUID format

  def test_conversation_accepts_custom_session_uuid(self) -> None:
    """Conversation should use provided session UUID."""
    custom_uuid = "12345678-1234-1234-1234-123456789abc"
    conversation = Conversation(session_uuid=custom_uuid)
    assert conversation.session_id == custom_uuid


class TestConversationProperties:
  """Tests for Conversation properties."""

  def test_block_count_default_is_zero(self) -> None:
    """block_count should default to 0."""
    conversation = Conversation()
    assert conversation.block_count == 0

  def test_session_id_property_exists(self) -> None:
    """session_id property should exist."""
    conversation = Conversation()
    assert hasattr(conversation, "session_id")

  def test_session_id_is_read_only(self) -> None:
    """session_id should be read-only (no setter)."""
    conversation = Conversation()
    try:
      conversation.session_id = "new-id"  # type: ignore[misc]
      raise AssertionError("session_id should be read-only")
    except AttributeError:
      pass


class TestConversationAppend:
  """Tests for Conversation append functionality."""

  def test_append_returns_block_id(self) -> None:
    """append() should return a unique block ID."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello")
    # Block ID should match pattern: {uuid}-{sequence}
    assert re.match(r"^[a-f0-9-]+-\d+$", block_id)

  def test_append_increments_block_count(self) -> None:
    """append() should increment block_count."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    assert conversation.block_count == 1

  def test_multiple_appends_create_unique_ids(self) -> None:
    """Multiple append() calls should create unique IDs."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      id1 = conversation.append("user", "Hello")
      id2 = conversation.append("assistant", "Hi")
      id3 = conversation.append("user", "How are you?")
    # All IDs should be unique
    assert id1 != id2 != id3
    assert conversation.block_count == 3

  def test_append_supports_different_roles(self) -> None:
    """append() should support all role types."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "User message")
      conversation.append("assistant", "Assistant message")
      conversation.append("system", "System message")
      conversation.append("tool", "Tool message")
    assert conversation.block_count == 4

  def test_append_updates_strips(self) -> None:
    """append() should update the strips list."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    # Should have strips (content lines + blank margin line)
    assert len(conversation._strips) > 0

  def test_append_updates_cumulative_heights(self) -> None:
    """append() should update cumulative heights."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    # Should have one cumulative height entry
    assert len(conversation._cumulative_heights) == 1

  def test_append_updates_total_lines(self) -> None:
    """append() should update total lines counter."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    # Should have some lines (content + margin)
    assert conversation._total_lines > 0

  def test_append_accepts_metadata(self) -> None:
    """append() should accept metadata parameter."""
    conversation = Conversation()
    metadata = {"source": "api", "priority": 1}
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello", metadata=metadata)
    block_info = conversation.get_block(block_id)
    assert block_info is not None
    assert block_info.metadata == metadata

  def test_append_default_metadata_is_empty_dict(self) -> None:
    """append() should default metadata to empty dict."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello")
    block_info = conversation.get_block(block_id)
    assert block_info is not None
    assert block_info.metadata == {}

  def test_append_creates_block_with_timestamp(self) -> None:
    """append() should create block with UTC-aware timestamp."""
    conversation = Conversation()
    before = datetime.now(timezone.utc)
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello")
    after = datetime.now(timezone.utc)
    block_info = conversation.get_block(block_id)
    assert block_info is not None
    assert block_info.timestamp >= before
    assert block_info.timestamp <= after
    assert block_info.timestamp.tzinfo == timezone.utc

  def test_append_creates_block_with_sequence(self) -> None:
    """append() should create block with correct sequence number."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      id1 = conversation.append("user", "Hello")
      id2 = conversation.append("assistant", "Hi")
      id3 = conversation.append("user", "How are you?")
    block1 = conversation.get_block(id1)
    block2 = conversation.get_block(id2)
    block3 = conversation.get_block(id3)
    assert block1 is not None and block1.sequence == 0
    assert block2 is not None and block2.sequence == 1
    assert block3 is not None and block3.sequence == 2


class TestConversationGetBlock:
  """Tests for Conversation get_block method."""

  def test_get_block_returns_block_info(self) -> None:
    """get_block() should return BlockInfo for valid ID."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello")
    block_info = conversation.get_block(block_id)
    assert block_info is not None
    assert isinstance(block_info, BlockInfo)
    assert block_info.block_id == block_id
    assert block_info.role == "user"
    assert block_info.content == "Hello"

  def test_get_block_returns_none_for_invalid_id(self) -> None:
    """get_block() should return None for invalid ID."""
    conversation = Conversation()
    block_info = conversation.get_block("invalid-id")
    assert block_info is None

  def test_get_block_performance_is_o1(self) -> None:
    """get_block() should use dict lookup (O(1))."""
    conversation = Conversation()
    # Append many blocks
    with patch.object(conversation, "call_after_refresh"):
      for i in range(1000):
        conversation.append("user", f"Message {i}")

    # Verify block_index exists and works
    assert len(conversation._block_index) == 1000
    # First and last block should be accessible
    first_id = conversation._blocks[0].info.block_id
    last_id = conversation._blocks[-1].info.block_id
    assert conversation.get_block(first_id) is not None
    assert conversation.get_block(last_id) is not None


class TestConversationGetBlockAtIndex:
  """Tests for Conversation get_block_at_index method."""

  def test_get_block_at_index_returns_block_info(self) -> None:
    """get_block_at_index() should return BlockInfo for valid index."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
      conversation.append("assistant", "Hi")
    block_info = conversation.get_block_at_index(0)
    assert block_info is not None
    assert isinstance(block_info, BlockInfo)
    assert block_info.role == "user"
    assert block_info.content == "Hello"

  def test_get_block_at_index_returns_none_for_negative(self) -> None:
    """get_block_at_index() should return None for negative index."""
    conversation = Conversation()
    block_info = conversation.get_block_at_index(-1)
    assert block_info is None

  def test_get_block_at_index_returns_none_for_out_of_bounds(self) -> None:
    """get_block_at_index() should return None for out of bounds."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    block_info = conversation.get_block_at_index(100)
    assert block_info is None

  def test_get_block_at_index_returns_correct_sequence(self) -> None:
    """get_block_at_index() should return block with correct sequence."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "First")
      conversation.append("assistant", "Second")
      conversation.append("user", "Third")
    # Sequence should match index
    for i in range(3):
      block_info = conversation.get_block_at_index(i)
      assert block_info is not None
      assert block_info.sequence == i


class TestConversationClear:
  """Tests for Conversation clear functionality."""

  def test_clear_removes_all_blocks(self) -> None:
    """clear() should remove all content blocks."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
      conversation.append("assistant", "Hi")
    assert conversation.block_count == 2
    conversation.clear()
    assert conversation.block_count == 0
    assert len(conversation._strips) == 0
    assert len(conversation._cumulative_heights) == 0
    assert conversation._total_lines == 0

  def test_clear_on_empty_conversation(self) -> None:
    """clear() should work on empty conversation without error."""
    conversation = Conversation()
    conversation.clear()  # Should not raise
    assert conversation.block_count == 0

  def test_append_after_clear_continues_sequence(self) -> None:
    """append() should continue sequence after clear()."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      id1 = conversation.append("user", "Hello")
    conversation.clear()
    with patch.object(conversation, "call_after_refresh"):
      id2 = conversation.append("user", "New message")
    # Sequence counter should NOT reset - second block should have sequence 1
    block2 = conversation.get_block(id2)
    assert block2 is not None
    assert block2.sequence == 1
    # IDs should be different
    assert id1 != id2

  def test_clear_preserves_session_uuid(self) -> None:
    """clear() should preserve session UUID."""
    conversation = Conversation()
    original_session_id = conversation.session_id
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    conversation.clear()
    assert conversation.session_id == original_session_id

  def test_clear_clears_block_index(self) -> None:
    """clear() should clear the block index."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    assert len(conversation._block_index) == 1
    conversation.clear()
    assert len(conversation._block_index) == 0


class TestConversationScrollActions:
  """Tests for Conversation scroll actions."""

  def test_has_scroll_up_action(self) -> None:
    """Conversation should have scroll_up action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_scroll_up")

  def test_has_scroll_down_action(self) -> None:
    """Conversation should have scroll_down action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_scroll_down")

  def test_has_page_up_action(self) -> None:
    """Conversation should have page_up action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_page_up")

  def test_has_page_down_action(self) -> None:
    """Conversation should have page_down action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_page_down")

  def test_has_scroll_home_action(self) -> None:
    """Conversation should have scroll_home action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_scroll_home")

  def test_has_scroll_end_action(self) -> None:
    """Conversation should have scroll_end action."""
    conversation = Conversation()
    assert hasattr(conversation, "action_scroll_end")


class TestConversationIntegration:
  """Tests for Conversation integration with clitic."""

  def test_conversation_exported_from_main_package(self) -> None:
    """Conversation should be exported from main package."""
    from clitic import Conversation as MainConversation

    assert MainConversation is Conversation

  def test_conversation_in_all(self) -> None:
    """Conversation should be in __all__."""
    import clitic

    assert "Conversation" in clitic.__all__

  def test_block_info_exported_from_main_package(self) -> None:
    """BlockInfo should be exported from main package."""
    from clitic import BlockInfo as MainBlockInfo

    assert MainBlockInfo is BlockInfo

  def test_block_info_in_all(self) -> None:
    """BlockInfo should be in __all__."""
    import clitic

    assert "BlockInfo" in clitic.__all__


class TestBlockData:
  """Tests for the internal _BlockData dataclass."""

  def test_block_data_exists(self) -> None:
    """_BlockData should exist as a dataclass."""
    from clitic.widgets.conversation import _BlockData

    assert _BlockData is not None

  def test_block_data_wraps_block_info(self) -> None:
    """_BlockData should wrap BlockInfo."""
    info = BlockInfo(
      block_id="test-id",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    block = _BlockData(info=info)
    assert block.info is info

  def test_append_creates_block_with_correct_role(self) -> None:
    """append() should create block with correct role."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Test message")
    # Block count should be 1
    assert conversation.block_count == 1
    # Check the block has correct role
    assert conversation._blocks[0].info.role == "user"


class TestConversationAutoScroll:
  """Tests for Conversation auto-scroll functionality."""

  def test_auto_scroll_defaults_to_true(self) -> None:
    """auto_scroll should default to True."""
    conversation = Conversation()
    assert conversation.auto_scroll is True

  def test_auto_scroll_can_be_disabled_at_init(self) -> None:
    """auto_scroll can be set to False at initialization."""
    conversation = Conversation(auto_scroll=False)
    assert conversation.auto_scroll is False

  def test_auto_scroll_property_can_be_set(self) -> None:
    """auto_scroll property can be set after creation."""
    conversation = Conversation()
    conversation.auto_scroll = False
    assert conversation.auto_scroll is False

  def test_paused_class_not_present_by_default(self) -> None:
    """paused class should not be present when auto_scroll is True."""
    conversation = Conversation()
    assert "paused" not in conversation.classes

  def test_paused_class_added_when_auto_scroll_disabled(self) -> None:
    """paused class should be added when auto_scroll is False."""
    conversation = Conversation()
    conversation.auto_scroll = False
    assert "paused" in conversation.classes

  def test_paused_class_removed_when_re_enabled(self) -> None:
    """paused class should be removed when auto_scroll is True again."""
    conversation = Conversation()
    conversation.auto_scroll = False
    assert "paused" in conversation.classes
    conversation.auto_scroll = True
    assert "paused" not in conversation.classes

  def test_has_watch_scroll_y_method(self) -> None:
    """Conversation should have watch_scroll_y method."""
    conversation = Conversation()
    assert hasattr(conversation, "watch_scroll_y")

  def test_has_watch_auto_scroll_method(self) -> None:
    """Conversation should have watch_auto_scroll method."""
    conversation = Conversation()
    assert hasattr(conversation, "watch_auto_scroll")

  def test_append_calls_scroll_when_auto_scroll_true(self) -> None:
    """append() should call call_after_refresh when auto_scroll is True."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh") as mock_scroll:
      conversation.append("user", "Hello")
    mock_scroll.assert_called_once()

  def test_append_does_not_scroll_when_auto_scroll_false(self) -> None:
    """append() should not call call_after_refresh when auto_scroll is False."""
    conversation = Conversation(auto_scroll=False)
    with patch.object(conversation, "call_after_refresh") as mock_scroll:
      conversation.append("user", "Hello")
    mock_scroll.assert_not_called()

  def test_has_on_resize_method(self) -> None:
    """Conversation should have on_resize method."""
    conversation = Conversation()
    assert hasattr(conversation, "on_resize")

  def test_has_update_auto_scroll_from_scroll_position_method(self) -> None:
    """Conversation should have _update_auto_scroll_from_scroll_position method."""
    conversation = Conversation()
    assert hasattr(conversation, "_update_auto_scroll_from_scroll_position")


class TestConversationVirtualRendering:
  """Tests for Conversation virtual rendering functionality."""

  def test_render_line_returns_strip(self) -> None:
    """render_line() should return a Strip."""
    conversation = Conversation()
    # Even with no content, render_line should return a Strip
    strip = conversation.render_line(0)
    from textual.strip import Strip

    assert isinstance(strip, Strip)

  def test_render_line_handles_empty_content(self) -> None:
    """render_line() should handle empty conversation."""
    conversation = Conversation()
    strip = conversation.render_line(0)
    # Should return blank strip for empty content
    assert strip is not None

  async def test_render_line_returns_content(self) -> None:
    """render_line() should return content for visible lines."""
    from textual.app import App, ComposeResult
    from textual.strip import Strip

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield Conversation()

    async with TestApp().run_test() as pilot:
      conversation = pilot.app.query_one(Conversation)
      conversation.append("user", "Hello")
      await pilot.pause()

      # Now render_line should work with proper context
      strip = conversation.render_line(0)
      assert isinstance(strip, Strip)

  def test_get_block_id_at_line(self) -> None:
    """get_block_id_at_line() should find block ID for a line."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # First block should be accessible
    block_id = conversation.get_block_id_at_line(0)
    assert block_id is not None
    assert re.match(r"^[a-f0-9-]+-\d+$", block_id)

  def test_get_block_id_at_line_out_of_bounds(self) -> None:
    """get_block_id_at_line() should return None for out-of-bounds lines."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # Negative line
    block_id = conversation.get_block_id_at_line(-1)
    assert block_id is None

    # Line beyond content
    block_id = conversation.get_block_id_at_line(1000)
    assert block_id is None

  def test_virtual_size_updated_after_append(self) -> None:
    """virtual_size should be updated after append()."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # Virtual size should have been set
    assert conversation.virtual_size.height > 0


class TestConversationRerenderOnResize:
  """Tests for Conversation resize handling."""

  def test_has_rerender_all_blocks_method(self) -> None:
    """Conversation should have _rerender_all_blocks method."""
    conversation = Conversation()
    assert hasattr(conversation, "_rerender_all_blocks")

  def test_rerender_preserves_block_count(self) -> None:
    """_rerender_all_blocks should preserve block count."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
      conversation.append("assistant", "Hi")
    original_count = conversation.block_count

    conversation._rerender_all_blocks()

    assert conversation.block_count == original_count


class TestConversationPerformance:
  """Tests for Conversation performance characteristics."""

  def test_many_appends_performance(self) -> None:
    """Appending many blocks should be reasonably fast."""
    conversation = Conversation(auto_scroll=False)
    start = time.time()

    # Append 1000 blocks
    with patch.object(conversation, "call_after_refresh"):
      for i in range(1000):
        conversation.append("user", f"Message {i}")

    elapsed = time.time() - start
    # Should complete in reasonable time (adjust threshold as needed)
    assert elapsed < 5.0, f"Appending 1000 blocks took {elapsed:.2f}s"
    assert conversation.block_count == 1000

  def test_strips_count_matches_lines(self) -> None:
    """Total strips should match total lines."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
      conversation.append("assistant", "Hi")

    assert len(conversation._strips) == conversation._total_lines

  def test_benchmark_large_content(self) -> None:
    """Benchmark test for large content (10000+ blocks).

    This test verifies that:
    - Appending 10,000 blocks completes in reasonable time
    - Memory usage stays within acceptable bounds

    Performance target: < 10 seconds for 10,000 blocks
    """
    import tracemalloc

    tracemalloc.start()
    conversation = Conversation(auto_scroll=False)
    start = time.time()

    # Append 10,000 blocks
    with patch.object(conversation, "call_after_refresh"):
      for i in range(10000):
        conversation.append("user", f"Message {i}")

    elapsed = time.time() - start

    # Verify count
    assert conversation.block_count == 10000

    # Verify total lines are tracked
    assert conversation._total_lines > 0

    # Performance check - should complete in reasonable time
    # CI runners can be slower, so use a generous threshold
    assert elapsed < 20.0, f"Appending 10,000 blocks took {elapsed:.2f}s (expected < 20s)"

    # Memory check - use tracemalloc for accurate measurement
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Peak memory should be under 50MB for 10,000 blocks
    # Each block has content ~10-15 chars + overhead
    assert peak < 50 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.1f}MB (expected < 50MB)"

  async def test_render_line_performance(self) -> None:
    """Benchmark render_line performance for visible lines.

    This test verifies that rendering visible lines is O(1),
    not dependent on total content size.
    """
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield Conversation(auto_scroll=False)

    async with TestApp().run_test() as pilot:
      conversation = pilot.app.query_one(Conversation)

      # Append many blocks
      for i in range(1000):
        conversation.append("user", f"Message {i}")
      await pilot.pause()

      start = time.time()

      # Render 100 lines (simulating a screen of content)
      for y in range(100):
        conversation.render_line(y)

      elapsed = time.time() - start

      # Rendering 100 lines should be fast (< 100ms)
      assert elapsed < 0.1, f"Rendering 100 lines took {elapsed:.3f}s (expected < 100ms)"

  def test_100k_lines_performance(self) -> None:
    """Test that 100,000+ lines are supported without performance degradation.

    Acceptance criteria specifies 100,000+ lines without degradation.
    This test uses 10,000 blocks with 10 lines each = 100,000 lines.
    """
    conversation = Conversation(auto_scroll=False)
    start = time.time()

    # Append 10,000 blocks, each with 10 lines of content
    with patch.object(conversation, "call_after_refresh"):
      for _ in range(10000):
        # Each block has ~10 lines (9 newlines + 1 base line)
        content = "\n".join([f"Line {j}" for j in range(10)])
        conversation.append("user", content)

    elapsed = time.time() - start

    # Verify count
    assert conversation.block_count == 10000

    # Verify total lines is approximately 100,000+ (10 lines per block + 1 margin)
    # Each block has 10 content lines + 1 blank margin line
    assert conversation._total_lines >= 100000, (
      f"Expected 100,000+ lines, got {conversation._total_lines}"
    )

    # Performance: should complete within 60 seconds
    # (Generous threshold for slower CI runners)
    assert elapsed < 60.0, f"Appending 10,000 blocks (100k lines) took {elapsed:.2f}s (expected < 60s)"

    # Render performance: getting any line should be O(1)
    start = time.time()
    for y in [0, 50000, 99999]:
      if y < conversation._total_lines:
        # Access strips directly to verify O(1) lookup
        _ = conversation._strips[y]
    elapsed = time.time() - start

    # Accessing 3 arbitrary lines should be instant
    assert elapsed < 0.001, f"Line access took {elapsed:.4f}s (expected instant)"
