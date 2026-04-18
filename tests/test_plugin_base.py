"""Tests for clitic plugin base classes."""

import pytest

from clitic.plugins import ContentPlugin, Highlighter, ModeProvider, Renderable


class TestRenderableProtocol:
    """Tests for the Renderable protocol."""

    def test_string_is_renderable(self) -> None:
        """Strings should satisfy the Renderable protocol."""
        text: Renderable = "hello"
        assert str(text) == "hello"

    def test_custom_class_can_be_renderable(self) -> None:
        """Custom classes with __str__ should work as Renderable."""

        class CustomContent:
            def __str__(self) -> str:
                return "custom content"

        content: Renderable = CustomContent()
        assert str(content) == "custom content"


class TestHighlighterProtocol:
    """Tests for the Highlighter protocol."""

    def test_highlighter_protocol(self) -> None:
        """Highlighter should have a highlight method."""

        class SimpleHighlighter:
            def highlight(self, text: str) -> str:
                return f"[bold]{text}[/bold]"

        highlighter: Highlighter = SimpleHighlighter()
        result = highlighter.highlight("test")
        assert "[bold]test[/bold]" == result


class ConcreteContentPlugin(ContentPlugin):
    """Concrete implementation of ContentPlugin for testing."""

    @property
    def name(self) -> str:
        return "TestPlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        return content_type == "text/plain"

    def render(self, content: str) -> object:
        # Return a mock widget
        class MockWidget:
            def __init__(self, content: str) -> None:
                self.content = content

        return MockWidget(content)


class CustomPriorityPlugin(ContentPlugin):
    """Plugin with custom priority for testing."""

    @property
    def name(self) -> str:
        return "HighPriorityPlugin"

    @property
    def priority(self) -> int:
        return 100

    def can_render(self, content_type: str, content: str) -> bool:
        return True

    def render(self, content: str) -> object:
        return object()


class TestContentPlugin:
    """Tests for the ContentPlugin abstract base class."""

    def test_cannot_instantiate_abc(self) -> None:
        """ContentPlugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ContentPlugin()  # type: ignore[abstract]

    def test_must_implement_name(self) -> None:
        """Subclasses must implement name property."""

        class IncompletePlugin(ContentPlugin):
            def can_render(self, content_type: str, content: str) -> bool:
                return False

            def render(self, content: str) -> object:
                return object()

        with pytest.raises(TypeError):
            IncompletePlugin()  # type: ignore[abstract]

    def test_must_implement_can_render(self) -> None:
        """Subclasses must implement can_render method."""

        class IncompletePlugin(ContentPlugin):
            @property
            def name(self) -> str:
                return "Incomplete"

            def render(self, content: str) -> object:
                return object()

        with pytest.raises(TypeError):
            IncompletePlugin()  # type: ignore[abstract]

    def test_must_implement_render(self) -> None:
        """Subclasses must implement render method."""

        class IncompletePlugin(ContentPlugin):
            @property
            def name(self) -> str:
                return "Incomplete"

            def can_render(self, content_type: str, content: str) -> bool:
                return False

        with pytest.raises(TypeError):
            IncompletePlugin()  # type: ignore[abstract]

    def test_concrete_implementation_works(self) -> None:
        """Concrete implementation can be instantiated."""
        plugin = ConcreteContentPlugin()
        assert plugin.name == "TestPlugin"

    def test_default_priority_is_zero(self) -> None:
        """Default priority should be 0."""
        plugin = ConcreteContentPlugin()
        assert plugin.priority == 0

    def test_custom_priority(self) -> None:
        """Custom priority can be set."""
        plugin = CustomPriorityPlugin()
        assert plugin.priority == 100

    def test_render_returns_widget(self) -> None:
        """render should return a widget-like object."""
        plugin = ConcreteContentPlugin()
        widget = plugin.render("test content")
        assert hasattr(widget, "content")
        assert widget.content == "test content"

    def test_can_render_returns_bool(self) -> None:
        """can_render should return boolean."""
        plugin = ConcreteContentPlugin()
        assert plugin.can_render("text/plain", "hello") is True
        assert plugin.can_render("text/html", "hello") is False

    def test_render_async_default_impl(self) -> None:
        """render_async should call render by default."""
        import asyncio

        plugin = ConcreteContentPlugin()
        widget = asyncio.run(plugin.render_async("test"))
        assert hasattr(widget, "content")
        assert widget.content == "test"

    def test_on_register_default_impl(self) -> None:
        """on_register should have empty default implementation."""
        plugin = ConcreteContentPlugin()
        # Should not raise
        plugin.on_register(None)  # type: ignore[arg-type]

    def test_on_unregister_default_impl(self) -> None:
        """on_unregister should have empty default implementation."""
        plugin = ConcreteContentPlugin()
        # Should not raise
        plugin.on_unregister(None)  # type: ignore[arg-type]


class AsyncRenderPlugin(ContentPlugin):
    """Plugin with async rendering for testing."""

    @property
    def name(self) -> str:
        return "AsyncPlugin"

    async def render_async(self, content: str) -> object:
        """Custom async implementation."""
        return object()

    def can_render(self, content_type: str, content: str) -> bool:
        return True

    def render(self, content: str) -> object:
        return object()


class TestContentPluginAsync:
    """Tests for ContentPlugin async functionality."""

    def test_render_async_can_be_overridden(self) -> None:
        """render_async can be overridden in subclasses."""
        import asyncio

        plugin = AsyncRenderPlugin()
        result = asyncio.run(plugin.render_async("test"))
        assert result is not None


class LifecyclePlugin(ContentPlugin):
    """Plugin with lifecycle hooks for testing."""

    def __init__(self) -> None:
        self.registered = False
        self.unregistered = False
        self._app = None

    @property
    def name(self) -> str:
        return "LifecyclePlugin"

    def can_render(self, content_type: str, content: str) -> bool:
        return True

    def render(self, content: str) -> object:
        return object()

    def on_register(self, app: object) -> None:
        self.registered = True
        self._app = app

    def on_unregister(self, app: object) -> None:
        self.unregistered = True
        self._app = None


class TestContentPluginLifecycle:
    """Tests for ContentPlugin lifecycle hooks."""

    def test_on_register_receives_app(self) -> None:
        """on_register should receive the app instance."""
        plugin = LifecyclePlugin()

        class MockApp:
            pass

        app = MockApp()
        plugin.on_register(app)

        assert plugin.registered is True
        assert plugin._app is app

    def test_on_unregister_receives_app(self) -> None:
        """on_unregister should receive the app instance."""
        plugin = LifecyclePlugin()

        class MockApp:
            pass

        app = MockApp()
        plugin.on_register(app)
        plugin.on_unregister(app)

        assert plugin.unregistered is True
        assert plugin._app is None


class ConcreteModeProvider(ModeProvider):
    """Concrete implementation of ModeProvider for testing."""

    @property
    def name(self) -> str:
        return "TestMode"

    @property
    def indicator(self) -> str:
        return "[T]"

    def detect(self, text: str, cursor_position: int) -> bool:
        return text.startswith("test:")

    def get_highlighter(self) -> object | None:
        return None


class CustomPriorityModeProvider(ModeProvider):
    """Mode provider with custom priority for testing."""

    @property
    def name(self) -> str:
        return "HighPriorityMode"

    @property
    def indicator(self) -> str:
        return "[HP]"

    @property
    def priority(self) -> int:
        return 50

    def detect(self, text: str, cursor_position: int) -> bool:
        return True

    def get_highlighter(self) -> object | None:
        return None


class TestModeProvider:
    """Tests for the ModeProvider abstract base class."""

    def test_cannot_instantiate_abc(self) -> None:
        """ModeProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ModeProvider()  # type: ignore[abstract]

    def test_must_implement_name(self) -> None:
        """Subclasses must implement name property."""

        class IncompleteMode(ModeProvider):
            @property
            def indicator(self) -> str:
                return ""

            def detect(self, text: str, cursor_position: int) -> bool:
                return False

            def get_highlighter(self) -> object | None:
                return None

        with pytest.raises(TypeError):
            IncompleteMode()  # type: ignore[abstract]

    def test_must_implement_indicator(self) -> None:
        """Subclasses must implement indicator property."""

        class IncompleteMode(ModeProvider):
            @property
            def name(self) -> str:
                return "Incomplete"

            def detect(self, text: str, cursor_position: int) -> bool:
                return False

            def get_highlighter(self) -> object | None:
                return None

        with pytest.raises(TypeError):
            IncompleteMode()  # type: ignore[abstract]

    def test_must_implement_detect(self) -> None:
        """Subclasses must implement detect method."""

        class IncompleteMode(ModeProvider):
            @property
            def name(self) -> str:
                return "Incomplete"

            @property
            def indicator(self) -> str:
                return ""

            def get_highlighter(self) -> object | None:
                return None

        with pytest.raises(TypeError):
            IncompleteMode()  # type: ignore[abstract]

    def test_must_implement_get_highlighter(self) -> None:
        """Subclasses must implement get_highlighter method."""

        class IncompleteMode(ModeProvider):
            @property
            def name(self) -> str:
                return "Incomplete"

            @property
            def indicator(self) -> str:
                return ""

            def detect(self, text: str, cursor_position: int) -> bool:
                return False

        with pytest.raises(TypeError):
            IncompleteMode()  # type: ignore[abstract]

    def test_concrete_implementation_works(self) -> None:
        """Concrete implementation can be instantiated."""
        provider = ConcreteModeProvider()
        assert provider.name == "TestMode"
        assert provider.indicator == "[T]"

    def test_default_priority_is_zero(self) -> None:
        """Default priority should be 0."""
        provider = ConcreteModeProvider()
        assert provider.priority == 0

    def test_custom_priority(self) -> None:
        """Custom priority can be set."""
        provider = CustomPriorityModeProvider()
        assert provider.priority == 50

    def test_detect_returns_bool(self) -> None:
        """detect should return boolean."""
        provider = ConcreteModeProvider()
        assert provider.detect("test: hello", 0) is True
        assert provider.detect("hello", 0) is False

    def test_get_highlighter_returns_optional(self) -> None:
        """get_highlighter should return Highlighter or None."""
        provider = ConcreteModeProvider()
        result = provider.get_highlighter()
        assert result is None

    def test_on_enter_default_impl(self) -> None:
        """on_enter should return text unchanged by default."""
        provider = ConcreteModeProvider()
        result = provider.on_enter("test input")
        assert result == "test input"

    def test_on_exit_default_impl(self) -> None:
        """on_exit should return text unchanged by default."""
        provider = ConcreteModeProvider()
        result = provider.on_exit("test input")
        assert result == "test input"


class TransformModeProvider(ModeProvider):
    """Mode provider with text transformation for testing."""

    @property
    def name(self) -> str:
        return "TransformMode"

    @property
    def indicator(self) -> str:
        return "[X]"

    def detect(self, text: str, cursor_position: int) -> bool:
        return True

    def get_highlighter(self) -> object | None:
        return None

    def on_enter(self, text: str) -> str:
        return text.upper()

    def on_exit(self, text: str) -> str:
        return text.lower()


class TestModeProviderLifecycle:
    """Tests for ModeProvider lifecycle hooks."""

    def test_on_enter_transforms_text(self) -> None:
        """on_enter can transform text."""
        provider = TransformModeProvider()
        result = provider.on_enter("hello world")
        assert result == "HELLO WORLD"

    def test_on_exit_transforms_text(self) -> None:
        """on_exit can transform text."""
        provider = TransformModeProvider()
        result = provider.on_exit("HELLO WORLD")
        assert result == "hello world"

    def test_on_enter_receives_correct_text(self) -> None:
        """on_enter should receive the input text."""
        received: list[str] = []

        class CapturingMode(ModeProvider):
            @property
            def name(self) -> str:
                return "Capture"

            @property
            def indicator(self) -> str:
                return ""

            def detect(self, text: str, cursor_position: int) -> bool:
                return True

            def get_highlighter(self) -> object | None:
                return None

            def on_enter(self, text: str) -> str:
                received.append(text)
                return text

        provider = CapturingMode()
        provider.on_enter("test input")
        assert received == ["test input"]

    def test_on_exit_receives_correct_text(self) -> None:
        """on_exit should receive the input text."""
        received: list[str] = []

        class CapturingMode(ModeProvider):
            @property
            def name(self) -> str:
                return "Capture"

            @property
            def indicator(self) -> str:
                return ""

            def detect(self, text: str, cursor_position: int) -> bool:
                return True

            def get_highlighter(self) -> object | None:
                return None

            def on_exit(self, text: str) -> str:
                received.append(text)
                return text

        provider = CapturingMode()
        provider.on_exit("test output")
        assert received == ["test output"]


class ModeWithHighlighter(ModeProvider):
    """Mode provider with highlighter for testing."""

    @property
    def name(self) -> str:
        return "HighlighterMode"

    @property
    def indicator(self) -> str:
        return "[H]"

    def detect(self, text: str, cursor_position: int) -> bool:
        return True

    def get_highlighter(self) -> Highlighter:
        class SimpleHighlighter:
            def highlight(self, text: str) -> str:
                return f"[hl]{text}[/hl]"

        return SimpleHighlighter()


class TestModeProviderHighlighter:
    """Tests for ModeProvider highlighter functionality."""

    def test_get_highlighter_returns_highlighter(self) -> None:
        """get_highlighter can return a Highlighter instance."""
        provider = ModeWithHighlighter()
        highlighter = provider.get_highlighter()
        assert highlighter is not None

    def test_highlighter_highlights_text(self) -> None:
        """Returned highlighter should work correctly."""
        provider = ModeWithHighlighter()
        highlighter = provider.get_highlighter()
        assert highlighter is not None
        result = highlighter.highlight("test")
        assert result == "[hl]test[/hl]"
