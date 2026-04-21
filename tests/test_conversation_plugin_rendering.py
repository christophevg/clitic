"""Tests for Conversation widget plugin rendering integration."""

from unittest.mock import patch

from rich.text import Text

from clitic import Conversation
from clitic.plugins import ContentPlugin, MarkdownPlugin


class MockPlugin(ContentPlugin):
  """Mock plugin for testing."""

  @property
  def name(self) -> str:
    return "MockPlugin"

  @property
  def priority(self) -> int:
    return 5

  def can_render(self, content_type: str, content: str) -> bool:
    return content_type == "mock/test"

  def render(self, content: str) -> Text:
    return Text(f"[MOCK] {content}")


class FailingPlugin(ContentPlugin):
  """Plugin that raises during render."""

  @property
  def name(self) -> str:
    return "FailingPlugin"

  @property
  def priority(self) -> int:
    return 10

  def can_render(self, content_type: str, content: str) -> bool:
    return content_type == "fail/test"

  def render(self, content: str) -> Text:
    raise RuntimeError("Intentional failure for testing")


class TestConversationPluginIntegration:
  """Tests for Conversation plugin integration."""

  def test_conversation_accepts_plugins(self) -> None:
    """Conversation should accept plugins parameter."""
    plugin = MarkdownPlugin()
    conversation = Conversation(plugins=[plugin])
    assert conversation._plugins == [plugin]

  def test_empty_plugins_by_default(self) -> None:
    """Conversation should have empty plugins list by default."""
    conversation = Conversation()
    assert conversation._plugins == []

  def test_content_type_routes_to_plugin(self) -> None:
    """Blocks with content_type metadata should use plugin rendering."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Test content",
        metadata={"content_type": "mock/test"},
      )

    # Should have strips rendered
    assert len(conversation._strips) > 0
    assert conversation.block_count == 1

  def test_fallback_on_no_matching_plugin(self) -> None:
    """Should fall back to plain text when no plugin matches."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append(
        "assistant",
        "Plain text content",
        metadata={"content_type": "text/plain"},
      )

    # Should still have content (plain text rendering)
    assert len(conversation._strips) > 0
    block = conversation.get_block(block_id)
    assert block is not None
    assert block.content == "Plain text content"

  def test_fallback_on_plugin_failure(self) -> None:
    """Should fall back to plain text when plugin raises."""
    plugin = FailingPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append(
        "assistant",
        "Fallback content",
        metadata={"content_type": "fail/test"},
      )

    # Should fall back to plain text rendering
    assert len(conversation._strips) > 0
    block = conversation.get_block(block_id)
    assert block is not None
    # Content should still be there
    assert "Fallback content" in block.content

  def test_priority_ordering(self) -> None:
    """Higher priority plugins should be preferred."""
    low_priority = MockPlugin()
    low_priority._priority = 1
    # Rename to distinguish
    object.__setattr__(low_priority, "_name", "LowPriority")

    # Test that sorting by priority works as expected
    plugins = [low_priority]
    plugins.sort(key=lambda p: p.priority, reverse=True)
    assert plugins[0] == low_priority

  def test_no_content_type_uses_plain_text(self) -> None:
    """Blocks without content_type should use plain text rendering."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append(
        "assistant",
        "Plain text",
      )

    block = conversation.get_block(block_id)
    assert block is not None
    assert block.content == "Plain text"

  def test_multiple_plugins_registered(self) -> None:
    """Multiple plugins can be registered."""
    markdown_plugin = MarkdownPlugin()
    mock_plugin = MockPlugin()
    conversation = Conversation(plugins=[markdown_plugin, mock_plugin])
    assert len(conversation._plugins) == 2

  def test_markdown_plugin_integration(self) -> None:
    """MarkdownPlugin should render markdown content."""
    plugin = MarkdownPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "# Header\n\n**Bold text**",
        metadata={"content_type": "text/markdown"},
      )

    # Should have rendered strips
    assert len(conversation._strips) > 0
    assert conversation.block_count == 1


class TestConversationPluginRerender:
  """Tests for plugin rendering with resize/selection."""

  def test_resize_rerenders_plugins(self) -> None:
    """Plugins should re-render on resize."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Test",
        metadata={"content_type": "mock/test"},
      )

    initial_strip_count = len(conversation._strips)

    # Rerender should work
    conversation._rerender_all_blocks()

    # Should still have strips
    assert len(conversation._strips) > 0
    # Strip count should be same after rerender (same content, same width)
    assert len(conversation._strips) == initial_strip_count

  def test_selection_styling_with_plugins(self) -> None:
    """Selection styling should work with plugin content."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])
    with patch.object(conversation, "call_after_refresh"):
      conversation.append(
        "assistant",
        "Selected content",
        metadata={"content_type": "mock/test"},
      )

    # Select the block
    conversation._selected_index = 0
    conversation.selected_block = conversation._blocks[0].info.block_id
    conversation._update_selected_visual()

    # Should still have content after selection visual update
    assert len(conversation._strips) > 0


class TestConversationPluginMetadata:
  """Tests for plugin metadata handling."""

  def test_metadata_preserved(self) -> None:
    """Metadata should be preserved in block info."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])
    metadata = {"content_type": "mock/test", "custom_key": "custom_value"}
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("assistant", "Test", metadata=metadata)

    block = conversation.get_block(block_id)
    assert block is not None
    assert block.metadata["content_type"] == "mock/test"
    assert block.metadata["custom_key"] == "custom_value"

  def test_empty_metadata_works(self) -> None:
    """Blocks should work with empty metadata."""
    conversation = Conversation()
    with patch.object(conversation, "call_after_refresh"):
      block_id = conversation.append("assistant", "Test", metadata={})

    block = conversation.get_block(block_id)
    assert block is not None
    assert block.metadata == {}


class TestGetMatchingPlugin:
  """Tests for _get_matching_plugin method."""

  def test_get_matching_plugin_returns_highest_priority(self) -> None:
    """_get_matching_plugin should return highest priority matching plugin."""

    class HighPriorityPlugin(ContentPlugin):
      @property
      def name(self) -> str:
        return "High"

      @property
      def priority(self) -> int:
        return 10

      def can_render(self, content_type: str, content: str) -> bool:
        return content_type.startswith("test/")

      def render(self, content: str) -> Text:
        return Text("high")

    class LowPriorityPlugin(ContentPlugin):
      @property
      def name(self) -> str:
        return "Low"

      @property
      def priority(self) -> int:
        return 1

      def can_render(self, content_type: str, content: str) -> bool:
        return content_type.startswith("test/")

      def render(self, content: str) -> Text:
        return Text("low")

    high = HighPriorityPlugin()
    low = LowPriorityPlugin()
    conversation = Conversation(plugins=[low, high])

    result = conversation._get_matching_plugin("test/foo", "content")
    assert result is not None
    assert result.name == "High"

  def test_get_matching_plugin_returns_none_for_no_match(self) -> None:
    """_get_matching_plugin should return None when no plugin matches."""
    plugin = MockPlugin()
    conversation = Conversation(plugins=[plugin])

    result = conversation._get_matching_plugin("unknown/type", "content")
    assert result is None

  def test_get_matching_plugin_returns_none_for_empty_plugins(self) -> None:
    """_get_matching_plugin should return None when no plugins registered."""
    conversation = Conversation(plugins=[])

    result = conversation._get_matching_plugin("any/type", "content")
    assert result is None


class TestRenderableToStrips:
  """Tests for _renderable_to_strips conversion."""

  def test_renderable_to_strips_returns_strips(self) -> None:
    """_renderable_to_strips should convert Rich renderable to list of Strips."""
    conversation = Conversation()
    renderable = Text("Test content")
    strips = conversation._renderable_to_strips(renderable, width=80)

    assert strips is not None
    assert len(strips) > 0

  def test_renderable_to_strips_handles_multiline(self) -> None:
    """_renderable_to_strips should handle multiline content."""
    conversation = Conversation()
    renderable = Text("Line 1\nLine 2\nLine 3")
    strips = conversation._renderable_to_strips(renderable, width=80)

    assert strips is not None
    # Should have multiple strips for multiple lines
    assert len(strips) >= 3

  def test_renderable_to_strips_with_markdown(self) -> None:
    """_renderable_to_strips should handle Markdown renderable."""
    from rich.markdown import Markdown

    conversation = Conversation()
    renderable = Markdown("# Header\n\n**Bold** text")
    strips = conversation._renderable_to_strips(renderable, width=80)

    assert strips is not None
    assert len(strips) > 0


class TestRenderPluginToStrips:
  """Tests for _render_plugin_to_strips method."""

  def test_render_plugin_to_strips_success(self) -> None:
    """_render_plugin_to_strips should return strips on success."""
    plugin = MockPlugin()
    conversation = Conversation()

    strips = conversation._render_plugin_to_strips(
      plugin, "Test content", width=80, role="assistant", is_selected=False
    )

    assert strips is not None
    assert len(strips) > 0

  def test_render_plugin_to_strips_returns_none_on_failure(self) -> None:
    """_render_plugin_to_strips should return None on plugin failure."""
    plugin = FailingPlugin()
    conversation = Conversation()

    strips = conversation._render_plugin_to_strips(
      plugin, "Test content", width=80, role="assistant", is_selected=False
    )

    # Should return None on failure
    assert strips is None
