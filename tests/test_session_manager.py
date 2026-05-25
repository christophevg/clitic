"""Tests for SessionManager."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from clitic.exceptions import SessionError
from clitic.session import SessionInfo, SessionManager
from clitic.widgets.conversation import BlockInfo


class TestSessionManagerInstantiation:
  """Tests for SessionManager instantiation."""

  def test_session_manager_can_be_instantiated(self) -> None:
    """SessionManager should be instantiable."""
    manager = SessionManager()
    assert manager is not None

  def test_session_manager_default_persistence_disabled(self) -> None:
    """SessionManager should default to persistence disabled."""
    manager = SessionManager()
    assert manager.persistence_enabled is False

  def test_session_manager_accepts_persistence_enabled(self) -> None:
    """SessionManager should accept persistence_enabled parameter."""
    manager = SessionManager(persistence_enabled=True)
    assert manager.persistence_enabled is True

  def test_session_manager_default_session_dir(self) -> None:
    """SessionManager should have default session directory."""
    manager = SessionManager()
    expected_dir = Path.home() / ".local" / "share" / "clitic" / "sessions"
    assert manager.session_dir == expected_dir

  def test_session_manager_accepts_custom_session_dir(self, tmp_path: Path) -> None:
    """SessionManager should accept custom session directory."""
    custom_dir = tmp_path / "custom_sessions"
    manager = SessionManager(session_dir=custom_dir)
    assert manager.session_dir == custom_dir


class TestSessionManagerStartSession:
  """Tests for SessionManager start_session method."""

  def test_start_session_creates_directory(self, tmp_path: Path) -> None:
    """start_session should create session directory."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    assert (tmp_path / "sessions").exists()

  def test_start_session_stores_session_id(self, tmp_path: Path) -> None:
    """start_session should store session ID."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    assert manager._current_session_id == "test-session-id"

  def test_start_session_resets_block_count(self, tmp_path: Path) -> None:
    """start_session should reset block count."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager._block_count = 10  # Set to non-zero
    manager.start_session("test-session-id")

    assert manager._block_count == 0

  def test_start_session_no_op_when_disabled(self, tmp_path: Path) -> None:
    """start_session should do nothing when persistence disabled."""
    manager = SessionManager(persistence_enabled=False, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    # Directory should not be created
    assert not (tmp_path / "sessions").exists()
    assert manager._current_session_id is None


class TestSessionManagerSaveBlock:
  """Tests for SessionManager save_block method."""

  def test_save_block_writes_to_file(self, tmp_path: Path) -> None:
    """save_block should write block to JSONL file."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    block = BlockInfo(
      block_id="test-session-id-0",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    manager.save_block(block)
    manager.close_session()

    # Check file was created
    session_file = tmp_path / "sessions" / "test-session-id.jsonl"
    assert session_file.exists()

    # Check content
    content = session_file.read_text()
    assert "test-session-id-0" in content
    assert "Hello" in content

  def test_save_block_increments_block_count(self, tmp_path: Path) -> None:
    """save_block should increment block count."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    block = BlockInfo(
      block_id="test-session-id-0",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    manager.save_block(block)

    assert manager._block_count == 1

  def test_save_block_raises_when_disabled(self, tmp_path: Path) -> None:
    """save_block should raise SessionError when persistence disabled."""
    manager = SessionManager(persistence_enabled=False, session_dir=tmp_path / "sessions")

    block = BlockInfo(
      block_id="test-session-id-0",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )

    try:
      manager.save_block(block)
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "save"

  def test_save_block_raises_when_no_active_session(self, tmp_path: Path) -> None:
    """save_block should raise SessionError when no active session."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")

    block = BlockInfo(
      block_id="test-session-id-0",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )

    try:
      manager.save_block(block)
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "save"

  def test_save_block_appends_to_existing_file(self, tmp_path: Path) -> None:
    """save_block should append to existing session file."""
    manager = SessionManager(persistence_enabled=True, session_dir=tmp_path / "sessions")
    manager.start_session("test-session-id")

    block1 = BlockInfo(
      block_id="test-session-id-0",
      role="user",
      content="Hello",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=0,
    )
    block2 = BlockInfo(
      block_id="test-session-id-1",
      role="assistant",
      content="Hi",
      metadata={},
      timestamp=datetime.now(timezone.utc),
      sequence=1,
    )
    manager.save_block(block1)
    manager.save_block(block2)
    manager.close_session()

    # Check file has two lines
    session_file = tmp_path / "sessions" / "test-session-id.jsonl"
    lines = session_file.read_text().strip().split("\n")
    assert len(lines) == 2


class TestSessionManagerResumeSession:
  """Tests for SessionManager resume_session method."""

  def test_resume_session_loads_blocks(self, tmp_path: Path) -> None:
    """resume_session should load blocks from file."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session-id.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-id-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    blocks = manager.resume_session("test-session-id")

    assert len(blocks) == 1
    assert blocks[0].block_id == "test-session-id-0"
    assert blocks[0].role == "user"
    assert blocks[0].content == "Hello"

  def test_resume_session_raises_when_not_found(self, tmp_path: Path) -> None:
    """resume_session should raise SessionError when file not found."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    try:
      manager.resume_session("non-existent-session")
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "resume"
      assert "not found" in str(e).lower()

  def test_resume_session_handles_multiple_blocks(self, tmp_path: Path) -> None:
    """resume_session should handle multiple blocks."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file with multiple blocks
    session_file = tmp_path / "sessions" / "test-session-id.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-id-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-session-id-1","role":"assistant","content":"Hi","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
    )

    blocks = manager.resume_session("test-session-id")

    assert len(blocks) == 2
    assert blocks[0].sequence == 0
    assert blocks[1].sequence == 1

  def test_resume_session_preserves_metadata(self, tmp_path: Path) -> None:
    """resume_session should preserve block metadata."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file with metadata
    session_file = tmp_path / "sessions" / "test-session-id.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-id-0","role":"user","content":"Hello","metadata":{"key":"value"},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    blocks = manager.resume_session("test-session-id")

    assert blocks[0].metadata == {"key": "value"}


class TestSessionManagerListSessions:
  """Tests for SessionManager list_sessions method."""

  def test_list_sessions_returns_empty_when_no_sessions(self, tmp_path: Path) -> None:
    """list_sessions should return empty list when no sessions."""
    manager = SessionManager(session_dir=tmp_path / "sessions")
    sessions = manager.list_sessions()

    assert sessions == []

  def test_list_sessions_returns_sessions(self, tmp_path: Path) -> None:
    """list_sessions should return available sessions."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create session files
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "session-1.jsonl").write_text(
      '{"block_id":"session-1-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )
    (session_dir / "session-2.jsonl").write_text(
      '{"block_id":"session-2-0","role":"user","content":"World","metadata":{},"timestamp":"2024-01-15T11:00:00+00:00","sequence":0}\n'
    )

    sessions = manager.list_sessions()

    assert len(sessions) == 2
    session_ids = {s.session_id for s in sessions}
    assert "session-1" in session_ids
    assert "session-2" in session_ids

  def test_list_sessions_returns_session_info(self, tmp_path: Path) -> None:
    """list_sessions should return SessionInfo objects."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create session file
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "test-session.jsonl").write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    sessions = manager.list_sessions()

    assert len(sessions) == 1
    assert isinstance(sessions[0], SessionInfo)
    assert sessions[0].session_id == "test-session"
    assert sessions[0].block_count == 1
    assert sessions[0].file_path == session_dir / "test-session.jsonl"

  def test_list_sessions_sorted_by_updated_at(self, tmp_path: Path) -> None:
    """list_sessions should sort sessions by updated_at descending."""
    import time

    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create session files with different times
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "older.jsonl").write_text(
      '{"block_id":"older-0","role":"user","content":"Old","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )
    time.sleep(0.1)  # Ensure different mtime
    (session_dir / "newer.jsonl").write_text(
      '{"block_id":"newer-0","role":"user","content":"New","metadata":{},"timestamp":"2024-01-15T11:00:00+00:00","sequence":0}\n'
    )

    sessions = manager.list_sessions()

    # Newer should come first
    assert sessions[0].session_id == "newer"
    assert sessions[1].session_id == "older"


class TestSessionManagerDeleteSession:
  """Tests for SessionManager delete_session method."""

  def test_delete_session_removes_file(self, tmp_path: Path) -> None:
    """delete_session should remove session file."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create session file
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "test-session.jsonl"
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    manager.delete_session("test-session")

    assert not session_file.exists()

  def test_delete_session_raises_when_not_found(self, tmp_path: Path) -> None:
    """delete_session should raise SessionError when file not found."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    try:
      manager.delete_session("non-existent-session")
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "delete"
      assert "not found" in str(e).lower()


class TestSessionError:
  """Tests for SessionError exception."""

  def test_session_error_with_all_fields(self) -> None:
    """SessionError should format correctly with all fields."""
    error = SessionError(
      session_id="test-session",
      operation="save",
      message="Failed to write",
    )
    assert "test-session" in str(error)
    assert "save" in str(error)
    assert "Failed to write" in str(error)

  def test_session_error_without_session_id(self) -> None:
    """SessionError should format correctly without session_id."""
    error = SessionError(
      session_id=None,
      operation="start",
      message="Failed to create directory",
    )
    assert "start" in str(error)
    assert "Failed to create directory" in str(error)
    assert "for session" not in str(error)

  def test_session_error_without_message(self) -> None:
    """SessionError should format correctly without message."""
    error = SessionError(
      session_id="test-session",
      operation="delete",
    )
    assert "test-session" in str(error)
    assert "delete" in str(error)

  def test_session_error_repr(self) -> None:
    """SessionError repr should contain all fields."""
    error = SessionError(
      session_id="test-session",
      operation="save",
      message="Failed to write",
    )
    repr_str = repr(error)
    assert "test-session" in repr_str
    assert "save" in repr_str
    assert "Failed to write" in repr_str


class TestSessionInfo:
  """Tests for SessionInfo dataclass."""

  def test_session_info_is_frozen(self) -> None:
    """SessionInfo should be frozen (immutable)."""
    info = SessionInfo(
      session_id="test-session",
      block_count=5,
      created_at=datetime.now(timezone.utc),
      updated_at=datetime.now(timezone.utc),
      file_path=Path("/tmp/test.jsonl"),
    )
    try:
      info.block_count = 10  # type: ignore[misc]
      raise AssertionError("SessionInfo should be frozen")
    except (AttributeError, TypeError):
      pass

  def test_session_info_attributes(self) -> None:
    """SessionInfo should have all required attributes."""
    created = datetime.now(timezone.utc)
    updated = datetime.now(timezone.utc)
    info = SessionInfo(
      session_id="test-session",
      block_count=5,
      created_at=created,
      updated_at=updated,
      file_path=Path("/tmp/test.jsonl"),
    )
    assert info.session_id == "test-session"
    assert info.block_count == 5
    assert info.created_at == created
    assert info.updated_at == updated
    assert info.file_path == Path("/tmp/test.jsonl")


class TestConversationWithPersistence:
  """Tests for Conversation with session persistence."""

  def test_conversation_with_persistence_enabled(self, tmp_path: Path) -> None:
    """Conversation should accept persistence_enabled parameter."""
    from clitic import Conversation

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # Session manager should exist
    assert conversation._session_manager is not None

  def test_conversation_saves_to_file(self, tmp_path: Path) -> None:
    """Conversation should save blocks to file when persistence enabled."""
    from clitic import Conversation

    conversation = Conversation(
      persistence_enabled=True,
      session_dir=tmp_path / "sessions",
    )
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # Close the session
    if conversation._session_manager is not None:
      conversation._session_manager.close_session()

    # Check file was created
    session_file = tmp_path / "sessions" / f"{conversation.session_id}.jsonl"
    assert session_file.exists()

  def test_conversation_resume(self, tmp_path: Path) -> None:
    """Conversation.resume should restore blocks from file."""
    from clitic import Conversation

    # Create a session file
    session_id = "test-resume-session"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{session_id}.jsonl"
    session_file.write_text(
      '{"block_id":"test-resume-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-resume-session-1","role":"assistant","content":"Hi","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
    )

    conversation = Conversation.resume(session_id, session_dir=session_dir)

    # Check blocks were restored
    assert conversation.block_count == 2
    assert conversation.session_id == session_id

    # Check sequence counter was restored
    block0 = conversation.get_block_at_index(0)
    block1 = conversation.get_block_at_index(1)
    assert block0 is not None and block0.content == "Hello"
    assert block1 is not None and block1.content == "Hi"

  def test_conversation_without_persistence(self) -> None:
    """Conversation should work without persistence enabled."""
    from clitic import Conversation

    conversation = Conversation(persistence_enabled=False)
    with patch.object(conversation, "call_after_refresh"):
      conversation.append("user", "Hello")

    # Session manager should not exist
    assert conversation._session_manager is None

    # But blocks should still be added
    assert conversation.block_count == 1


class TestSessionManagerLoadBlockBySequence:
  """Tests for SessionManager load_block_by_sequence method."""

  def test_load_block_by_sequence_returns_block(self, tmp_path: Path) -> None:
    """load_block_by_sequence should return the correct block."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-session-1","role":"assistant","content":"Hi","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
    )

    block = manager.load_block_by_sequence("test-session", 0)

    assert block is not None
    assert block.sequence == 0
    assert block.content == "Hello"
    assert block.role == "user"

  def test_load_block_by_sequence_returns_none_for_missing(self, tmp_path: Path) -> None:
    """load_block_by_sequence should return None for non-existent sequence."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    block = manager.load_block_by_sequence("test-session", 99)

    assert block is None

  def test_load_block_by_sequence_raises_for_missing_file(self, tmp_path: Path) -> None:
    """load_block_by_sequence should raise SessionError for missing file."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    try:
      manager.load_block_by_sequence("non-existent-session", 0)
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "load_block"
      assert "not found" in str(e).lower()

  def test_load_block_by_sequence_skips_malformed_lines(self, tmp_path: Path) -> None:
    """load_block_by_sequence should skip malformed lines."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file with malformed line
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      "malformed line\n"
      '{"block_id":"test-session-1","role":"assistant","content":"Hi","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
    )

    block = manager.load_block_by_sequence("test-session", 1)

    assert block is not None
    assert block.sequence == 1


class TestSessionManagerLoadBlocksBySequenceRange:
  """Tests for SessionManager load_blocks_by_sequence_range method."""

  def test_load_blocks_by_sequence_range_returns_blocks(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should return blocks in range."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Zero","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-session-1","role":"assistant","content":"One","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
      '{"block_id":"test-session-2","role":"user","content":"Two","metadata":{},"timestamp":"2024-01-15T10:00:02+00:00","sequence":2}\n'
      '{"block_id":"test-session-3","role":"assistant","content":"Three","metadata":{},"timestamp":"2024-01-15T10:00:03+00:00","sequence":3}\n'
    )

    blocks = manager.load_blocks_by_sequence_range("test-session", 1, 2)

    assert len(blocks) == 2
    assert blocks[0].sequence == 1
    assert blocks[1].sequence == 2

  def test_load_blocks_by_sequence_range_returns_sorted(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should return sorted blocks."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file with blocks out of order
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-2","role":"user","content":"Two","metadata":{},"timestamp":"2024-01-15T10:00:02+00:00","sequence":2}\n'
      '{"block_id":"test-session-0","role":"user","content":"Zero","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-session-1","role":"assistant","content":"One","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
    )

    blocks = manager.load_blocks_by_sequence_range("test-session", 0, 2)

    assert len(blocks) == 3
    assert blocks[0].sequence == 0
    assert blocks[1].sequence == 1
    assert blocks[2].sequence == 2

  def test_load_blocks_by_sequence_range_returns_empty_for_no_matches(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should return empty list for no matches."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    blocks = manager.load_blocks_by_sequence_range("test-session", 10, 20)

    assert blocks == []

  def test_load_blocks_by_sequence_range_raises_for_missing_file(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should raise SessionError for missing file."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    try:
      manager.load_blocks_by_sequence_range("non-existent-session", 0, 10)
      raise AssertionError("Should have raised SessionError")
    except SessionError as e:
      assert e.operation == "load_blocks"
      assert "not found" in str(e).lower()

  def test_load_blocks_by_sequence_range_inclusive_range(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should include both start and end."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Zero","metadata":{},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
      '{"block_id":"test-session-1","role":"assistant","content":"One","metadata":{},"timestamp":"2024-01-15T10:00:01+00:00","sequence":1}\n'
      '{"block_id":"test-session-2","role":"user","content":"Two","metadata":{},"timestamp":"2024-01-15T10:00:02+00:00","sequence":2}\n'
    )

    blocks = manager.load_blocks_by_sequence_range("test-session", 1, 1)

    assert len(blocks) == 1
    assert blocks[0].sequence == 1

  def test_load_blocks_by_sequence_range_preserves_metadata(self, tmp_path: Path) -> None:
    """load_blocks_by_sequence_range should preserve block metadata."""
    manager = SessionManager(session_dir=tmp_path / "sessions")

    # Create a session file with metadata
    session_file = tmp_path / "sessions" / "test-session.jsonl"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(
      '{"block_id":"test-session-0","role":"user","content":"Hello","metadata":{"key":"value"},"timestamp":"2024-01-15T10:00:00+00:00","sequence":0}\n'
    )

    blocks = manager.load_blocks_by_sequence_range("test-session", 0, 0)

    assert len(blocks) == 1
    assert blocks[0].metadata == {"key": "value"}
