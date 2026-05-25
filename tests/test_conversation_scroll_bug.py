"""Tests for Conversation widget scroll/render bug.

This module tests the bug where lines from different blocks bleed into each other
when scrolling, specifically when plugin content is used with role labels on
separate lines.

Bug symptoms:
- First line of markdown/code plugin content duplicates into the role header line
- System lines sometimes merge into following blocks
- Lines bleed into each other when scrolling up
"""

from unittest.mock import patch

from rich.text import Text

from clitic import Conversation
from clitic.plugins import ContentPlugin


class SimplePlugin(ContentPlugin):
  """Simple plugin for testing that returns predictable content."""

  @property
  def name(self) -> str:
    return "SimplePlugin"

  @property
  def priority(self) -> int:
    return 10

  def can_render(self, content_type: str, content: str) -> bool:
    return content_type == "test/simple"

  def render(self, content: str) -> Text:
    # Return text with clear line markers for testing
    return Text(content)


class TestConversationScrollRenderBug:
  """Tests for the scroll/render bug with plugin content."""

  def test_strips_correct_order_with_plugin_content(self) -> None:
    """Verify strips are in correct order: role_label + content + blank."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Line1\nLine2\nLine3",
        metadata={"content_type": "test/simple"},
      )

    # Should have: role_label_strip + 3 content strips + blank_strip
    # Total: 5 strips
    assert len(conversation._strips) == 5, f"Expected 5 strips, got {len(conversation._strips)}"

    # First strip should be the role label
    first_strip = conversation._strips[0]
    # Get text content from segments
    first_text = "".join(seg.text for seg in first_strip if hasattr(seg, "text"))
    assert "Assistant" in first_text, f"First strip should contain role label, got: {first_text}"

    # Last strip should be blank
    last_strip = conversation._strips[-1]
    last_text = "".join(seg.text for seg in last_strip if hasattr(seg, "text"))
    assert last_text.strip() == "", f"Last strip should be blank, got: {last_text}"

  def test_cumulative_heights_correct_with_plugin_content(self) -> None:
    """Verify cumulative heights correctly track plugin content lines."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Line1\nLine2",
        metadata={"content_type": "test/simple"},
      )

    # Block should have: role_label + 2 content + blank = 4 lines
    assert conversation._cumulative_heights == [4], (
      f"Expected [4], got {conversation._cumulative_heights}"
    )

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "user",
        "UserLine1",
        metadata={"content_type": "test/simple"},
      )

    # Second block should have: role_label + 1 content + blank = 3 lines
    # Total: 4 + 3 = 7
    assert conversation._cumulative_heights == [4, 7], (
      f"Expected [4, 7], got {conversation._cumulative_heights}"
    )

  def test_strips_width_consistency(self) -> None:
    """Verify all strips have consistent width."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    # Force a specific width
    conversation._last_width = 80

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Line1\nLine2",
        metadata={"content_type": "test/simple"},
      )

    # Check all strips have the same width
    widths = [strip.cell_length for strip in conversation._strips]
    # All widths should be the same
    assert len(set(widths)) == 1, f"All strips should have the same width, got: {widths}"

  def test_render_line_returns_correct_strip(self) -> None:
    """Verify render_line returns the correct strip for each line."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Line1\nLine2",
        metadata={"content_type": "test/simple"},
      )

    # Verify line 0 is role label
    strip_0 = conversation._strips[0]
    text_0 = "".join(seg.text for seg in strip_0 if hasattr(seg, "text"))
    assert "Assistant" in text_0, f"Line 0 should be role label, got: {text_0}"

    # Verify line 1 is first content line
    strip_1 = conversation._strips[1]
    text_1 = "".join(seg.text for seg in strip_1 if hasattr(seg, "text"))
    assert "Line1" in text_1, f"Line 1 should contain 'Line1', got: {text_1}"

    # Verify line 2 is second content line
    strip_2 = conversation._strips[2]
    text_2 = "".join(seg.text for seg in strip_2 if hasattr(seg, "text"))
    assert "Line2" in text_2, f"Line 2 should contain 'Line2', got: {text_2}"

  def test_multiple_blocks_strip_ordering(self) -> None:
    """Verify strips are correctly ordered across multiple blocks."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      # Block 0: assistant, 2 content lines + role + blank = 4 strips
      conversation.append(
        "assistant",
        "A1\nA2",
        metadata={"content_type": "test/simple"},
      )
      # Block 1: user, 1 content line + role + blank = 3 strips
      conversation.append(
        "user",
        "U1",
        metadata={"content_type": "test/simple"},
      )

    # Total: 4 + 3 = 7 strips
    assert len(conversation._strips) == 7, f"Expected 7 strips, got {len(conversation._strips)}"

    # Verify ordering
    # Strip 0: Assistant role label
    # Strip 1: A1
    # Strip 2: A2
    # Strip 3: blank
    # Strip 4: User role label
    # Strip 5: U1
    # Strip 6: blank

    text_0 = "".join(seg.text for seg in conversation._strips[0] if hasattr(seg, "text"))
    assert "Assistant" in text_0, f"Strip 0 should be Assistant role, got: {text_0}"

    text_1 = "".join(seg.text for seg in conversation._strips[1] if hasattr(seg, "text"))
    assert "A1" in text_1, f"Strip 1 should contain A1, got: {text_1}"

    text_4 = "".join(seg.text for seg in conversation._strips[4] if hasattr(seg, "text"))
    assert "User" in text_4, f"Strip 4 should be User role, got: {text_4}"

  def test_get_block_id_at_line_with_plugin_content(self) -> None:
    """Verify get_block_id_at_line returns correct block for each line."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      # Block 0: 4 lines (role + 2 content + blank)
      conversation.append(
        "assistant",
        "A1\nA2",
        metadata={"content_type": "test/simple"},
      )
      # Block 1: 3 lines (role + 1 content + blank)
      conversation.append(
        "user",
        "U1",
        metadata={"content_type": "test/simple"},
      )

    # Line 0-3 should be block 0
    for line in range(4):
      block_id = conversation.get_block_id_at_line(line)
      assert block_id == conversation._blocks[0].info.block_id, f"Line {line} should be in block 0"

    # Line 4-6 should be block 1
    for line in range(4, 7):
      block_id = conversation.get_block_id_at_line(line)
      assert block_id == conversation._blocks[1].info.block_id, f"Line {line} should be in block 1"

  def test_role_label_strip_width_matches_content_width(self) -> None:
    """Verify role label strip width matches content strips width."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    # Mock _get_content_width to return a specific value
    conversation._get_content_width = lambda: 100

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Content",
        metadata={"content_type": "test/simple"},
      )

    # All strips should have the same width
    widths = [strip.cell_length for strip in conversation._strips]
    assert len(set(widths)) == 1, f"All strips should have same width, got: {widths}"

  def test_strips_remain_consistent_after_rerender(self) -> None:
    """Verify strips remain consistent after re-rendering all blocks."""
    plugin = SimplePlugin()
    conversation = Conversation(plugins=[plugin])

    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "A1\nA2",
        metadata={"content_type": "test/simple"},
      )
      conversation.append(
        "user",
        "U1",
        metadata={"content_type": "test/simple"},
      )

    # Store original strip contents
    original_texts = []
    for strip in conversation._strips:
      text = "".join(seg.text for seg in strip if hasattr(seg, "text"))
      original_texts.append(text)

    # Re-render
    conversation._rerender_all_blocks()

    # Verify strip contents are preserved (same order)
    for i, (strip, original_text) in enumerate(
      zip(conversation._strips, original_texts, strict=True)
    ):
      text = "".join(seg.text for seg in strip if hasattr(seg, "text"))
      # Normalize whitespace for comparison
      assert text.strip() == original_text.strip(), (
        f"Strip {i} changed after rerender: was '{original_text}', now '{text}'"
      )

  def test_scroll_up_with_plugin_content_preserves_strip_order(self) -> None:
    """Verify scrolling up doesn't corrupt strip order.

    This test specifically targets the reported bug where lines
    bleed into each other when scrolling.
    """
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield Conversation(plugins=[SimplePlugin()])

    import asyncio

    async def run_test():
      app = TestApp()
      async with app.run_test() as pilot:
        conversation = pilot.app.query_one(Conversation)

        # Add enough content to enable scrolling
        for i in range(10):
          conversation.append(
            "assistant" if i % 2 == 0 else "user",
            f"Content{i}_Line1\nContent{i}_Line2\nContent{i}_Line3",
            metadata={"content_type": "test/simple"},
          )

        # Wait for layout
        await pilot.pause()

        # Store all strip references before scrolling
        original_strips = list(conversation._strips)

        # Simulate scrolling up (reducing scroll_y)
        conversation.scroll_to(0, animate=False)
        await pilot.pause()

        # After scrolling to top, strips should still be the same objects
        for i, (original, current) in enumerate(
          zip(original_strips, conversation._strips, strict=True)
        ):
          assert original is current, f"Strip {i} changed after scroll"

        # Verify strip content at various positions
        # First strip should be role label
        first_text = conversation._strips[0].text
        assert "Assistant" in first_text, f"First strip should be role label: {first_text}"

        # Second strip should be first content line
        second_text = conversation._strips[1].text
        assert "Content0_Line1" in second_text, f"Second strip should be content: {second_text}"

    asyncio.run(run_test())
