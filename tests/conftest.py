"""Shared pytest fixtures for clitic tests.

This module provides comprehensive fixtures to reduce code duplication
across the test suite. Fixtures are organized by category:

- BlockInfo fixtures: Factory and preset instances for creating BlockInfo
- Conversation fixtures: Conversation instances with mocked methods
- InputBar fixtures: InputBar instances and message capture utilities
- Session fixtures: SessionManager and temporary session directory fixtures
- Plugin/Provider fixtures: Test implementations of ContentPlugin and ModeProvider
- Mock App fixtures: Factory for creating minimal Textual App instances
- Utility fixtures: Timestamps, timing, and memory tracking
"""

from __future__ import annotations

import json
import time
import tracemalloc
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from unittest.mock import patch

import pytest
from textual.app import App, ComposeResult
from textual.events import Key
from textual.geometry import Size
from textual.message import Message

if TYPE_CHECKING:
  from clitic.completion.base import Completion, CompletionProvider
  from clitic.plugins.base import ContentPlugin, ModeProvider
  from clitic.session import SessionManager
  from clitic.widgets import Conversation, InputBar
  from clitic.widgets.conversation import BlockInfo

# ============================================================================
# Phase 1: Core Fixtures
# ============================================================================

# ----------------------------------------------------------------------------
# 1.1 BlockInfo Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def block_info_factory() -> Callable[..., BlockInfo]:
  """Factory fixture for creating BlockInfo instances with sensible defaults.

  Returns:
      A callable that creates BlockInfo instances. Auto-increments block_id
      counter if not provided.

  Example:
      >>> create_block = block_info_factory
      >>> block1 = create_block(role="user", content="Hello")
      >>> block2 = create_block(role="assistant", content="Hi")
      >>> # block1.block_id == "block-0", block2.block_id == "block-1"
  """
  from clitic.widgets.conversation import BlockInfo

  counter = [0]  # Use list to allow mutation in nested function

  def create_block(
    role: str = "user",
    content: str = "Test message",
    metadata: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
    sequence: int | None = None,
    block_id: str | None = None,
  ) -> BlockInfo:
    """Create a BlockInfo instance with defaults.

    Args:
        role: The role of the message (default: "user")
        content: The text content (default: "Test message")
        metadata: Optional metadata dict (default: empty dict)
        timestamp: Optional timestamp (default: now in UTC)
        sequence: Optional sequence number (default: auto-incremented)
        block_id: Optional block ID (default: "block-{counter}")

    Returns:
        A BlockInfo instance with the specified parameters.
    """
    current_sequence = sequence if sequence is not None else counter[0]
    current_block_id = block_id if block_id is not None else f"block-{current_sequence}"

    block = BlockInfo(
      block_id=current_block_id,
      role=role,
      content=content,
      metadata=metadata if metadata is not None else {},
      timestamp=timestamp if timestamp is not None else datetime.now(timezone.utc),
      sequence=current_sequence,
    )
    counter[0] += 1
    return block

  return create_block


@pytest.fixture
def block_info() -> BlockInfo:
  """Simple BlockInfo instance with default values.

  Returns:
      A BlockInfo with block_id="block-0", role="user", content="Test message"

  Example:
      >>> info = block_info
      >>> assert info.role == "user"
      >>> assert info.content == "Test message"
  """
  from clitic.widgets.conversation import BlockInfo

  return BlockInfo(
    block_id="block-0",
    role="user",
    content="Test message",
    metadata={},
    timestamp=datetime.now(timezone.utc),
    sequence=0,
  )


@pytest.fixture
def user_block_info() -> BlockInfo:
  """BlockInfo instance with role="user".

  Returns:
      A BlockInfo with role="user" and default other values.
  """
  from clitic.widgets.conversation import BlockInfo

  return BlockInfo(
    block_id="user-block-0",
    role="user",
    content="User message",
    metadata={},
    timestamp=datetime.now(timezone.utc),
    sequence=0,
  )


@pytest.fixture
def assistant_block_info() -> BlockInfo:
  """BlockInfo instance with role="assistant".

  Returns:
      A BlockInfo with role="assistant" and default other values.
  """
  from clitic.widgets.conversation import BlockInfo

  return BlockInfo(
    block_id="assistant-block-0",
    role="assistant",
    content="Assistant response",
    metadata={},
    timestamp=datetime.now(timezone.utc),
    sequence=0,
  )


# ----------------------------------------------------------------------------
# 1.2 Conversation Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def conversation() -> Conversation:
  """Conversation with call_after_refresh mocked using patch.object.

  Returns:
      A Conversation instance with call_after_refresh mocked.

  Example:
      >>> conv = conversation
      >>> conv.append("user", "Hello")  # Won't try to scroll
  """
  from clitic import Conversation

  conv = Conversation()
  # The caller should use: with patch.object(conv, "call_after_refresh"):
  return conv


@pytest.fixture
def conversation_factory() -> Callable[..., Conversation]:
  """Factory for creating Conversation instances with custom settings.

  Returns:
      A callable that creates Conversation instances.

  Example:
      >>> create_conv = conversation_factory
      >>> conv = create_conv(auto_scroll=False)
      >>> conv = create_conv(session_uuid="custom-id")
  """
  from clitic import Conversation

  def create_conversation(
    session_uuid: str | None = None,
    auto_scroll: bool = True,
    persistence_enabled: bool = False,
    session_dir: Path | None = None,
    max_blocks_in_memory: int = 100,
    **kwargs: Any,
  ) -> Conversation:
    """Create a Conversation instance.

    Args:
        session_uuid: Optional UUID for the session.
        auto_scroll: Whether to auto-scroll (default: True)
        persistence_enabled: Enable persistence (default: False)
        session_dir: Directory for session files
        max_blocks_in_memory: Max blocks in memory (default: 100)
        **kwargs: Additional arguments passed to Conversation

    Returns:
        A Conversation instance.
    """
    return Conversation(
      session_uuid=session_uuid,
      auto_scroll=auto_scroll,
      persistence_enabled=persistence_enabled,
      session_dir=session_dir,
      max_blocks_in_memory=max_blocks_in_memory,
      **kwargs,
    )

  return create_conversation


@pytest.fixture
def conversation_with_persistence(tmp_path: Path) -> Conversation:
  """Conversation with persistence enabled, using tmp_path for session files.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      A Conversation with persistence_enabled=True and session_dir in tmp_path.

  Example:
      >>> conv = conversation_with_persistence
      >>> conv.append("user", "Hello")
      >>> # Check tmp_path / "sessions" for JSONL file
  """
  from clitic import Conversation

  session_dir = tmp_path / "sessions"
  return Conversation(
    persistence_enabled=True,
    session_dir=session_dir,
  )


@pytest.fixture
def conversation_with_pruning(tmp_path: Path) -> Conversation:
  """Conversation with low memory threshold for testing pruning behavior.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      A Conversation with max_blocks_in_memory=2 for testing pruning.

  Example:
      >>> conv = conversation_with_pruning
      >>> # Only 2 blocks kept in memory at a time
  """
  from clitic import Conversation

  session_dir = tmp_path / "sessions"
  return Conversation(
    persistence_enabled=True,
    session_dir=session_dir,
    max_blocks_in_memory=2,
  )


@pytest.fixture
def append_block() -> Callable[[Conversation, str, str, dict[str, Any] | None], str]:
  """Helper function that appends blocks with call_after_refresh patched.

  Returns:
      A callable that appends blocks to a conversation with proper mocking.

  Example:
      >>> conv = Conversation()
      >>> block_id = append_block(conv, "user", "Hello")
  """

  def append(
    conv: Conversation,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
  ) -> str:
    """Append a block to the conversation with mocking.

    Args:
        conv: The Conversation to append to.
        role: The role of the message.
        content: The content of the message.
        metadata: Optional metadata.

    Returns:
        The block_id of the created block.
    """
    with patch.object(conv, "call_after_refresh"):
      return conv.append(role, content, metadata)

  return append


# ----------------------------------------------------------------------------
# 1.3 InputBar Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def input_bar() -> InputBar:
  """Basic InputBar instance.

  Returns:
      An InputBar with default settings.

  Example:
      >>> bar = input_bar
      >>> bar.text = "Hello"
  """
  from clitic import InputBar

  return InputBar()


@pytest.fixture
def input_bar_with_text() -> Callable[[str], InputBar]:
  """Factory for creating InputBar instances with specified text.

  Returns:
      A callable that creates InputBar instances with text.

  Example:
      >>> create_bar = input_bar_with_text
      >>> bar = create_bar("Hello world")
      >>> assert bar.text == "Hello world"
  """
  from clitic import InputBar

  def create_input_bar(text: str, **kwargs: Any) -> InputBar:
    """Create an InputBar with text.

    Args:
        text: Initial text content.
        **kwargs: Additional arguments passed to InputBar.

    Returns:
        An InputBar instance with the specified text.
    """
    return InputBar(text=text, **kwargs)

  return create_input_bar


@pytest.fixture
def capture_submit_messages():
  """Context manager to capture Submit messages from InputBar.

  Returns:
      A callable that returns a context manager for capturing messages.

  Example:
      >>> bar = InputBar(text="test")
      >>> with capture_submit_messages(bar) as messages:
      ...     bar.submit()
      >>> assert len(messages) == 1
      >>> assert isinstance(messages[0], InputBar.Submit)
  """

  @contextmanager
  def capture(bar: InputBar) -> Generator[list[Message], None, None]:
    """Capture Submit messages from InputBar.

    Args:
        bar: The InputBar to capture messages from.

    Yields:
        A list that will contain captured messages.
    """
    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(bar, "post_message", side_effect=capture_post):
      yield posted_messages

  return capture


@pytest.fixture
def key_event_factory() -> Callable[[str], Key]:
  """Factory for creating Key events.

  Returns:
      A callable that creates Key events for testing.

  Example:
      >>> create_key = key_event_factory
      >>> enter_key = create_key("enter")
      >>> shift_enter = create_key("shift+enter")
  """

  def create_key(key: str, character: str | None = None) -> Key:
    """Create a Key event.

    Args:
        key: The key name (e.g., "enter", "shift+enter", "a")
        character: Optional character representation.

    Returns:
        A Key event instance.
    """
    return Key(key=key, character=character)

  return create_key


# ----------------------------------------------------------------------------
# 1.4 Session Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def temp_session_dir(tmp_path: Path) -> Path:
  """Create a temporary session directory using tmp_path.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      Path to a temporary session directory.

  Example:
      >>> session_dir = temp_session_dir
      >>> manager = SessionManager(session_dir=session_dir)
  """
  session_dir = tmp_path / "sessions"
  session_dir.mkdir(parents=True, exist_ok=True)
  return session_dir


@pytest.fixture
def session_file_factory(tmp_path: Path) -> Callable[[str, list[dict[str, Any]]], Path]:
  """Factory for creating session JSONL files.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      A callable that creates session files with blocks.

  Example:
      >>> create_session = session_file_factory
      >>> session_file = create_session("test-session", [
      ...     {"block_id": "test-0", "role": "user", "content": "Hello", "sequence": 0}
      ... ])
  """
  session_dir = tmp_path / "sessions"
  session_dir.mkdir(parents=True, exist_ok=True)

  def create_session_file(
    session_id: str,
    blocks: list[dict[str, Any]],
  ) -> Path:
    """Create a session JSONL file.

    Args:
        session_id: The session identifier.
        blocks: List of block dictionaries with block_id, role, content, etc.

    Returns:
        Path to the created session file.
    """
    file_path = session_dir / f"{session_id}.jsonl"
    lines = []
    for block in blocks:
      # Ensure timestamp is included
      if "timestamp" not in block:
        block["timestamp"] = datetime.now(timezone.utc).isoformat()
      if "metadata" not in block:
        block["metadata"] = {}
      lines.append(json.dumps(block))

    file_path.write_text("\n".join(lines) + "\n")
    return file_path

  return create_session_file


@pytest.fixture
def session_manager(tmp_path: Path) -> SessionManager:
  """SessionManager with temporary directory.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      A SessionManager instance with a temp session_dir.

  Example:
      >>> manager = session_manager
      >>> manager.start_session("test-id")
  """
  from clitic.session import SessionManager

  return SessionManager(session_dir=tmp_path / "sessions")


@pytest.fixture
def session_manager_with_persistence(tmp_path: Path) -> SessionManager:
  """SessionManager with persistence enabled and temp directory.

  Args:
      tmp_path: pytest's built-in temp directory fixture.

  Returns:
      A SessionManager with persistence_enabled=True.

  Example:
      >>> manager = session_manager_with_persistence
      >>> manager.start_session("test-id")
      >>> manager.save_block(block_info)
  """
  from clitic.session import SessionManager

  return SessionManager(
    persistence_enabled=True,
    session_dir=tmp_path / "sessions",
  )


# ============================================================================
# Phase 2: Plugin/Provider Fixtures
# ============================================================================


@pytest.fixture
def simple_plugin() -> ContentPlugin:
  """Simple ContentPlugin implementation for testing.

  Returns:
      A ContentPlugin that accepts all content types.

  Example:
      >>> plugin = simple_plugin
      >>> assert plugin.name == "SimplePlugin"
      >>> assert plugin.can_render("text/plain", "hello")
  """
  from clitic.plugins import ContentPlugin

  class SimplePlugin(ContentPlugin):
    """Simple test plugin that accepts all content."""

    @property
    def name(self) -> str:
      return "SimplePlugin"

    def can_render(self, content_type: str, content: str) -> bool:
      return True

    def render(self, content: str) -> object:
      class MockWidget:
        def __init__(self, content: str) -> None:
          self.content = content

      return MockWidget(content)

  return SimplePlugin()


@pytest.fixture
def lifecycle_plugin() -> ContentPlugin:
  """ContentPlugin with lifecycle tracking for testing.

  Returns:
      A ContentPlugin with registered/unregistered flags.

  Example:
      >>> plugin = lifecycle_plugin
      >>> app = App()
      >>> plugin.on_register(app)
      >>> assert plugin.registered
  """
  from clitic.plugins import ContentPlugin

  class LifecyclePlugin(ContentPlugin):
    """Plugin with lifecycle tracking."""

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
      class MockWidget:
        pass

      return MockWidget()

    def on_register(self, app: object) -> None:
      self.registered = True
      self._app = app

    def on_unregister(self, app: object) -> None:
      self.unregistered = True
      self._app = None

  return LifecyclePlugin()


@pytest.fixture
def plugin_factory() -> Callable[[str, int], ContentPlugin]:
  """Factory for creating custom ContentPlugin instances.

  Returns:
      A callable that creates ContentPlugin instances with custom settings.

  Example:
      >>> create_plugin = plugin_factory
      >>> plugin = create_plugin("CustomPlugin", priority=100)
      >>> assert plugin.name == "CustomPlugin"
      >>> assert plugin.priority == 100
  """
  from clitic.plugins import ContentPlugin

  def create_plugin(
    name: str = "TestPlugin",
    priority: int = 0,
  ) -> ContentPlugin:
    """Create a ContentPlugin with specified name and priority.

    Args:
        name: Plugin name (default: "TestPlugin")
        priority: Plugin priority (default: 0)

    Returns:
        A ContentPlugin instance.
    """

    class CustomPlugin(ContentPlugin):
      """Custom test plugin."""

      _name = name
      _priority = priority

      @property
      def name(self) -> str:
        return self._name

      @property
      def priority(self) -> int:
        return self._priority

      def can_render(self, content_type: str, content: str) -> bool:
        return True

      def render(self, content: str) -> object:
        class MockWidget:
          def __init__(self, content: str) -> None:
            self.content = content

        return MockWidget(content)

    return CustomPlugin()

  return create_plugin


@pytest.fixture
def completion_provider_factory() -> Callable[[str], CompletionProvider]:
  """Factory for creating CompletionProvider instances.

  Returns:
      A callable that creates CompletionProvider instances.

  Note:
      Requires clitic.completion module to be available.
  """
  from clitic.completion.base import CompletionProvider

  def create_provider(name: str = "TestProvider") -> CompletionProvider:
    """Create a CompletionProvider with specified name.

    Args:
        name: Provider name (default: "TestProvider")

    Returns:
        A CompletionProvider instance.
    """

    class TestProvider(CompletionProvider):
      """Test completion provider."""

      _name = name

      @property
      def name(self) -> str:
        return self._name

      def get_completions(
        self,
        text: str,
        cursor_position: int,
      ) -> list[Completion]:
        return []

    return TestProvider()

  return create_provider


@pytest.fixture
def mode_provider_factory() -> Callable[[str, str], ModeProvider]:
  """Factory for creating ModeProvider instances.

  Returns:
      A callable that creates ModeProvider instances.

  Example:
      >>> create_mode = mode_provider_factory
      >>> mode = create_mode("TestMode", "[T]")
      >>> assert mode.name == "TestMode"
      >>> assert mode.indicator == "[T]"
  """
  from clitic.plugins import ModeProvider

  def create_mode(
    name: str = "TestMode",
    indicator: str = "[T]",
  ) -> ModeProvider:
    """Create a ModeProvider with specified name and indicator.

    Args:
        name: Mode name (default: "TestMode")
        indicator: Mode indicator string (default: "[T]")

    Returns:
        A ModeProvider instance.
    """

    class TestMode(ModeProvider):
      """Test mode provider."""

      _name = name
      _indicator = indicator

      @property
      def name(self) -> str:
        return self._name

      @property
      def indicator(self) -> str:
        return self._indicator

      def detect(self, text: str, cursor_position: int) -> bool:
        return text.startswith(name.lower())

      def get_highlighter(self) -> object | None:
        return None

    return TestMode()

  return create_mode


# ============================================================================
# Phase 3: Mock App Fixtures
# ============================================================================


@pytest.fixture
def mock_app_factory() -> Callable[..., type[App]]:
  """Factory for creating minimal Textual App instances.

  Returns:
      A callable that creates minimal App subclasses for testing.

  Example:
      >>> create_app = mock_app_factory
      >>> MyApp = create_app()
      >>> app = MyApp()
      >>> # Or with custom widgets:
      >>> MyApp = create_app(widgets=[Conversation(), InputBar()])
  """

  def create_app(
    widgets: list[object] | None = None,
    title: str = "Test App",
    **kwargs: Any,
  ) -> type[App]:
    """Create a minimal App class for testing.

    Args:
        widgets: Optional list of widgets to compose.
        title: App title (default: "Test App")
        **kwargs: Additional arguments passed to App.

    Returns:
        An App subclass.
    """
    _widgets = widgets if widgets is not None else []

    class TestApp(App):
      """Minimal test app."""

      def compose(self) -> ComposeResult:
        yield from _widgets

    TestApp.__name__ = "TestApp"
    return TestApp

  return create_app


@pytest.fixture
async def mounted_conversation() -> Conversation:
  """Async fixture for a mounted Conversation widget.

  Returns:
      A Conversation that is mounted in a minimal App.

  Note:
      This is an async fixture, use with pytest-asyncio.
  """
  from clitic import Conversation

  class TestApp(App):
    def compose(self) -> ComposeResult:
      yield Conversation()

  async with TestApp().run_test() as pilot:
    conv = pilot.app.query_one(Conversation)
    yield conv


@pytest.fixture
async def mounted_input_bar() -> InputBar:
  """Async fixture for a mounted InputBar widget.

  Returns:
      An InputBar that is mounted in a minimal App.

  Note:
      This is an async fixture, use with pytest-asyncio.
  """
  from clitic import InputBar

  class TestApp(App):
    def compose(self) -> ComposeResult:
      yield InputBar()

  async with TestApp().run_test() as pilot:
    input_bar = pilot.app.query_one(InputBar)
    yield input_bar


# ============================================================================
# Phase 4: Utility Fixtures
# ============================================================================


@pytest.fixture
def utc_timestamp() -> Callable[[int | None], datetime]:
  """Factory for creating UTC timestamps.

  Returns:
      A callable that creates datetime objects in UTC.

  Example:
      >>> create_ts = utc_timestamp
      >>> now = create_ts()  # Current time
      >>> past = create_ts(-60)  # 60 seconds ago
      >>> future = create_ts(60)  # 60 seconds from now
  """

  def create_timestamp(offset_seconds: int | None = None) -> datetime:
    """Create a UTC timestamp.

    Args:
        offset_seconds: Optional offset from now in seconds.
            Positive for future, negative for past.

    Returns:
        A timezone-aware datetime in UTC.
    """
    ts = datetime.now(timezone.utc)
    if offset_seconds is not None:
      ts = ts + timedelta(seconds=offset_seconds)
    return ts

  return create_timestamp


class TimingResult:
  """Mutable container for timing results."""

  __slots__ = ("elapsed",)

  def __init__(self) -> None:
    self.elapsed: float = 0.0


class MemoryResult:
  """Mutable container for memory tracking results."""

  __slots__ = ("current", "peak")

  def __init__(self) -> None:
    self.current: int = 0
    self.peak: int = 0


@pytest.fixture
def timer():
  """Context manager for timing execution.

  Returns:
      A callable that returns a context manager for timing.

  Example:
      >>> time_it = timer
      >>> with time_it() as result:
      ...     # Do some work
      ...     pass
      >>> print(f"Elapsed: {result.elapsed:.3f}s")
  """

  @contextmanager
  def time_context() -> Generator[TimingResult, None, None]:
    """Time the execution of a block.

    Yields:
        A TimingResult object with `elapsed` attribute.
    """
    result = TimingResult()
    start = time.perf_counter()
    try:
      yield result
    finally:
      result.elapsed = time.perf_counter() - start

  return time_context


@pytest.fixture
def memory_tracker():
  """Context manager for tracking memory usage.

  Returns:
      A callable that returns a context manager for memory tracking.

  Example:
      >>> track_memory = memory_tracker
      >>> with track_memory() as result:
      ...     # Do some work
      ...     pass
      >>> print(f"Peak memory: {result.peak / 1024 / 1024:.1f}MB")
  """

  @contextmanager
  def track_memory() -> Generator[MemoryResult, None, None]:
    """Track memory usage during a block.

    Yields:
        A MemoryResult object with `current` and `peak` attributes.
    """
    result = MemoryResult()
    tracemalloc.start()
    try:
      yield result
    finally:
      result.current, result.peak = tracemalloc.get_traced_memory()
      tracemalloc.stop()

  return track_memory


# ============================================================================
# Additional Helper Fixtures
# ============================================================================


@pytest.fixture
def geometry_size() -> Callable[[int, int], Size]:
  """Factory for creating Size objects.

  Returns:
      A callable that creates Size instances.

  Example:
      >>> create_size = geometry_size
      >>> size = create_size(80, 24)  # 80x24 terminal
  """

  def create_size(width: int, height: int) -> Size:
    """Create a Size instance.

    Args:
        width: Width in characters.
        height: Height in lines.

    Returns:
        A Size instance.
    """
    return Size(width, height)

  return create_size
