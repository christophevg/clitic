"""Tests for Conversation widget."""

import time
from unittest.mock import patch

from textual.scroll_view import ScrollView

from clitic import Conversation


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


class TestConversationProperties:
  """Tests for Conversation properties."""

  def test_block_count_default_is_zero(self) -> None:
    """block_count should default to 0."""
    conversation = Conversation()
    assert conversation.block_count == 0


class TestConversationAppend:
  """Tests for Conversation append functionality."""

  def test_append_returns_block_id(self) -> None:
    """append() should return a unique block ID."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "Hello")
    assert block_id == "block-0"

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
    assert id1 == "block-0"
    assert id2 == "block-1"
    assert id3 == "block-2"
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

  def test_append_after_clear(self) -> None:
    """append() should work after clear()."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")
    conversation.clear()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("user", "New message")
    # Counter should reset to 0 after clear
    assert block_id == "block-0"
    assert conversation.block_count == 1


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


class TestBlockData:
  """Tests for the internal _BlockData dataclass."""

  def test_block_data_exists(self) -> None:
    """_BlockData should exist as a dataclass."""
    from clitic.widgets.conversation import _BlockData

    assert _BlockData is not None

  def test_append_creates_block_with_correct_role(self) -> None:
    """append() should create block with correct role."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Test message")
    # Block count should be 1
    assert conversation.block_count == 1
    # Check the block has correct role
    assert conversation._blocks[0].role == "user"


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

    # First block should have ID block-0
    block_id = conversation.get_block_id_at_line(0)
    assert block_id == "block-0"

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
    assert elapsed < 10.0, f"Appending 10,000 blocks took {elapsed:.2f}s (expected < 10s)"

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

    # Performance: should complete within 30 seconds
    # (This is a generous threshold; actual performance should be better)
    assert elapsed < 30.0, f"Appending 10,000 blocks (100k lines) took {elapsed:.2f}s (expected < 30s)"

    # Render performance: getting any line should be O(1)
    start = time.time()
    for y in [0, 50000, 99999]:
      if y < conversation._total_lines:
        # Access strips directly to verify O(1) lookup
        _ = conversation._strips[y]
    elapsed = time.time() - start

    # Accessing 3 arbitrary lines should be instant
    assert elapsed < 0.001, f"Line access took {elapsed:.4f}s (expected instant)"
