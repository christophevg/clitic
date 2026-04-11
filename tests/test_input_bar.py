"""Tests for InputBar widget."""

from unittest.mock import patch

from textual.events import Key
from textual.message import Message
from textual.widgets import TextArea

from clitic import InputBar


class TestInputBarInstantiation:
  """Tests for InputBar instantiation."""

  def test_input_bar_can_be_instantiated(self) -> None:
    """InputBar should be instantiable."""
    input_bar = InputBar()
    assert input_bar is not None

  def test_input_bar_extends_text_area(self) -> None:
    """InputBar should extend TextArea."""
    input_bar = InputBar()
    assert isinstance(input_bar, TextArea)

  def test_input_bar_accepts_initial_text(self) -> None:
    """InputBar should accept initial text parameter."""
    input_bar = InputBar(text="Hello")
    assert input_bar.text == "Hello"

  def test_input_bar_default_empty(self) -> None:
    """InputBar should default to empty text."""
    input_bar = InputBar()
    assert input_bar.text == ""

  def test_input_bar_accepts_name_parameter(self) -> None:
    """InputBar should accept a name parameter."""
    input_bar = InputBar(name="test_input")
    assert input_bar._name == "test_input"

  def test_input_bar_accepts_id_parameter(self) -> None:
    """InputBar should accept an id parameter."""
    input_bar = InputBar(id="test-id")
    assert input_bar.id == "test-id"

  def test_input_bar_accepts_classes_parameter(self) -> None:
    """InputBar should accept classes parameter."""
    input_bar = InputBar(classes="custom-class")
    assert input_bar.classes == {"custom-class"}


class TestInputBarProperties:
  """Tests for InputBar properties."""

  def test_text_property_returns_content(self) -> None:
    """text property should return the current text content."""
    input_bar = InputBar(text="test content")
    assert input_bar.text == "test content"

  def test_text_property_can_be_set(self) -> None:
    """text property should be settable."""
    input_bar = InputBar()
    input_bar.text = "new content"
    assert input_bar.text == "new content"

  def test_text_property_returns_empty_when_cleared(self) -> None:
    """text property should return empty string after clear_text."""
    input_bar = InputBar(text="some text")
    input_bar.clear_text()
    assert input_bar.text == ""

  def test_clear_text_removes_all_text(self) -> None:
    """clear_text() should remove all text from the input."""
    input_bar = InputBar(text="multiline\ntext\nhere")
    input_bar.clear_text()
    assert input_bar.text == ""

  def test_clear_text_on_empty_input(self) -> None:
    """clear_text() should work on empty input without error."""
    input_bar = InputBar()
    input_bar.clear_text()  # Should not raise
    assert input_bar.text == ""


class TestInputBarSubmit:
  """Tests for InputBar submit functionality."""

  def test_submit_posts_submit_message(self) -> None:
    """submit() should post a Submit message."""
    input_bar = InputBar(text="test message")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      input_bar.submit()

    # Find Submit messages (TextArea also posts Changed messages)
    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 1
    assert submit_messages[0].text == "test message"

  def test_submit_clears_text(self) -> None:
    """submit() should clear the text after emitting."""
    input_bar = InputBar(text="test message")
    with patch.object(input_bar, "post_message"):
      input_bar.submit()
    assert input_bar.text == ""

  def test_submit_skips_empty_text(self) -> None:
    """submit() should not emit for empty text."""
    input_bar = InputBar(text="")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      input_bar.submit()

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_submit_skips_whitespace_only(self) -> None:
    """submit() should not emit for whitespace-only text."""
    input_bar = InputBar(text="   \n\t  ")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      input_bar.submit()

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_submit_preserves_multiline_text(self) -> None:
    """submit() should preserve multiline text in the message."""
    input_bar = InputBar(text="line one\nline two\nline three")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      input_bar.submit()

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 1
    assert submit_messages[0].text == "line one\nline two\nline three"


class TestInputBarSubmitMessage:
  """Tests for InputBar.Submit message."""

  def test_submit_message_carries_text(self) -> None:
    """Submit message should carry the submitted text."""
    message = InputBar.Submit("test text")
    assert message.text == "test text"

  def test_submit_message_is_a_message(self) -> None:
    """Submit should be a Textual Message."""
    msg = InputBar.Submit("test")
    assert isinstance(msg, Message)

  def test_submit_message_text_attribute(self) -> None:
    """Submit message text should be accessible."""
    message = InputBar.Submit("original")
    assert message.text == "original"


class TestInputBarKeyHandling:
  """Tests for InputBar key handling."""

  def test_enter_key_triggers_submit(self) -> None:
    """Enter key without Shift should trigger submit."""
    input_bar = InputBar(text="test")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 1

  def test_shift_enter_does_not_submit(self) -> None:
    """Shift+Enter should not trigger submit (pass through for newline)."""
    input_bar = InputBar(text="test")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      # When Kitty protocol is supported, shift+enter is a distinct key
      event = Key(key="shift+enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_other_keys_do_not_trigger_submit(self) -> None:
    """Other keys should not trigger submit."""
    input_bar = InputBar(text="test")

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="a", character="a")
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_enter_stops_event(self) -> None:
    """Enter key should stop the event."""
    input_bar = InputBar(text="test")
    event = Key(key="enter", character=None)

    input_bar.on_key(event)

    # Check that stop was called (event is stopped)
    assert event._stop_propagation

  def test_enter_prevents_default(self) -> None:
    """Enter key should prevent default behavior."""
    input_bar = InputBar(text="test")
    event = Key(key="enter", character=None)

    input_bar.on_key(event)

    # Check that prevent_default was called (sets _no_default_action)
    assert event._no_default_action

  def test_disabled_widget_does_not_submit(self) -> None:
    """Enter key should not submit when widget is disabled."""
    input_bar = InputBar(text="test", disabled=True)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="enter", character=None)
      input_bar.on_key(event)

    # Should not submit when disabled
    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0
    # Event should not be stopped when disabled
    assert not event._stop_propagation


class TestInputBarIntegration:
  """Tests for InputBar integration with clitic."""

  def test_input_bar_exported_from_main_package(self) -> None:
    """InputBar should be exported from main package."""
    from clitic import InputBar as MainInputBar

    assert MainInputBar is InputBar

  def test_input_bar_in_all(self) -> None:
    """InputBar should be in __all__."""
    import clitic

    assert "InputBar" in clitic.__all__

  def test_input_bar_has_submit_nested_class(self) -> None:
    """InputBar should have Submit as a nested class."""
    assert hasattr(InputBar, "Submit")
    assert InputBar.Submit is not None
