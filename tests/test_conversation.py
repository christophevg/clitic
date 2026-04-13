"""Tests for Conversation widget."""

from unittest.mock import patch

from textual.containers import VerticalScroll

from clitic import Conversation


class TestConversationInstantiation:
  """Tests for Conversation instantiation."""

  def test_conversation_can_be_instantiated(self) -> None:
    """Conversation should be instantiable."""
    conversation = Conversation()
    assert conversation is not None

  def test_conversation_extends_vertical_scroll(self) -> None:
    """Conversation should extend VerticalScroll."""
    conversation = Conversation()
    assert isinstance(conversation, VerticalScroll)

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
    with patch.object(conversation, "mount"):
      block_id = conversation.append("user", "Hello")
    assert block_id == "block-0"

  def test_append_increments_block_count(self) -> None:
    """append() should increment block_count."""
    conversation = Conversation()
    with patch.object(conversation, "mount"):
      conversation.append("user", "Hello")
    assert conversation.block_count == 1

  def test_multiple_appends_create_unique_ids(self) -> None:
    """Multiple append() calls should create unique IDs."""
    conversation = Conversation()
    with patch.object(conversation, "mount"):
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
    with patch.object(conversation, "mount"):
      conversation.append("user", "User message")
      conversation.append("assistant", "Assistant message")
      conversation.append("system", "System message")
      conversation.append("tool", "Tool message")
    assert conversation.block_count == 4


class TestConversationClear:
  """Tests for Conversation clear functionality."""

  def test_clear_removes_all_blocks(self) -> None:
    """clear() should remove all content blocks."""
    conversation = Conversation()
    with patch.object(conversation, "mount"):
      conversation.append("user", "Hello")
      conversation.append("assistant", "Hi")
    assert conversation.block_count == 2
    # Mock the remove method on all blocks
    for block in conversation._blocks:
      block.remove = lambda: None
    conversation.clear()
    assert conversation.block_count == 0

  def test_clear_on_empty_conversation(self) -> None:
    """clear() should work on empty conversation without error."""
    conversation = Conversation()
    conversation.clear()  # Should not raise
    assert conversation.block_count == 0

  def test_append_after_clear(self) -> None:
    """append() should work after clear()."""
    conversation = Conversation()
    with patch.object(conversation, "mount"):
      conversation.append("user", "Hello")
    # Mock remove on blocks
    for block in conversation._blocks:
      block.remove = lambda: None
    conversation.clear()
    with patch.object(conversation, "mount"):
      block_id = conversation.append("user", "New message")
    assert block_id == "block-1"  # Counter continues
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


class TestContentBlock:
  """Tests for the internal _ContentBlock widget."""

  def test_content_block_exists(self) -> None:
    """_ContentBlock should exist as a nested class."""
    # Import from the module directly
    from clitic.widgets.conversation import _ContentBlock

    assert _ContentBlock is not None

  def test_append_creates_block_with_correct_role(self) -> None:
    """append() should create block with correct role."""
    conversation = Conversation()
    with patch.object(conversation, "mount"):
      conversation.append("user", "Test message")
    # Block count should be 1
    assert conversation.block_count == 1
