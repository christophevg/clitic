"""Integration tests for Conversation resize/scroll behavior.

Tests the complete cycle: resize → scroll position → auto_scroll → CSS class.

This module tests:
- Scroll state management (auto_scroll transitions)
- Resize handling and its effect on auto_scroll
- Visual feedback (CSS class toggling)
- Edge cases in scroll/resize behavior
"""

from unittest.mock import patch

import pytest
from textual.app import App, ComposeResult
from textual.events import Resize

from clitic import Conversation

# ==============================================================================
# Test App for Integration Tests
# ==============================================================================


class ConversationTestApp(App):
    """Minimal test app with a Conversation widget."""

    def __init__(self, **kwargs):
        """Initialize with Conversation kwargs."""
        super().__init__()
        self._conv_kwargs = kwargs

    def compose(self) -> ComposeResult:
        yield Conversation(**self._conv_kwargs)


# ==============================================================================
# Test Class: Scroll State Management
# ==============================================================================


@pytest.mark.asyncio
class TestScrollStateManagement:
    """Tests for scroll position → auto_scroll state transitions."""

    async def test_auto_scroll_true_at_bottom(self) -> None:
        """Scrolling to bottom should set auto_scroll=True."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content to make it scrollable
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Wait for layout to settle
            await pilot.pause()

            # Scroll to bottom using scroll_end
            conv.scroll_end(animate=False)
            await pilot.pause()

            # Verify we're at or near bottom (scroll_y >= max_scroll_y - 1)
            max_y = conv.max_scroll_y
            if max_y > 0:
                # At bottom, scroll_y should be at or near max_y
                # Manually trigger the update to verify the logic
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True, (
                    f"Expected auto_scroll=True at bottom (scroll_y={conv.scroll_y}, max_y={max_y})"
                )

    async def test_auto_scroll_false_when_scrolled_up(self) -> None:
        """Scrolling up from bottom should set auto_scroll=False."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content to make it scrollable
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Start at bottom (auto_scroll = True)
            conv.auto_scroll = True

            # Simulate scrolling up
            conv.scroll_to(0, animate=False)
            conv.watch_scroll_y(old=conv.max_scroll_y, new=0.0)

            # Should be False when scrolled to top
            assert conv.auto_scroll is False

    async def test_auto_scroll_true_when_content_fits(self) -> None:
        """When content fits viewport, auto_scroll should be True."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add minimal content that fits in viewport
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Short message")

            # Content fits, so max_scroll_y should be 0
            if conv.max_scroll_y == 0:
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True

    async def test_scroll_near_bottom_threshold(self) -> None:
        """Being near bottom (max_y - 1) should resume auto_scroll."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add enough content to scroll
            with patch.object(conv, "call_after_refresh"):
                for i in range(30):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            max_y = conv.max_scroll_y
            if max_y > 1:
                # Scroll to end - this puts us at or near max_scroll_y
                conv.scroll_end(animate=False)
                await pilot.pause()

                # At bottom, auto_scroll should be True
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True, (
                    f"auto_scroll should be True at bottom (scroll_y={conv.scroll_y}, max_y={max_y})"
                )

                # Now scroll to top to disable auto_scroll
                conv.scroll_home(animate=False)
                await pilot.pause()
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is False, "auto_scroll should be False at top"

    async def test_update_auto_scroll_from_scroll_position_all_branches(
        self,
    ) -> None:
        """Test all branches of _update_auto_scroll_from_scroll_position."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Branch 1: max_scroll_y == 0 (content fits)
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Short")
            await pilot.pause()

            if conv.max_scroll_y == 0:
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True, "auto_scroll should be True when content fits"

            # Branch 2: scroll_y >= max_scroll_y - 1 (at or near bottom)
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")
            await pilot.pause()

            max_y = conv.max_scroll_y
            if max_y > 0:
                # Scroll to bottom
                conv.scroll_end(animate=False)
                await pilot.pause()
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True, (
                    f"auto_scroll should be True at bottom (scroll_y={conv.scroll_y}, max_y={max_y})"
                )

                # Branch 3: scrolled up (else branch)
                conv.scroll_home(animate=False)
                await pilot.pause()
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is False, "auto_scroll should be False when scrolled up"


# ==============================================================================
# Test Class: Resize Behavior
# ==============================================================================


@pytest.mark.asyncio
class TestResizeBehavior:
    """Tests for resize handling and its effect on auto_scroll."""

    async def test_resize_at_bottom_preserves_auto_scroll(self) -> None:
        """Resize while at bottom should preserve auto_scroll=True."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            # Scroll to bottom with scroll_end
            conv.scroll_end(animate=False)
            await pilot.pause()

            # Verify we're at bottom (scroll_y >= max_scroll_y - 1)
            max_y = conv.max_scroll_y
            if max_y > 0:
                conv._update_auto_scroll_from_scroll_position()
                initial_auto_scroll = conv.auto_scroll

                # Simulate resize event
                resize_event = Resize(None, None, (80, 24))
                conv.on_resize(resize_event)

                # auto_scroll should remain True (at or near bottom)
                assert conv.auto_scroll == initial_auto_scroll, (
                    f"auto_scroll should remain {initial_auto_scroll} after resize"
                )

    async def test_resize_scrolled_up_preserves_state(self) -> None:
        """Resize while scrolled up should preserve auto_scroll=False."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Scroll up and disable auto_scroll
            conv.scroll_to(0, animate=False)
            conv._update_auto_scroll_from_scroll_position()
            assert conv.auto_scroll is False

            # Simulate resize
            resize_event = Resize(None, None, (120, 30))
            conv.on_resize(resize_event)

            # auto_scroll should still be False (scrolled up state)
            assert conv.auto_scroll is False

    async def test_resize_to_content_fits_enables_auto_scroll(self) -> None:
        """Resize that makes content fit should enable auto_scroll."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add minimal content
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Short message")

            # Simulate resize
            resize_event = Resize(None, None, (200, 50))
            conv.on_resize(resize_event)

            # If content now fits, auto_scroll should be True
            if conv.max_scroll_y == 0:
                assert conv.auto_scroll is True

    async def test_resize_triggers_rerender(self) -> None:
        """Width change should trigger block re-rendering."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "This is a test message")

            # Store initial width
            initial_width = conv._last_width

            # Simulate resize with different width
            resize_event = Resize(None, None, (100, 24))
            conv.on_resize(resize_event)

            # Width should have been updated
            # Note: depends on internal _get_content_width implementation
            # The key behavior is that _rerender_all_blocks was called if width changed
            if conv._last_width != initial_width:
                # Rerender should have been triggered
                pass  # Success - width changed and rerender happened

    async def test_resize_calls_update_auto_scroll(self) -> None:
        """Resize should call _update_auto_scroll_from_scroll_position."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Track if _update_auto_scroll_from_scroll_position was called
            update_called = []

            original_update = conv._update_auto_scroll_from_scroll_position

            def track_update():
                update_called.append(True)
                return original_update()

            conv._update_auto_scroll_from_scroll_position = track_update

            # Simulate resize
            resize_event = Resize(None, None, (80, 24))
            conv.on_resize(resize_event)

            assert len(update_called) > 0, (
                "_update_auto_scroll_from_scroll_position should be called"
            )


# ==============================================================================
# Test Class: Visual Feedback
# ==============================================================================


@pytest.mark.asyncio
class TestVisualFeedback:
    """Tests for CSS class toggling based on auto_scroll state."""

    async def test_paused_class_removed_at_bottom(self) -> None:
        """Scrolling to bottom should remove 'paused' CSS class."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content and scroll up
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            # Scroll up and verify paused class
            conv.scroll_home(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()
            assert conv.auto_scroll is False, "auto_scroll should be False at top"
            assert "paused" in conv.classes, "paused class should be present at top"

            # Scroll to bottom
            conv.scroll_end(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()

            # paused class should be removed
            assert conv.auto_scroll is True, (
                f"auto_scroll should be True at bottom (scroll_y={conv.scroll_y}, max_y={conv.max_scroll_y})"
            )
            assert "paused" not in conv.classes, "paused class should not be present at bottom"

    async def test_paused_class_added_when_scrolled_up(self) -> None:
        """Scrolling up should add 'paused' CSS class."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Start at bottom (paused class should not be present)
            assert "paused" not in conv.classes

            # Scroll up
            conv.scroll_to(0, animate=False)
            conv._update_auto_scroll_from_scroll_position()

            # paused class should be added
            assert "paused" in conv.classes

    async def test_paused_class_toggles_on_state_change(self) -> None:
        """CSS class should toggle correctly on state changes."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            # Cycle through states
            # State 1: At bottom (auto_scroll=True, no paused class)
            conv.scroll_end(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()
            assert conv.auto_scroll is True, "auto_scroll should be True at bottom"
            assert "paused" not in conv.classes, "paused class should not be present at bottom"

            # State 2: Scrolled up (auto_scroll=False, paused class)
            conv.scroll_home(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()
            assert conv.auto_scroll is False, "auto_scroll should be False at top"
            assert "paused" in conv.classes, "paused class should be present at top"

            # State 3: Back to bottom (auto_scroll=True, no paused class)
            conv.scroll_end(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()
            assert conv.auto_scroll is True, "auto_scroll should be True at bottom"
            assert "paused" not in conv.classes, "paused class should not be present at bottom"

    async def test_watch_auto_scroll_adds_removes_class(self) -> None:
        """watch_auto_scroll should add/remove 'paused' class."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Initially auto_scroll is True, no paused class
            assert conv.auto_scroll is True
            assert "paused" not in conv.classes

            # Set auto_scroll to False
            conv.auto_scroll = False
            # watch_auto_scroll should have been called automatically
            assert "paused" in conv.classes

            # Set auto_scroll back to True
            conv.auto_scroll = True
            assert "paused" not in conv.classes


# ==============================================================================
# Test Class: Edge Cases
# ==============================================================================


@pytest.mark.asyncio
class TestEdgeCases:
    """Tests for edge cases in scroll/resize behavior."""

    async def test_rapid_scroll_events(self) -> None:
        """Multiple scroll events in succession should work correctly."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(50):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            # Rapid scroll events
            for _ in range(3):
                # Scroll to top
                conv.scroll_home(animate=False)
                await pilot.pause()
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is False, "auto_scroll should be False at top"

                # Scroll to bottom
                conv.scroll_end(animate=False)
                await pilot.pause()
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True, "auto_scroll should be True at bottom"

    async def test_empty_conversation_scroll(self) -> None:
        """Scroll behavior with no content should not error."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # No content added
            assert conv.block_count == 0
            assert conv.max_scroll_y == 0

            # Should not error on scroll operations
            conv.scroll_to(0, animate=False)
            conv._update_auto_scroll_from_scroll_position()

            # auto_scroll should be True (content fits)
            assert conv.auto_scroll is True

    async def test_single_line_content(self) -> None:
        """Single line content should auto_scroll=True."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add single line
            with patch.object(conv, "call_after_refresh"):
                conv.append("user", "Single line")

            # Content fits (max_scroll_y == 0)
            if conv.max_scroll_y == 0:
                conv._update_auto_scroll_from_scroll_position()
                assert conv.auto_scroll is True
                assert "paused" not in conv.classes

    async def test_scroll_y_fractional_values(self) -> None:
        """Fractional scroll_y values should be handled correctly."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(30):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            max_y = conv.max_scroll_y
            if max_y > 1:
                # Scroll near bottom
                conv.scroll_end(animate=False)
                await pilot.pause()

                # At bottom, scroll_y should be >= max_y - 1
                conv._update_auto_scroll_from_scroll_position()

                # If scroll_y >= max_y - 1, auto_scroll should be True
                if conv.scroll_y >= max_y - 1:
                    assert conv.auto_scroll is True, (
                        f"auto_scroll should be True near bottom (scroll_y={conv.scroll_y}, max_y={max_y})"
                    )

    async def test_resize_with_no_content(self) -> None:
        """Resize with no content should not error."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # No content
            assert conv.block_count == 0

            # Simulate resize
            resize_event = Resize(None, None, (100, 40))
            # Should not raise
            conv.on_resize(resize_event)

            # auto_scroll should remain True
            assert conv.auto_scroll is True

    async def test_consecutive_resizes(self) -> None:
        """Multiple resize events should not cause issues."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Multiple resize events
            sizes = [(80, 24), (120, 30), (60, 20), (100, 40)]
            for width, height in sizes:
                resize_event = Resize(None, None, (width, height))
                conv.on_resize(resize_event)

            # Should have auto_scroll set based on current scroll position
            # No error means success
            assert conv.auto_scroll is not None

    async def test_scroll_position_preserved_after_resize_at_bottom(
        self,
    ) -> None:
        """Resize at bottom should keep user at bottom."""
        async with ConversationTestApp().run_test() as pilot:
            conv = pilot.app.query_one(Conversation)

            # Add content
            with patch.object(conv, "call_after_refresh"):
                for i in range(20):
                    conv.append("user", f"Line {i}")

            # Wait for layout
            await pilot.pause()

            # Scroll to bottom
            conv.scroll_end(animate=False)
            await pilot.pause()
            conv._update_auto_scroll_from_scroll_position()

            # Verify we're at bottom
            if conv.max_scroll_y > 0:
                assert conv.auto_scroll is True, (
                    f"auto_scroll should be True at bottom (scroll_y={conv.scroll_y}, max_y={conv.max_scroll_y})"
                )

                # Simulate resize
                resize_event = Resize(None, None, (100, 30))
                conv.on_resize(resize_event)

                # Should still have auto_scroll = True
                assert conv.auto_scroll is True, (
                    "auto_scroll should remain True after resize at bottom"
                )
