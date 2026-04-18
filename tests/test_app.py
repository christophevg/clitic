"""Tests for clitic App class."""

from clitic import App
from clitic.plugins import ContentPlugin


class TestApp:
    """Tests for the App class."""

    def test_app_can_be_instantiated(self) -> None:
        """App should be instantiable."""
        app = App()
        assert app is not None

    def test_app_accepts_title_parameter(self) -> None:
        """App should accept a title parameter."""
        app = App(title="Test App")
        assert app.title == "Test App"

    def test_app_default_title(self) -> None:
        """App should have a default title."""
        app = App()
        assert app.title == "clitic"

    def test_app_accepts_theme_parameter(self) -> None:
        """App should accept a theme_name parameter."""
        app = App(theme_name="light")
        assert app.theme_name == "light"

    def test_app_default_theme_is_dark(self) -> None:
        """App should default to dark theme."""
        app = App()
        assert app.theme_name == "dark"

    def test_app_stores_theme_internally(self) -> None:
        """App should store theme internally."""
        app = App(title="Test", theme_name="custom")
        assert app._theme_name == "custom"


class TestAppPluginManagement:
    """Tests for App plugin management."""

    def test_register_plugin_works(self) -> None:
        """register_plugin should add plugin to registry."""
        app = App()
        plugin = SimpleTestPlugin()

        app.register_plugin(plugin)

        assert len(app.get_plugins()) == 1
        assert app.get_plugins()[0] is plugin

    def test_register_plugin_calls_on_register(self) -> None:
        """register_plugin should call on_register hook."""
        app = App()
        plugin = LifecycleTestPlugin()

        app.register_plugin(plugin)

        assert plugin.registered is True
        assert plugin._app is app

    def test_unregister_plugin_removes_from_registry(self) -> None:
        """unregister_plugin should remove plugin from registry."""
        app = App()
        plugin = SimpleTestPlugin()
        app.register_plugin(plugin)

        app.unregister_plugin(plugin)

        assert len(app.get_plugins()) == 0

    def test_unregister_plugin_calls_on_unregister(self) -> None:
        """unregister_plugin should call on_unregister hook."""
        app = App()
        plugin = LifecycleTestPlugin()
        app.register_plugin(plugin)

        app.unregister_plugin(plugin)

        assert plugin.unregistered is True

    def test_get_plugins_returns_copy(self) -> None:
        """get_plugins should return a copy of the plugins list."""
        app = App()
        plugin = SimpleTestPlugin()
        app.register_plugin(plugin)

        plugins = app.get_plugins()
        plugins.clear()

        assert len(app.get_plugins()) == 1

    def test_register_multiple_plugins(self) -> None:
        """App should support multiple plugins."""
        app = App()
        plugin1 = SimpleTestPlugin()
        plugin2 = SimpleTestPlugin()

        app.register_plugin(plugin1)
        app.register_plugin(plugin2)

        assert len(app.get_plugins()) == 2


class TestAppOnSubmit:
    """Tests for App on_submit decorator."""

    def test_on_submit_registers_handler(self) -> None:
        """on_submit should register a handler."""
        app = App()
        calls: list[str] = []

        @app.on_submit
        def handler(text: str) -> None:
            calls.append(text)

        app._trigger_submit("test input")

        assert calls == ["test input"]

    def test_on_submit_returns_handler(self) -> None:
        """on_submit should return the handler for chaining."""
        app = App()

        @app.on_submit
        def handler(text: str) -> str:
            return text.upper()

        result = handler("test")
        assert result == "TEST"

    def test_multiple_submit_handlers(self) -> None:
        """Multiple handlers should all be called."""
        app = App()
        calls: list[str] = []

        @app.on_submit
        def handler1(text: str) -> None:
            calls.append(f"1:{text}")

        @app.on_submit
        def handler2(text: str) -> None:
            calls.append(f"2:{text}")

        app._trigger_submit("hello")

        assert calls == ["1:hello", "2:hello"]

    def test_handlers_called_in_order(self) -> None:
        """Handlers should be called in registration order."""
        app = App()
        order: list[int] = []

        @app.on_submit
        def first(text: str) -> None:
            order.append(1)

        @app.on_submit
        def second(text: str) -> None:
            order.append(2)

        @app.on_submit
        def third(text: str) -> None:
            order.append(3)

        app._trigger_submit("test")

        assert order == [1, 2, 3]


class TestAppMinimalUsage:
    """Tests for minimal App usage."""

    def test_minimal_app_can_be_created(self) -> None:
        """A minimal app should be creatable."""
        app = App()
        assert app is not None

    def test_minimal_app_with_title(self) -> None:
        """A minimal app with custom title should work."""
        app = App(title="My App")
        assert app.title == "My App"

    def test_minimal_app_with_handler(self) -> None:
        """A minimal app with handler should be usable."""
        received: list[str] = []

        app = App(title="Test App")

        @app.on_submit
        def handle_input(text: str) -> None:
            received.append(text)

        app._trigger_submit("hello")

        assert received == ["hello"]


class SimpleTestPlugin(ContentPlugin):
    """Simple plugin implementation for testing."""

    @property
    def name(self) -> str:
        return "SimpleTestPlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        return True

    def render(self, content: str) -> object:
        class MockWidget:
            pass

        return MockWidget()


class LifecycleTestPlugin(ContentPlugin):
    """Plugin with lifecycle tracking for testing."""

    def __init__(self) -> None:
        self.registered = False
        self.unregistered = False
        self._app = None

    @property
    def name(self) -> str:
        return "LifecycleTestPlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        return True

    def render(self, content: str) -> object:
        class MockWidget:
            pass

        return MockWidget()

    def on_register(self, app: App) -> None:
        self.registered = True
        self._app = app

    def on_unregister(self, app: App) -> None:
        self.unregistered = True
        self._app = None
