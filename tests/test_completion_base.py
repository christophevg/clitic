"""Tests for clitic completion base classes."""

import pytest

from clitic.completion import Completion, CompletionProvider


class TestCompletion:
  """Tests for the Completion dataclass."""

  def test_required_fields(self) -> None:
    """Completion requires text and display_text."""
    completion = Completion(text="hello", display_text="Hello World")
    assert completion.text == "hello"
    assert completion.display_text == "Hello World"

  def test_default_values(self) -> None:
    """Completion should have sensible defaults."""
    completion = Completion(text="test", display_text="Test")
    assert completion.cursor_offset == 0
    assert completion.description == ""
    assert completion.priority == 0
    assert completion.metadata == {}

  def test_custom_values(self) -> None:
    """Completion should accept custom values."""
    completion = Completion(
      text="func()",
      display_text="func()",
      cursor_offset=-1,
      description="Call function",
      priority=10,
      metadata={"type": "function"},
    )
    assert completion.cursor_offset == -1
    assert completion.description == "Call function"
    assert completion.priority == 10
    assert completion.metadata == {"type": "function"}

  def test_metadata_mutable_default(self) -> None:
    """Each Completion should have its own metadata dict."""
    completion1 = Completion(text="a", display_text="A")
    completion2 = Completion(text="b", display_text="B")
    completion1.metadata["key"] = "value"
    assert "key" not in completion2.metadata

  def test_less_than_by_priority(self) -> None:
    """Higher priority should sort before lower priority."""
    high = Completion(text="high", display_text="High", priority=10)
    low = Completion(text="low", display_text="Low", priority=1)
    assert high < low
    assert not low < high

  def test_less_than_by_display_text(self) -> None:
    """Same priority should sort alphabetically by display_text."""
    a = Completion(text="a", display_text="A", priority=5)
    b = Completion(text="b", display_text="B", priority=5)
    assert a < b
    assert not b < a

  def test_less_than_priority_first(self) -> None:
    """Priority should take precedence over display_text."""
    high_z = Completion(text="z", display_text="Z", priority=10)
    low_a = Completion(text="a", display_text="A", priority=1)
    assert high_z < low_a

  def test_equality_by_text_and_display(self) -> None:
    """Equality should be based on text and display_text."""
    c1 = Completion(text="test", display_text="Test")
    c2 = Completion(text="test", display_text="Test")
    c3 = Completion(text="test", display_text="Different")
    c4 = Completion(text="different", display_text="Test")
    assert c1 == c2
    assert c1 != c3
    assert c1 != c4

  def test_equality_with_different_priority(self) -> None:
    """Completions with different priorities can still be equal."""
    c1 = Completion(text="test", display_text="Test", priority=1)
    c2 = Completion(text="test", display_text="Test", priority=10)
    assert c1 == c2

  def test_equality_with_non_completion(self) -> None:
    """Equality with non-Completion should return NotImplemented."""
    completion = Completion(text="test", display_text="Test")
    assert completion != "test"
    assert completion != 123
    assert completion is not None

  def test_hash_consistent_with_equality(self) -> None:
    """Equal completions should have equal hashes."""
    c1 = Completion(text="test", display_text="Test")
    c2 = Completion(text="test", display_text="Test")
    assert hash(c1) == hash(c2)

  def test_hash_usable_in_set(self) -> None:
    """Completion should be usable in sets."""
    c1 = Completion(text="test", display_text="Test")
    c2 = Completion(text="test", display_text="Test")
    c3 = Completion(text="other", display_text="Other")
    completion_set = {c1, c2, c3}
    assert len(completion_set) == 2

  def test_sorting_completions(self) -> None:
    """Completions should sort correctly."""
    completions = [
      Completion(text="c", display_text="C", priority=1),
      Completion(text="a", display_text="A", priority=10),
      Completion(text="b", display_text="B", priority=1),
      Completion(text="d", display_text="D", priority=10),
    ]
    sorted_completions = sorted(completions)
    # High priority first, then alphabetically
    assert sorted_completions[0].display_text == "A"
    assert sorted_completions[1].display_text == "D"
    assert sorted_completions[2].display_text == "B"
    assert sorted_completions[3].display_text == "C"


class ConcreteCompletionProvider(CompletionProvider):
  """Concrete implementation of CompletionProvider for testing."""

  @property
  def name(self) -> str:
    return "TestProvider"

  def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
    if text.startswith("hel"):
      return [
        Completion(text="hello", display_text="hello"),
        Completion(text="help", display_text="help"),
      ]
    return []


class CustomPriorityProvider(CompletionProvider):
  """Provider with custom priority for testing."""

  @property
  def name(self) -> str:
    return "HighPriorityProvider"

  @property
  def priority(self) -> int:
    return 100

  def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
    return []


class TestCompletionProvider:
  """Tests for the CompletionProvider abstract base class."""

  def test_cannot_instantiate_abc(self) -> None:
    """CompletionProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
      CompletionProvider()  # type: ignore[abstract]

  def test_must_implement_name(self) -> None:
    """Subclasses must implement name property."""

    class IncompleteProvider(CompletionProvider):
      def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        return []

    with pytest.raises(TypeError):
      IncompleteProvider()  # type: ignore[abstract]

  def test_must_implement_get_completions(self) -> None:
    """Subclasses must implement get_completions method."""

    class IncompleteProvider(CompletionProvider):
      @property
      def name(self) -> str:
        return "Incomplete"

    with pytest.raises(TypeError):
      IncompleteProvider()  # type: ignore[abstract]

  def test_concrete_implementation_works(self) -> None:
    """Concrete implementation can be instantiated."""
    provider = ConcreteCompletionProvider()
    assert provider.name == "TestProvider"

  def test_default_priority_is_zero(self) -> None:
    """Default priority should be 0."""
    provider = ConcreteCompletionProvider()
    assert provider.priority == 0

  def test_custom_priority(self) -> None:
    """Custom priority can be set."""
    provider = CustomPriorityProvider()
    assert provider.priority == 100

  def test_get_completions_returns_list(self) -> None:
    """get_completions should return a list of Completions."""
    provider = ConcreteCompletionProvider()
    completions = provider.get_completions("hel", 3)
    assert isinstance(completions, list)
    assert len(completions) == 2

  def test_get_completions_empty_when_no_match(self) -> None:
    """get_completions should return empty list when no matches."""
    provider = ConcreteCompletionProvider()
    completions = provider.get_completions("xyz", 3)
    assert completions == []

  def test_get_completions_async_default_impl(self) -> None:
    """get_completions_async should call get_completions by default."""
    import asyncio

    provider = ConcreteCompletionProvider()
    completions = asyncio.run(provider.get_completions_async("hel", 3))
    assert len(completions) == 2


class AsyncCompletionProvider(CompletionProvider):
  """Provider with async completions for testing."""

  @property
  def name(self) -> str:
    return "AsyncProvider"

  async def get_completions_async(
    self, text: str, cursor_position: int
  ) -> list[Completion]:
    """Custom async implementation."""
    return [
      Completion(text="async_result", display_text="async_result"),
    ]

  def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
    return []


class TestCompletionProviderAsync:
  """Tests for CompletionProvider async functionality."""

  def test_get_completions_async_can_be_overridden(self) -> None:
    """get_completions_async can be overridden in subclasses."""
    import asyncio

    provider = AsyncCompletionProvider()
    completions = asyncio.run(provider.get_completions_async("test", 0))
    assert len(completions) == 1
    assert completions[0].text == "async_result"


class TestCompletionProviderIntegration:
  """Integration tests for CompletionProvider."""

  def test_provider_with_sorted_completions(self) -> None:
    """Provider should be able to return sorted completions."""

    class SortedProvider(CompletionProvider):
      @property
      def name(self) -> str:
        return "Sorted"

      def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        completions = [
          Completion(text="c", display_text="C", priority=1),
          Completion(text="a", display_text="A", priority=10),
          Completion(text="b", display_text="B", priority=5),
        ]
        return sorted(completions)

    provider = SortedProvider()
    completions = provider.get_completions("", 0)
    assert completions[0].display_text == "A"
    assert completions[1].display_text == "B"
    assert completions[2].display_text == "C"

  def test_provider_with_metadata(self) -> None:
    """Provider should be able to return completions with metadata."""

    class MetadataProvider(CompletionProvider):
      @property
      def name(self) -> str:
        return "Metadata"

      def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        return [
          Completion(
            text="func",
            display_text="func()",
            metadata={"type": "function", "args": 0},
          ),
        ]

    provider = MetadataProvider()
    completions = provider.get_completions("", 0)
    assert completions[0].metadata["type"] == "function"

  def test_cursor_position_affects_completions(self) -> None:
    """Provider should be able to use cursor position."""

    class PositionAwareProvider(CompletionProvider):
      @property
      def name(self) -> str:
        return "PositionAware"

      def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        # Only provide completions at start of line
        if cursor_position == 0:
          return [Completion(text="start", display_text="start")]
        return []

    provider = PositionAwareProvider()
    assert len(provider.get_completions("text", 0)) == 1
    assert len(provider.get_completions("text", 2)) == 0
