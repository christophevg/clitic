"""Tests for Conversation block navigation functionality."""

from unittest.mock import patch

import pytest
from textual.app import App, ComposeResult

from clitic import Conversation


class ConversationTestApp(App):
    """Minimal test app with a Conversation widget."""

    def __init__(self, **kwargs):
        """Initialize with Conversation kwargs."""
        super().__init__()
        self._conv_kwargs = kwargs

    def compose(self) -> ComposeResult:
        yield Conversation(**self._conv_kwargs)


# ==============================================================================
# Test Class: Navigation Properties
# ==============================================================================


class TestNavigationProperties:
    """Tests for navigation reactive properties."""

    def test_selected_block_defaults_to_none(self) -> None:
        """selected_block should default to None."""
        conversation = Conversation()
        assert conversation.selected_block is None

    def test_wrap_navigation_defaults_to_true(self) -> None:
        """wrap_navigation should default to True."""
        conversation = Conversation()
        assert conversation.wrap_navigation is True

    def test_navigation_bell_defaults_to_true(self) -> None:
        """navigation_bell should default to True."""
        conversation = Conversation()
        assert conversation.navigation_bell is True

    def test_selected_block_index_defaults_to_none(self) -> None:
        """selected_block_index should default to None."""
        conversation = Conversation()
        assert conversation.selected_block_index is None

    def test_selected_block_index_returns_correct_value(self) -> None:
        """selected_block_index should return correct index when set."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")
            conversation.append("user", "Bye")

        # Select second block
        conversation._selected_index = 1
        assert conversation.selected_block_index == 1

    def test_selected_block_info_returns_none_when_no_selection(self) -> None:
        """selected_block_info should return None when no selection."""
        conversation = Conversation()
        assert conversation.selected_block_info is None

    def test_selected_block_info_returns_block_info(self) -> None:
        """selected_block_info should return BlockInfo for selected block."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select first block
        conversation._selected_index = 0
        info = conversation.selected_block_info
        assert info is not None
        assert info.role == "user"
        assert info.content == "Hello"


# ==============================================================================
# Test Class: Navigation Actions
# ==============================================================================


class TestNavigationActions:
    """Tests for navigation action methods."""

    def test_has_nav_prev_block_action(self) -> None:
        """Conversation should have nav_prev_block action."""
        conversation = Conversation()
        assert hasattr(conversation, "action_nav_prev_block")

    def test_has_nav_next_block_action(self) -> None:
        """Conversation should have nav_next_block action."""
        conversation = Conversation()
        assert hasattr(conversation, "action_nav_next_block")

    def test_has_deselect_block_action(self) -> None:
        """Conversation should have deselect_block action."""
        conversation = Conversation()
        assert hasattr(conversation, "action_deselect_block")

    def test_nav_next_block_selects_first_when_none(self) -> None:
        """nav_next_block should select first block when no selection."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        conversation.action_nav_next_block()

        assert conversation._selected_index == 0
        assert conversation.selected_block is not None

    def test_nav_prev_block_selects_last_when_none(self) -> None:
        """nav_prev_block should select last block when no selection."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")
            conversation.append("user", "Bye")

        conversation.action_nav_prev_block()

        assert conversation._selected_index == 2
        assert conversation.selected_block is not None

    def test_nav_next_block_moves_to_next(self) -> None:
        """nav_next_block should move to next block."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")
            conversation.append("user", "Bye")

        # Select first block
        conversation._selected_index = 0
        conversation.action_nav_next_block()

        assert conversation._selected_index == 1

        conversation.action_nav_next_block()

        assert conversation._selected_index == 2

    def test_nav_prev_block_moves_to_previous(self) -> None:
        """nav_prev_block should move to previous block."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")
            conversation.append("user", "Bye")

        # Select last block
        conversation._selected_index = 2
        conversation.action_nav_prev_block()

        assert conversation._selected_index == 1

        conversation.action_nav_prev_block()

        assert conversation._selected_index == 0

    def test_nav_next_block_wraps_when_enabled(self) -> None:
        """nav_next_block should wrap to first block when at last and wrap enabled."""
        conversation = Conversation(wrap_navigation=True)
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select last block
        conversation._selected_index = 1
        conversation.action_nav_next_block()

        assert conversation._selected_index == 0

    def test_nav_prev_block_wraps_when_enabled(self) -> None:
        """nav_prev_block should wrap to last block when at first and wrap enabled."""
        conversation = Conversation(wrap_navigation=True)
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select first block
        conversation._selected_index = 0
        conversation.action_nav_prev_block()

        assert conversation._selected_index == 1

    def test_nav_next_block_no_wrap_when_disabled(self) -> None:
        """nav_next_block should not wrap when wrap_navigation is False."""
        conversation = Conversation(wrap_navigation=False, navigation_bell=False)
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select last block
        conversation._selected_index = 1
        conversation.action_nav_next_block()

        # Should stay at last block (no wrap)
        assert conversation._selected_index == 1

    def test_nav_prev_block_no_wrap_when_disabled(self) -> None:
        """nav_prev_block should not wrap when wrap_navigation is False."""
        conversation = Conversation(wrap_navigation=False, navigation_bell=False)
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select first block
        conversation._selected_index = 0
        conversation.action_nav_prev_block()

        # Should stay at first block (no wrap)
        assert conversation._selected_index == 0

    def test_deselect_block_clears_selection(self) -> None:
        """deselect_block should clear selection."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        # Select first block
        conversation._selected_index = 0
        conversation.action_deselect_block()

        assert conversation._selected_index == -1
        assert conversation.selected_block is None

    def test_navigation_does_nothing_on_empty_conversation(self) -> None:
        """Navigation actions should do nothing on empty conversation."""
        conversation = Conversation(navigation_bell=False)

        # These should not raise
        conversation.action_nav_prev_block()
        conversation.action_nav_next_block()
        conversation.action_deselect_block()

        assert conversation._selected_index == -1
        assert conversation.selected_block is None


# ==============================================================================
# Test Class: Selection State Management
# ==============================================================================


class TestSelectionStateManagement:
    """Tests for selection state management."""

    def test_selected_block_syncs_with_index(self) -> None:
        """selected_block should sync with _selected_index."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            block_id = conversation.append("user", "Hello")

        # Set via watch_selected_block
        conversation.selected_block = block_id
        # watch_selected_block should have updated _selected_index
        assert conversation._selected_index == 0

    def test_selected_block_clears_index_when_none(self) -> None:
        """selected_block=None should clear _selected_index."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        conversation._selected_index = 0
        conversation.selected_block = None

        assert conversation._selected_index == -1

    def test_selection_cleared_on_clear(self) -> None:
        """Selection should be cleared when clear() is called."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")
            conversation.append("assistant", "Hi")

        # Select first block
        conversation._selected_index = 0
        conversation.selected_block = conversation._blocks[0].info.block_id

        conversation.clear()

        assert conversation._selected_index == -1
        assert conversation.selected_block is None

    def test_selection_not_persisted_across_sessions(self) -> None:
        """Selection should not persist in session data."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        conversation._selected_index = 0

        # Create new conversation - no selection
        new_conversation = Conversation()
        assert new_conversation._selected_index == -1
        assert new_conversation.selected_block is None


# ==============================================================================
# Test Class: Watch Callbacks
# ==============================================================================


class TestWatchCallbacks:
    """Tests for reactive watch callbacks."""

    def test_watch_selected_block_updates_index(self) -> None:
        """watch_selected_block should update _selected_index."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            block_id = conversation.append("user", "Hello")

        conversation.watch_selected_block(None, block_id)

        assert conversation._selected_index == 0

    def test_watch_selected_block_handles_invalid_id(self) -> None:
        """watch_selected_block should handle invalid block ID."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        conversation.watch_selected_block(None, "invalid-id")

        # Should clear selection for invalid ID
        assert conversation._selected_index == -1

    def test_watch_selected_block_clears_index_for_none(self) -> None:
        """watch_selected_block should clear index when set to None."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        conversation._selected_index = 0
        conversation.watch_selected_block("old-id", None)

        assert conversation._selected_index == -1


# ==============================================================================
# Test Class: Visual Updates
# ==============================================================================


class TestVisualUpdates:
    """Tests for visual update methods."""

    def test_has_update_selected_visual_method(self) -> None:
        """Conversation should have _update_selected_visual method."""
        conversation = Conversation()
        assert hasattr(conversation, "_update_selected_visual")

    def test_has_scroll_to_selected_method(self) -> None:
        """Conversation should have _scroll_to_selected method."""
        conversation = Conversation()
        assert hasattr(conversation, "_scroll_to_selected")

    def test_update_selected_visual_rerenders(self) -> None:
        """_update_selected_visual should re-render strips."""
        conversation = Conversation()
        with patch.object(conversation, "call_after_refresh"):
            conversation.append("user", "Hello")

        # Set width to enable re-render
        conversation._last_width = 80

        # Verify strips exist before update
        initial_strips = list(conversation._strips)

        conversation._selected_index = 0
        conversation._update_selected_visual()

        # Strips should have been re-rendered
        # The content should be similar but potentially with different styling
        assert len(conversation._strips) == len(initial_strips)


# ==============================================================================
# Test Class: Integration Tests
# ==============================================================================


@pytest.mark.asyncio
class TestNavigationIntegration:
    """Integration tests for navigation with app context."""

    async def test_alt_up_down_navigation(self) -> None:
        """Alt+Up and Alt+Down should navigate between blocks."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add blocks
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Hello")
                conv.append("assistant", "Hi")
                conv.append("user", "How are you?")

            await pilot.pause()

            # Alt+Down should select first block
            conv.action_nav_next_block()
            assert conv._selected_index == 0

            # Alt+Down again should select second block
            conv.action_nav_next_block()
            assert conv._selected_index == 1

            # Alt+Up should go back to first block
            conv.action_nav_prev_block()
            assert conv._selected_index == 0

    async def test_escape_clears_selection(self) -> None:
        """Escape should clear selection."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Hello")

            await pilot.pause()

            # Select block
            conv.action_nav_next_block()
            assert conv._selected_index == 0

            # Escape should clear
            conv.action_deselect_block()
            assert conv._selected_index == -1
            assert conv.selected_block is None

    async def test_wrap_navigation_full_cycle(self) -> None:
        """Wrap navigation should cycle through all blocks."""
        async with ConversationTestApp(wrap_navigation=True).run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "A")
                conv.append("assistant", "B")
                conv.append("user", "C")

            await pilot.pause()

            # Start from no selection, Alt+Down selects first
            conv.action_nav_next_block()
            assert conv._selected_index == 0

            # Navigate to last
            conv.action_nav_next_block()
            conv.action_nav_next_block()
            assert conv._selected_index == 2

            # Wrap to first
            conv.action_nav_next_block()
            assert conv._selected_index == 0

            # Wrap to last (going backwards)
            conv.action_nav_prev_block()
            assert conv._selected_index == 2

    async def test_no_wrap_navigation_stays_at_boundary(self) -> None:
        """No-wrap navigation should stay at boundary."""
        async with ConversationTestApp(
            wrap_navigation=False, navigation_bell=False
        ).run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "A")
                conv.append("assistant", "B")

            await pilot.pause()

            # Select first
            conv.action_nav_next_block()
            assert conv._selected_index == 0

            # Try to go before first - should stay
            conv.action_nav_prev_block()
            assert conv._selected_index == 0

            # Navigate to last
            conv.action_nav_next_block()
            assert conv._selected_index == 1

            # Try to go past last - should stay
            conv.action_nav_next_block()
            assert conv._selected_index == 1

    async def test_selection_visual_update(self) -> None:
        """Selection should trigger visual update."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Hello")

            await pilot.pause()

            # Set width to enable rendering
            conv._last_width = 80

            # Select block - should update visuals
            conv.action_nav_next_block()

            # Check that selected_block_info returns correct info
            info = conv.selected_block_info
            assert info is not None
            assert info.content == "Hello"
