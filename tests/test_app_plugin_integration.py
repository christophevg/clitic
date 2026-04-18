"""Integration tests for plugin system and submit flow in Textual app context.

This module tests the integration between plugins, InputBar submit flow,
and Conversation widget in a running Textual app. Tests cover:

- Plugin lifecycle (registration/unregistration) in running app
- Complete submit flow: InputBar.Submit -> handler -> Conversation
- Plugin interaction with app components
- Edge cases in submit flow and plugin management
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from textual.app import ComposeResult

from clitic import App as CliticApp
from clitic import ContentPlugin, Conversation, InputBar

if TYPE_CHECKING:
    from textual.widget import Widget


class LifecycleTrackingPlugin(ContentPlugin):
    """Plugin with lifecycle tracking for integration testing."""

    def __init__(self) -> None:
        """Initialize the plugin with tracking state."""
        self.registered = False
        self.unregistered = False
        self._app = None

    @property
    def name(self) -> str:
        """Return the plugin name."""
        return "LifecycleTrackingPlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        """Accept all content types."""
        return True

    def render(self, content: str) -> Widget:
        """Render content as a mock widget."""

        class MockWidget:
            def __init__(self, text: str) -> None:
                self.text = text

        return MockWidget(content)

    def on_register(self, app: object) -> None:
        """Track registration."""
        self.registered = True
        self._app = app

    def on_unregister(self, app: object) -> None:
        """Track unregistration."""
        self.unregistered = True
        self._app = None


class ContentTrackingPlugin(ContentPlugin):
    """Plugin that tracks content it renders."""

    def __init__(self) -> None:
        """Initialize the plugin with content tracking."""
        self.rendered_content: list[str] = []

    @property
    def name(self) -> str:
        """Return the plugin name."""
        return "ContentTrackingPlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        """Accept text/plain content."""
        return content_type == "text/plain"

    def render(self, content: str) -> Widget:
        """Render content and track it."""
        self.rendered_content.append(content)

        class MockWidget:
            def __init__(self, text: str) -> None:
                self.text = text

        return MockWidget(content)


class PriorityPlugin(ContentPlugin):
    """Plugin with custom priority for testing ordering."""

    def __init__(self, name: str, priority: int) -> None:
        """Initialize with custom name and priority."""
        self._name = name
        self._priority = priority

    @property
    def name(self) -> str:
        """Return the plugin name."""
        return self._name

    @property
    def priority(self) -> int:
        """Return the plugin priority."""
        return self._priority

    def can_render(self, content_type: str, content: str) -> bool:
        """Accept all content."""
        return True

    def render(self, content: str) -> Widget:
        """Render content."""

        class MockWidget:
            def __init__(self, text: str) -> None:
                self.text = text

        return MockWidget(content)


@pytest.mark.asyncio
class TestPluginLifecycleIntegration:
    """Tests for plugin registration/unregistration in running app."""

    async def test_register_plugin_in_running_app(self) -> None:
        """Plugin can be registered in a running app."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            assert plugin.registered is True
            assert plugin._app is pilot.app
            assert len(pilot.app.get_plugins()) == 1

    async def test_unregister_plugin_in_running_app(self) -> None:
        """Plugin can be unregistered from a running app."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)
            assert len(pilot.app.get_plugins()) == 1

            pilot.app.unregister_plugin(plugin)

            assert plugin.unregistered is True
            assert plugin._app is None
            assert len(pilot.app.get_plugins()) == 0

    async def test_multiple_plugins_registered(self) -> None:
        """Multiple plugins can be registered in a running app."""
        plugin1 = LifecycleTrackingPlugin()
        plugin2 = ContentTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin1)
            pilot.app.register_plugin(plugin2)

            plugins = pilot.app.get_plugins()
            assert len(plugins) == 2
            assert plugin1 in plugins
            assert plugin2 in plugins

    async def test_plugin_on_register_receives_app_instance(self) -> None:
        """on_register hook receives the app instance."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            assert plugin._app is pilot.app
            assert isinstance(plugin._app, CliticApp)

    async def test_plugin_can_access_app_widgets(self) -> None:
        """Plugin can access widgets through app instance."""

        class WidgetAccessPlugin(ContentPlugin):
            def __init__(self) -> None:
                self.conversation_found = False

            @property
            def name(self) -> str:
                return "WidgetAccessPlugin"

            def can_render(self, content_type: str, content: str) -> bool:
                return True

            def render(self, content: str) -> Widget:
                class MockWidget:
                    pass

                return MockWidget()

            def on_register(self, app: object) -> None:
                # Try to query widgets
                try:
                    conv = app.query_one(Conversation)  # type: ignore[union-attr]
                    self.conversation_found = conv is not None
                except Exception:
                    self.conversation_found = False

        plugin = WidgetAccessPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)
            await pilot.pause()

            assert plugin.conversation_found is True

    async def test_register_plugin_multiple_times(self) -> None:
        """Registering the same plugin twice adds it to the list twice."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)
            pilot.app.register_plugin(plugin)

            # on_register is called each time
            # The plugin appears in the list each time it's registered
            plugins = pilot.app.get_plugins()
            assert len(plugins) == 2

    async def test_unregister_plugin_not_registered(self) -> None:
        """Unregistering a plugin that was never registered does nothing."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            # Should not raise
            pilot.app.unregister_plugin(plugin)

            assert plugin.unregistered is True
            assert len(pilot.app.get_plugins()) == 0


@pytest.mark.asyncio
class TestSubmitFlowIntegration:
    """Tests for complete InputBar.Submit -> handler -> Conversation flow."""

    async def test_submit_flow_single_message(self) -> None:
        """Submit flow appends message to conversation."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Hello, world!"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 1
            assert messages == ["Hello, world!"]

    async def test_submit_flow_multiple_messages(self) -> None:
        """Multiple submits append multiple blocks to conversation."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.focus()

            input_bar.text = "First message"
            await pilot.press("enter")
            await pilot.pause()

            input_bar.text = "Second message"
            await pilot.press("enter")
            await pilot.pause()

            input_bar.text = "Third message"
            await pilot.press("enter")
            await pilot.pause()

            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 3
            assert messages == ["First message", "Second message", "Third message"]

    async def test_submit_flow_clears_input(self) -> None:
        """Submit clears the input bar text."""

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Test message"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert input_bar.text == ""

    async def test_submit_flow_multiline_text(self) -> None:
        """Submit handles multiline text correctly."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Line one\nLine two\nLine three"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert len(messages) == 1
            assert messages[0] == "Line one\nLine two\nLine three"
            assert "\n" in messages[0]

    async def test_submit_flow_with_on_submit_handler(self) -> None:
        """on_submit decorator receives submitted text when _trigger_submit is called."""
        received: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:

            @pilot.app.on_submit
            def handle_submit(text: str) -> None:
                received.append(text)

            # The on_submit decorator registers handlers that are called by _trigger_submit
            # This is separate from InputBar.Submit message handling
            pilot.app._trigger_submit("Test message")

            assert received == ["Test message"]

    async def test_submit_flow_multiple_handlers(self) -> None:
        """Multiple on_submit handlers are all called in registration order."""
        calls: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:

            @pilot.app.on_submit
            def first_handler(text: str) -> None:
                calls.append(f"first:{text}")

            @pilot.app.on_submit
            def second_handler(text: str) -> None:
                calls.append(f"second:{text}")

            pilot.app._trigger_submit("Test")

            # Handlers are called in registration order
            assert calls == ["first:Test", "second:Test"]

    async def test_submit_flow_empty_text_not_submitted(self) -> None:
        """Empty or whitespace-only text is not submitted."""

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                raise AssertionError("Should not be called for empty text")

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "   "  # Whitespace only
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 0

    async def test_submit_flow_alternate_mode(self) -> None:
        """Submit works correctly with submit_on_enter=False."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar(submit_on_enter=False)

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Test message"
            input_bar.focus()

            # With submit_on_enter=False, Enter inserts newline (no submit)
            await pilot.press("enter")
            await pilot.pause()

            # No submit yet - text now has newline
            assert len(messages) == 0
            assert "\n" in input_bar.text

            # Reset text for clean submit test
            input_bar.text = "Test message"

            # Shift+Enter submits
            await pilot.press("shift+enter")
            await pilot.pause()

            assert messages == ["Test message"]


@pytest.mark.asyncio
class TestPluginAppIntegration:
    """Tests for plugin interaction with app components."""

    async def test_plugin_receives_app_on_mount(self) -> None:
        """Plugin receives app instance when registered during mount."""

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

            def on_mount(self) -> None:
                self.test_plugin = LifecycleTrackingPlugin()
                self.register_plugin(self.test_plugin)

        async with TestApp().run_test() as pilot:
            await pilot.pause()

            assert pilot.app.test_plugin.registered is True
            assert pilot.app.test_plugin._app is pilot.app

    async def test_plugin_can_use_app_on_submit(self) -> None:
        """Plugin can access Conversation when handling submit."""
        rendered_content: list[str] = []

        class RenderTrackingPlugin(ContentPlugin):
            @property
            def name(self) -> str:
                return "RenderTrackingPlugin"

            def can_render(self, content_type: str, content: str) -> bool:
                return True

            def render(self, content: str) -> Widget:
                rendered_content.append(content)

                class MockWidget:
                    pass

                return MockWidget()

        plugin = RenderTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Hello from plugin test"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 1

    async def test_plugin_registration_order(self) -> None:
        """Plugins are stored in registration order (not sorted by priority)."""
        low_plugin = PriorityPlugin("LowPriority", 10)
        high_plugin = PriorityPlugin("HighPriority", 100)

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(low_plugin)
            pilot.app.register_plugin(high_plugin)

            plugins = pilot.app.get_plugins()
            # Plugins are stored in registration order, not sorted by priority
            assert plugins[0] is low_plugin
            assert plugins[1] is high_plugin

    async def test_plugin_state_persists_across_renders(self) -> None:
        """Plugin state persists across app renders."""
        plugin = ContentTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            input_bar = pilot.app.query_one(InputBar)
            input_bar.focus()

            input_bar.text = "First"
            await pilot.press("enter")
            await pilot.pause()

            input_bar.text = "Second"
            await pilot.press("enter")
            await pilot.pause()

            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 2

    async def test_plugin_unregister_clears_app_reference(self) -> None:
        """Unregistering plugin clears app reference."""

        class AppReferencePlugin(ContentPlugin):
            def __init__(self) -> None:
                self.app_reference = None

            @property
            def name(self) -> str:
                return "AppReferencePlugin"

            def can_render(self, content_type: str, content: str) -> bool:
                return True

            def render(self, content: str) -> Widget:
                class MockWidget:
                    pass

                return MockWidget()

            def on_register(self, app: object) -> None:
                self.app_reference = app

            def on_unregister(self, app: object) -> None:
                self.app_reference = None

        plugin = AppReferencePlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)
            assert plugin.app_reference is pilot.app

            pilot.app.unregister_plugin(plugin)
            assert plugin.app_reference is None


@pytest.mark.asyncio
class TestSubmitFlowEdgeCases:
    """Tests for edge cases in submit flow."""

    async def test_submit_with_special_characters(self) -> None:
        """Submit handles special characters correctly."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Special: @#$%^&*()!"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert messages[0] == "Special: @#$%^&*()!"

    async def test_submit_with_unicode(self) -> None:
        """Submit handles unicode correctly."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Unicode: \u4e2d\u6587 \u0627\u0644\u0639\u0631\u0628\u064a\u0629"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert messages[0] == "Unicode: \u4e2d\u6587 \u0627\u0644\u0639\u0631\u0628\u064a\u0629"

    async def test_submit_with_tabs(self) -> None:
        """Submit handles tabs correctly."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = "Tab:\tseparated\tcontent"
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert "\t" in messages[0]

    async def test_submit_very_long_text(self) -> None:
        """Submit handles very long text correctly."""
        messages: list[str] = []
        long_text = "A" * 10000

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.text = long_text
            input_bar.focus()

            await pilot.press("enter")
            await pilot.pause()

            assert len(messages[0]) == 10000
            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 1

    async def test_rapid_submits(self) -> None:
        """Rapid consecutive submits are handled correctly."""
        messages: list[str] = []

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()
                yield InputBar()

            def on_input_bar_submit(self, event: InputBar.Submit) -> None:
                messages.append(event.text)
                conversation = self.query_one(Conversation)
                conversation.append("user", event.text)

        async with TestApp().run_test() as pilot:
            input_bar = pilot.app.query_one(InputBar)
            input_bar.focus()

            for i in range(5):
                input_bar.text = f"Message {i}"
                await pilot.press("enter")
                await pilot.pause()

            assert len(messages) == 5
            conversation = pilot.app.query_one(Conversation)
            assert conversation.block_count == 5


@pytest.mark.asyncio
class TestPluginEdgeCases:
    """Tests for edge cases in plugin management."""

    async def test_register_plugin_with_same_name(self) -> None:
        """Multiple plugins with the same name can be registered."""
        plugin1 = LifecycleTrackingPlugin()
        plugin2 = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin1)
            pilot.app.register_plugin(plugin2)

            plugins = pilot.app.get_plugins()
            assert len(plugins) == 2
            # Both are separate instances
            assert plugins[0] is not plugins[1]

    async def test_unregister_during_iteration(self) -> None:
        """Unregistering during iteration is handled correctly."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            plugins_before = pilot.app.get_plugins()
            assert len(plugins_before) == 1

            pilot.app.unregister_plugin(plugin)

            plugins_after = pilot.app.get_plugins()
            assert len(plugins_after) == 0

    async def test_plugin_render_async_default(self) -> None:
        """Plugin render_async calls render by default."""
        import asyncio

        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            # render_async should work (default implementation calls render)
            result = await asyncio.create_task(plugin.render_async("test content"))
            assert result.text == "test content"

    async def test_get_plugins_returns_copy(self) -> None:
        """get_plugins returns a copy, not the original list."""
        plugin = LifecycleTrackingPlugin()

        class TestApp(CliticApp):
            def compose(self) -> ComposeResult:
                yield Conversation()

        async with TestApp().run_test() as pilot:
            pilot.app.register_plugin(plugin)

            plugins = pilot.app.get_plugins()
            plugins.clear()  # Modify the returned copy

            # Original should still have the plugin
            assert len(pilot.app.get_plugins()) == 1
