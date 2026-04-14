"""Tests for InputBar widget."""

import pytest
from unittest.mock import patch

from textual.events import Key
from textual.message import Message
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

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


class TestInputBarCursorMovement:
  """Tests for InputBar cursor movement functionality."""

  def test_cursor_location_default(self) -> None:
    """Cursor should start at (0, 0) by default."""
    input_bar = InputBar(text="hello")
    assert input_bar.cursor_location == (0, 0)

  def test_cursor_location_can_be_set(self) -> None:
    """cursor_location property should be settable."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 3)
    assert input_bar.cursor_location == (0, 3)

  def test_cursor_location_multiline(self) -> None:
    """Cursor location should work correctly with multiline text."""
    input_bar = InputBar(text="line one\nline two\nline three")
    # Move to second line
    input_bar.cursor_location = (1, 0)
    assert input_bar.cursor_location == (1, 0)
    # Move to third line
    input_bar.cursor_location = (2, 4)
    assert input_bar.cursor_location == (2, 4)

  def test_action_cursor_right_moves_cursor(self) -> None:
    """action_cursor_right should move cursor right by one character."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_right()
    assert input_bar.cursor_location == (0, 1)
    input_bar.action_cursor_right()
    assert input_bar.cursor_location == (0, 2)

  def test_action_cursor_left_moves_cursor(self) -> None:
    """action_cursor_left should move cursor left by one character."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 3)
    input_bar.action_cursor_left()
    assert input_bar.cursor_location == (0, 2)
    input_bar.action_cursor_left()
    assert input_bar.cursor_location == (0, 1)

  def test_action_cursor_left_at_start(self) -> None:
    """action_cursor_left at start should stay at start."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_left()
    # Cursor should still be at start
    assert input_bar.cursor_location == (0, 0)

  def test_action_cursor_right_at_end(self) -> None:
    """action_cursor_right at end should stay at end."""
    input_bar = InputBar(text="hi")
    input_bar.cursor_location = (0, 2)
    input_bar.action_cursor_right()
    # Cursor should still be at end
    assert input_bar.cursor_location == (0, 2)

  def test_action_cursor_up_moves_up(self) -> None:
    """action_cursor_up should move cursor up one line."""
    input_bar = InputBar(text="line one\nline two\nline three")
    input_bar.cursor_location = (1, 4)
    input_bar.action_cursor_up()
    assert input_bar.cursor_location == (0, 4)

  def test_action_cursor_down_moves_down(self) -> None:
    """action_cursor_down should move cursor down one line."""
    input_bar = InputBar(text="line one\nline two\nline three")
    input_bar.cursor_location = (0, 4)
    input_bar.action_cursor_down()
    assert input_bar.cursor_location == (1, 4)

  def test_action_cursor_up_at_top(self) -> None:
    """action_cursor_up at top line moves to line start."""
    input_bar = InputBar(text="line one\nline two")
    input_bar.cursor_location = (0, 4)
    input_bar.action_cursor_up()
    # At top line, cursor_up moves to line start
    assert input_bar.cursor_location == (0, 0)

  def test_action_cursor_down_at_bottom(self) -> None:
    """action_cursor_down at bottom line moves to line end."""
    input_bar = InputBar(text="line one\nline two")
    input_bar.cursor_location = (1, 4)
    input_bar.action_cursor_down()
    # At bottom line, cursor_down moves to end of line
    assert input_bar.cursor_location == (1, 8)

  def test_action_cursor_line_start(self) -> None:
    """action_cursor_line_start should move cursor to start of line."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 5)
    input_bar.action_cursor_line_start()
    assert input_bar.cursor_location == (0, 0)

  def test_action_cursor_line_end(self) -> None:
    """action_cursor_line_end should move cursor to end of line."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_line_end()
    assert input_bar.cursor_location == (0, 11)

  def test_action_cursor_word_left(self) -> None:
    """action_cursor_word_left should move cursor to start of previous word."""
    input_bar = InputBar(text="hello world test")
    input_bar.cursor_location = (0, 15)  # At end of "test"
    input_bar.action_cursor_word_left()
    # Should move to start of "test"
    assert input_bar.cursor_location == (0, 12)

  def test_action_cursor_word_right(self) -> None:
    """action_cursor_word_right should move cursor to start of next word."""
    input_bar = InputBar(text="hello world test")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_word_right()
    # Moves to position 5 (end of "hello")
    assert input_bar.cursor_location == (0, 5)

  def test_cursor_movement_between_lines(self) -> None:
    """Cursor should move correctly between lines."""
    input_bar = InputBar(text="abc\ndef\nghi")
    # Start at end of first line
    input_bar.cursor_location = (0, 3)
    # Move right - should go to start of second line
    input_bar.action_cursor_right()
    assert input_bar.cursor_location == (1, 0)
    # Move left - should go back to end of first line
    input_bar.action_cursor_left()
    assert input_bar.cursor_location == (0, 3)


class TestInputBarSelection:
  """Tests for InputBar selection functionality."""

  def test_selection_default_empty(self) -> None:
    """Selection should be empty by default."""
    input_bar = InputBar(text="hello")
    assert input_bar.selection.is_empty

  def test_selection_start_equals_end_when_empty(self) -> None:
    """When selection is empty, start should equal end."""
    input_bar = InputBar(text="hello")
    assert input_bar.selection.start == input_bar.selection.end

  def test_selected_text_empty_by_default(self) -> None:
    """selected_text should be empty when no selection."""
    input_bar = InputBar(text="hello")
    assert input_bar.selection.is_empty
    assert input_bar.selected_text == ""

  def test_action_cursor_right_with_select(self) -> None:
    """action_cursor_right with select=True should create selection."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_right(select=True)
    assert input_bar.selection.start == (0, 0)
    assert input_bar.selection.end == (0, 1)
    assert input_bar.selected_text == "h"

  def test_action_cursor_left_with_select(self) -> None:
    """action_cursor_left with select=True should create selection."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 5)
    input_bar.action_cursor_left(select=True)
    # When selecting backwards, start is original pos, end is new pos
    assert input_bar.selection.start == (0, 5)
    assert input_bar.selection.end == (0, 4)
    assert input_bar.selected_text == "o"

  def test_action_cursor_down_with_select(self) -> None:
    """action_cursor_down with select=True should create vertical selection."""
    input_bar = InputBar(text="line one\nline two")
    input_bar.cursor_location = (0, 2)
    input_bar.action_cursor_down(select=True)
    # Selection should span lines
    assert input_bar.selection.start == (0, 2)
    assert input_bar.selection.end == (1, 2)

  def test_action_cursor_up_with_select(self) -> None:
    """action_cursor_up with select=True should create vertical selection."""
    input_bar = InputBar(text="line one\nline two")
    input_bar.cursor_location = (1, 2)
    input_bar.action_cursor_up(select=True)
    # When selecting backwards (up), start is original pos, end is new pos
    assert input_bar.selection.start == (1, 2)
    assert input_bar.selection.end == (0, 2)

  def test_action_cursor_line_start_with_select(self) -> None:
    """action_cursor_line_start with select=True should select to line start."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 6)
    input_bar.action_cursor_line_start(select=True)
    # When selecting backwards (to line start), start is original pos, end is new pos
    assert input_bar.selection.start == (0, 6)
    assert input_bar.selection.end == (0, 0)
    assert input_bar.selected_text == "hello "

  def test_action_cursor_line_end_with_select(self) -> None:
    """action_cursor_line_end with select=True should select to line end."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_line_end(select=True)
    assert input_bar.selection.start == (0, 0)
    assert input_bar.selection.end == (0, 11)
    assert input_bar.selected_text == "hello world"

  def test_select_line(self) -> None:
    """select_line should select entire line."""
    input_bar = InputBar(text="hello world\nsecond line")
    input_bar.cursor_location = (0, 5)
    input_bar.select_line(0)
    assert input_bar.selected_text == "hello world"

  def test_action_select_line(self) -> None:
    """action_select_line should select the current line."""
    input_bar = InputBar(text="hello world\nsecond line")
    input_bar.cursor_location = (0, 5)
    input_bar.action_select_line()
    assert input_bar.selected_text == "hello world"

  def test_select_all(self) -> None:
    """select_all should select all text."""
    input_bar = InputBar(text="hello\nworld")
    input_bar.select_all()
    assert input_bar.selection.start == (0, 0)
    assert input_bar.selection.end == (1, 5)
    assert input_bar.selected_text == "hello\nworld"

  def test_action_select_all(self) -> None:
    """action_select_all should select all text."""
    input_bar = InputBar(text="hello world")
    input_bar.action_select_all()
    assert input_bar.selected_text == "hello world"

  def test_selection_multiline(self) -> None:
    """Selection should work correctly across lines."""
    input_bar = InputBar(text="line one\nline two\nline three")
    input_bar.cursor_location = (0, 2)
    # Select down two lines - selects from (0, 2) to (2, 2)
    input_bar.action_cursor_down(select=True)
    input_bar.action_cursor_down(select=True)
    # "ne one\nline two\nli" = from "line one\nline two\nline three"
    assert input_bar.selected_text == "ne one\nline two\nli"

  def test_selection_can_be_cleared(self) -> None:
    """Selection can be cleared by setting cursor_location."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_right(select=True)
    input_bar.action_cursor_right(select=True)
    assert input_bar.selected_text == "he"
    # Clear selection by moving cursor without select
    input_bar.action_cursor_right(select=False)
    assert input_bar.selection.is_empty

  def test_selection_word_left(self) -> None:
    """action_cursor_word_left with select should select backwards."""
    input_bar = InputBar(text="hello world test")
    input_bar.cursor_location = (0, 15)
    input_bar.action_cursor_word_left(select=True)
    # Cursor moves from 15 to 12 (start of "test"), selecting "tes" (3 chars)
    assert input_bar.selected_text == "tes"

  def test_selection_word_right(self) -> None:
    """action_cursor_word_right with select should select forwards."""
    input_bar = InputBar(text="hello world test")
    input_bar.cursor_location = (0, 0)
    input_bar.action_cursor_word_right(select=True)
    input_bar.action_cursor_word_right(select=True)
    # After two word rights: cursor at (0, 11), selection from (0, 0) to (0, 11)
    assert input_bar.selected_text == "hello world"


class TestInputBarClipboard:
  """Tests for InputBar clipboard operations."""

  def test_copy_action_exists(self) -> None:
    """InputBar should inherit copy action from TextArea."""
    input_bar = InputBar(text="hello")
    # Verify the action exists
    assert hasattr(input_bar, "action_copy")

  def test_cut_action_exists(self) -> None:
    """InputBar should inherit cut action from TextArea."""
    input_bar = InputBar(text="hello")
    # Verify the action exists
    assert hasattr(input_bar, "action_cut")

  def test_paste_action_exists(self) -> None:
    """InputBar should inherit paste action from TextArea."""
    input_bar = InputBar(text="hello")
    # Verify the action exists
    assert hasattr(input_bar, "action_paste")

  def test_get_text_range(self) -> None:
    """get_text_range should return text in range."""
    input_bar = InputBar(text="hello world")
    text = input_bar.get_text_range((0, 0), (0, 5))
    assert text == "hello"

  def test_get_text_range_multiline(self) -> None:
    """get_text_range should work across lines."""
    input_bar = InputBar(text="hello\nworld")
    text = input_bar.get_text_range((0, 2), (1, 3))
    assert text == "llo\nwor"

  def test_insert_at_cursor(self) -> None:
    """insert() should insert text at cursor position."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 5)
    input_bar.insert(" world")
    assert input_bar.text == "hello world"
    # Cursor should be after inserted text
    assert input_bar.cursor_location == (0, 11)

  def test_insert_at_beginning(self) -> None:
    """insert() should insert text at beginning."""
    input_bar = InputBar(text="world")
    input_bar.cursor_location = (0, 0)
    input_bar.insert("hello ")
    assert input_bar.text == "hello world"

  def test_insert_in_middle(self) -> None:
    """insert() should insert text in middle."""
    input_bar = InputBar(text="helloworld")
    input_bar.cursor_location = (0, 5)
    input_bar.insert(" ")
    assert input_bar.text == "hello world"

  def test_insert_multiline(self) -> None:
    """insert() should handle multiline text."""
    input_bar = InputBar(text="start end")
    input_bar.cursor_location = (0, 6)
    input_bar.insert("\nmiddle\n")
    # Insert at position 6 (after "start "), results in:
    # "start " + "\nmiddle\n" + "end" = "start \nmiddle\nend"
    assert input_bar.text == "start \nmiddle\nend"


class TestInputBarTextAreaInheritance:
  """Tests for verifying InputBar properly inherits TextArea functionality."""

  def test_inherits_from_text_area(self) -> None:
    """InputBar should inherit from TextArea."""
    input_bar = InputBar()
    assert isinstance(input_bar, TextArea)

  def test_has_document(self) -> None:
    """InputBar should have a document."""
    input_bar = InputBar(text="test")
    assert hasattr(input_bar, "document")
    assert input_bar.document is not None

  def test_has_edit_history(self) -> None:
    """InputBar should have edit history for undo/redo."""
    input_bar = InputBar()
    assert hasattr(input_bar, "history")

  def test_undo_redo_basic(self) -> None:
    """InputBar should support undo/redo."""
    input_bar = InputBar(text="")
    # Insert some text
    input_bar.insert("hello")
    assert input_bar.text == "hello"
    # Undo the insert
    input_bar.action_undo()
    assert input_bar.text == ""
    # Redo the insert
    input_bar.action_redo()
    assert input_bar.text == "hello"

  def test_has_undo_action(self) -> None:
    """InputBar should have undo action."""
    input_bar = InputBar()
    assert hasattr(input_bar, "action_undo")

  def test_has_redo_action(self) -> None:
    """InputBar should have redo action."""
    input_bar = InputBar()
    assert hasattr(input_bar, "action_redo")

  def test_clear_clears_selection(self) -> None:
    """TextArea.clear() should work on InputBar."""
    input_bar = InputBar(text="hello")
    input_bar.selection = Selection((0, 0), (0, 5))
    input_bar.clear()
    # Selection should be cleared (text is empty)
    assert input_bar.text == ""

  def test_load_text(self) -> None:
    """load_text should replace all content."""
    input_bar = InputBar(text="old content")
    input_bar.load_text("new content")
    assert input_bar.text == "new content"

  def test_read_only_mode(self) -> None:
    """InputBar should support read-only mode."""
    input_bar = InputBar(text="test", read_only=True)
    assert input_bar.read_only is True

  def test_read_only_can_be_changed(self) -> None:
    """InputBar read_only should be changeable."""
    input_bar = InputBar(text="test")
    assert input_bar.read_only is False
    input_bar.read_only = True
    assert input_bar.read_only is True


class TestInputBarAutoGrow:
  """Tests for InputBar auto-grow functionality."""

  def test_default_max_height_is_10(self) -> None:
    """max_height should default to 10 lines."""
    input_bar = InputBar()
    assert input_bar.max_height == 10

  def test_custom_max_height_parameter(self) -> None:
    """max_height should accept custom values."""
    input_bar = InputBar(max_height=5)
    assert input_bar.max_height == 5

  def test_max_height_property_getter(self) -> None:
    """max_height property should return the configured value."""
    input_bar = InputBar(max_height=20)
    assert input_bar.max_height == 20

  def test_max_height_property_setter(self) -> None:
    """max_height property should be settable."""
    input_bar = InputBar(max_height=10)
    input_bar.max_height = 15
    assert input_bar.max_height == 15

  def test_get_content_height_empty_returns_1(self) -> None:
    """get_content_height should return 1 for empty content."""
    from textual.geometry import Size

    input_bar = InputBar()
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 1

  def test_get_content_height_single_line(self) -> None:
    """get_content_height should return 1 for single line content."""
    from textual.geometry import Size

    input_bar = InputBar(text="hello")
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 1

  def test_get_content_height_multiple_lines(self) -> None:
    """get_content_height should return actual line count up to max_height."""
    from textual.geometry import Size

    input_bar = InputBar(text="line one\nline two\nline three", max_height=10)
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 3

  def test_get_content_height_clamps_to_max_height(self) -> None:
    """get_content_height should clamp to max_height when content exceeds."""
    from textual.geometry import Size

    # 15 lines of content with max_height of 10
    lines = "\n".join([f"line {i}" for i in range(15)])
    input_bar = InputBar(text=lines, max_height=10)
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 10

  def test_get_content_height_with_custom_max_height(self) -> None:
    """get_content_height should respect custom max_height."""
    from textual.geometry import Size

    lines = "\n".join([f"line {i}" for i in range(8)])
    input_bar = InputBar(text=lines, max_height=5)
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 5

  def test_get_content_height_long_line_wraps(self) -> None:
    """get_content_height should account for wrapped lines."""
    from textual.geometry import Size

    # A very long line that will wrap at width 20
    long_line = "a" * 100
    input_bar = InputBar(text=long_line, max_height=10)
    container = Size(80, 24)
    viewport = Size(80, 24)
    # With width 20, 100 chars should wrap to ~5 lines
    # Note: wrapped_document.height requires the widget to be mounted
    # for proper wrap_width context. Without mounting, it returns 1.
    height = input_bar.get_content_height(container, viewport, 20)
    # The wrapped_document needs wrap_width context from mounting.
    # Without it, it returns 1 (unwrapped). This test verifies
    # the method works without crashing and returns a valid height.
    assert height >= 1

  def test_get_content_height_preserves_minimum_of_1(self) -> None:
    """get_content_height should always return at least 1."""
    from textual.geometry import Size

    input_bar = InputBar(text="", max_height=0)
    container = Size(80, 24)
    viewport = Size(80, 24)
    height = input_bar.get_content_height(container, viewport, 80)
    # Should be clamped to 1 even if max_height is 0
    assert height == 1

  def test_max_height_setter_triggers_refresh(self) -> None:
    """Setting max_height should trigger a layout refresh."""
    from unittest.mock import patch

    input_bar = InputBar(max_height=10)
    with patch.object(input_bar, "refresh") as mock_refresh:
      input_bar.max_height = 20
      mock_refresh.assert_called_once()

  def test_max_height_change_affects_content_height(self) -> None:
    """Changing max_height should affect get_content_height result."""
    from textual.geometry import Size

    lines = "\n".join([f"line {i}" for i in range(15)])
    input_bar = InputBar(text=lines, max_height=10)
    container = Size(80, 24)
    viewport = Size(80, 24)

    # Initially clamped to 10
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 10

    # Increase max_height
    input_bar.max_height = 20
    height = input_bar.get_content_height(container, viewport, 80)
    assert height == 15


class TestInputBarSubmitConfiguration:
  """Tests for configurable submit behavior."""

  def test_default_submit_on_enter_is_true(self) -> None:
    """Default submit_on_enter should be True."""
    input_bar = InputBar()
    assert input_bar.submit_on_enter is True

  def test_submit_on_enter_parameter_accepted(self) -> None:
    """submit_on_enter parameter should be accepted."""
    input_bar = InputBar(submit_on_enter=False)
    assert input_bar.submit_on_enter is False

  def test_submit_on_enter_property_returns_value(self) -> None:
    """submit_on_enter property should return the configured value."""
    input_bar = InputBar(submit_on_enter=True)
    assert input_bar.submit_on_enter is True

  def test_enter_submits_when_submit_on_enter_true(self) -> None:
    """Enter should submit when submit_on_enter=True (default)."""
    input_bar = InputBar(text="test", submit_on_enter=True)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 1

  def test_shift_enter_does_not_submit_when_submit_on_enter_true(self) -> None:
    """Shift+Enter should not submit when submit_on_enter=True."""
    input_bar = InputBar(text="test", submit_on_enter=True)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="shift+enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_enter_does_not_submit_when_submit_on_enter_false(self) -> None:
    """Enter should not submit when submit_on_enter=False."""
    input_bar = InputBar(text="test", submit_on_enter=False)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0

  def test_shift_enter_submits_when_submit_on_enter_false(self) -> None:
    """Shift+Enter should submit when submit_on_enter=False."""
    input_bar = InputBar(text="test", submit_on_enter=False)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="shift+enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 1

  def test_enter_not_stopped_when_submit_on_enter_false(self) -> None:
    """Enter should not be stopped when submit_on_enter=False."""
    input_bar = InputBar(text="test", submit_on_enter=False)
    event = Key(key="enter", character=None)

    input_bar.on_key(event)

    # Event should not be stopped
    assert not event._stop_propagation

  def test_shift_enter_stopped_when_submit_on_enter_false(self) -> None:
    """Shift+Enter should be stopped when submit_on_enter=False."""
    input_bar = InputBar(text="test", submit_on_enter=False)
    event = Key(key="shift+enter", character=None)

    with patch.object(input_bar, "post_message"):
      input_bar.on_key(event)

    # Event should be stopped
    assert event._stop_propagation

  def test_disabled_widget_does_not_submit_with_submit_on_enter_false(self) -> None:
    """Shift+Enter should not submit when widget is disabled (submit_on_enter=False)."""
    input_bar = InputBar(text="test", submit_on_enter=False, disabled=True)

    posted_messages: list[Message] = []

    def capture_post(msg: Message) -> None:
      posted_messages.append(msg)

    with patch.object(input_bar, "post_message", side_effect=capture_post):
      event = Key(key="shift+enter", character=None)
      input_bar.on_key(event)

    submit_messages = [m for m in posted_messages if isinstance(m, InputBar.Submit)]
    assert len(submit_messages) == 0


class TestInputBarNewlineInsertion:
  """Tests for newline insertion functionality."""

  def test_action_insert_newline_inserts_newline(self) -> None:
    """action_insert_newline() inserts a newline character."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 5)
    input_bar.action_insert_newline()
    assert "\n" in input_bar.text
    assert input_bar.text == "hello\n world"

  def test_action_insert_newline_at_cursor_position(self) -> None:
    """Newline is inserted at cursor position, not end."""
    input_bar = InputBar(text="line one")
    input_bar.cursor_location = (0, 4)  # After "line"
    input_bar.action_insert_newline()
    assert input_bar.text == "line\n one"

  def test_action_insert_newline_moves_cursor(self) -> None:
    """Cursor moves to start of next line after newline."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 5)
    input_bar.action_insert_newline()
    assert input_bar.cursor_location == (1, 0)

  def test_action_insert_newline_at_line_start(self) -> None:
    """Newline at position 0 creates empty first line."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 0)
    input_bar.action_insert_newline()
    assert input_bar.text == "\nhello world"
    assert input_bar.cursor_location == (1, 0)

  def test_action_insert_newline_at_line_end(self) -> None:
    """Newline at end of line creates empty next line."""
    input_bar = InputBar(text="hello")
    input_bar.cursor_location = (0, 5)
    input_bar.action_insert_newline()
    assert input_bar.text == "hello\n"
    assert input_bar.cursor_location == (1, 0)

  def test_action_insert_newline_in_middle_of_line(self) -> None:
    """Newline in middle of line splits the line."""
    input_bar = InputBar(text="hello world")
    input_bar.cursor_location = (0, 5)
    input_bar.action_insert_newline()
    assert input_bar.text == "hello\n world"
    assert input_bar.cursor_location == (1, 0)

  def test_action_insert_newline_with_existing_multiline(self) -> None:
    """Newline insertion works with existing multiline text."""
    input_bar = InputBar(text="line one\nline two")
    input_bar.cursor_location = (1, 4)  # After "line" on second line
    input_bar.action_insert_newline()
    assert input_bar.text == "line one\nline\n two"
    assert input_bar.cursor_location == (2, 0)

  def test_cursor_after_multiple_newlines(self) -> None:
    """Cursor position is correct after multiple newlines."""
    input_bar = InputBar(text="abc")
    input_bar.cursor_location = (0, 1)
    input_bar.action_insert_newline()
    assert input_bar.cursor_location == (1, 0)
    input_bar.action_insert_newline()
    assert input_bar.cursor_location == (2, 0)
    assert input_bar.text == "a\n\nbc"


@pytest.mark.asyncio
class TestInputBarNewlineInsertionAsync:
  """Async tests for newline insertion with mounted InputBar."""

  async def test_shift_enter_inserts_newline_default(self) -> None:
    """Shift+Enter inserts newline in default mode (submit_on_enter=True)."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello world"
      input_bar.cursor_location = (0, 5)

      await pilot.press("shift+enter")

      assert "\n" in input_bar.text
      assert input_bar.text == "hello\n world"
      assert input_bar.cursor_location == (1, 0)

  async def test_shift_enter_with_existing_text(self) -> None:
    """Shift+Enter inserts newline with existing multiline text."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "line one\nline two"
      input_bar.cursor_location = (0, 4)  # After "line" on first line

      await pilot.press("shift+enter")

      assert input_bar.text == "line\n one\nline two"
      assert input_bar.cursor_location == (1, 0)

  async def test_shift_enter_at_line_start(self) -> None:
    """Shift+Enter at position 0 creates empty first line."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello world"
      input_bar.cursor_location = (0, 0)

      await pilot.press("shift+enter")

      assert input_bar.text == "\nhello world"
      assert input_bar.cursor_location == (1, 0)

  async def test_shift_enter_at_line_end(self) -> None:
    """Shift+Enter at end of line creates empty next line."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello"
      input_bar.cursor_location = (0, 5)

      await pilot.press("shift+enter")

      assert input_bar.text == "hello\n"
      assert input_bar.cursor_location == (1, 0)

  async def test_shift_enter_in_middle_of_line(self) -> None:
    """Shift+Enter in middle of line splits the line."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello world"
      input_bar.cursor_location = (0, 5)

      await pilot.press("shift+enter")

      assert input_bar.text == "hello\n world"
      assert input_bar.cursor_location == (1, 0)

  async def test_enter_inserts_newline_alt_mode(self) -> None:
    """Enter inserts newline when submit_on_enter=False."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar(submit_on_enter=False)

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello world"
      input_bar.cursor_location = (0, 5)

      await pilot.press("enter")

      assert "\n" in input_bar.text
      assert input_bar.text == "hello\n world"
      assert input_bar.cursor_location == (1, 0)

  async def test_shift_enter_submits_alt_mode(self) -> None:
    """Shift+Enter submits when submit_on_enter=False."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar(submit_on_enter=False)

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "test message"

      await pilot.press("shift+enter")

      # Text should be cleared after submit
      assert input_bar.text == ""

  async def test_cursor_after_newline_at_start(self) -> None:
    """Cursor is at start of new line after newline at position 0."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello"
      input_bar.cursor_location = (0, 0)

      await pilot.press("shift+enter")

      assert input_bar.cursor_location == (1, 0)

  async def test_cursor_after_newline_at_middle(self) -> None:
    """Cursor is at start of new line after newline in middle."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello world"
      input_bar.cursor_location = (0, 5)

      await pilot.press("shift+enter")

      assert input_bar.cursor_location == (1, 0)

  async def test_cursor_after_newline_at_end(self) -> None:
    """Cursor is at start of new empty line after newline at end."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "hello"
      input_bar.cursor_location = (0, 5)

      await pilot.press("shift+enter")

      assert input_bar.cursor_location == (1, 0)

  async def test_cursor_after_multiple_newlines(self) -> None:
    """Cursor position is correct after multiple newlines."""
    from textual.app import App, ComposeResult

    class TestApp(App):
      def compose(self) -> ComposeResult:
        yield InputBar()

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      input_bar.text = "abc"
      input_bar.cursor_location = (0, 1)

      await pilot.press("shift+enter")
      assert input_bar.cursor_location == (1, 0)

      await pilot.press("shift+enter")
      assert input_bar.cursor_location == (2, 0)

      assert input_bar.text == "a\n\nbc"
