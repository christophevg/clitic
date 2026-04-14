"""Session persistence management.

This module provides session persistence for Conversation widgets,
allowing conversations to be saved to and resumed from JSONL files.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

from clitic.exceptions import SessionError
from clitic.widgets.conversation import BlockInfo

__all__ = ["SessionError", "SessionInfo", "SessionManager"]

# Default session directory: ~/.local/share/clitic/sessions
DEFAULT_SESSION_DIR = Path.home() / ".local" / "share" / "clitic" / "sessions"


@dataclass(frozen=True)
class SessionInfo:
  """Immutable information about a saved session.

  Attributes:
      session_id: The unique identifier for the session.
      block_count: Number of blocks in the session.
      created_at: When the session was created.
      updated_at: When the session was last modified.
      file_path: Path to the session file.
  """

  session_id: str
  block_count: int
  created_at: datetime
  updated_at: datetime
  file_path: Path


class SessionManager:
  """Manages conversation session persistence.

  Handles saving conversation blocks to JSONL files and resuming
  sessions from previously saved files.

  Attributes:
      persistence_enabled: Whether persistence is enabled.
      session_dir: Directory where session files are stored.

  Example:
      ```python
      from clitic.session import SessionManager

      # Create manager with persistence enabled
      manager = SessionManager(persistence_enabled=True)
      manager.start_session("my-session-uuid")

      # Save blocks
      manager.save_block(block_info)

      # Resume a session
      blocks = manager.resume_session("my-session-uuid")
      ```
  """

  def __init__(
    self,
    persistence_enabled: bool = False,
    session_dir: Path | None = None,
  ) -> None:
    """Initialize the SessionManager.

    Args:
        persistence_enabled: Whether to enable automatic saving.
        session_dir: Optional custom session directory.
    """
    self.persistence_enabled = persistence_enabled
    self.session_dir = session_dir or DEFAULT_SESSION_DIR
    self._current_session_id: str | None = None
    self._file_handle: TextIO | None = None
    self._block_count: int = 0

  def start_session(self, session_id: str) -> None:
    """Start a new session for persistence.

    Creates the session directory if needed and opens the session file
    for appending blocks.

    Args:
        session_id: The unique identifier for this session.

    Raises:
        SessionError: If unable to create session directory or file.
    """
    if not self.persistence_enabled:
      return

    try:
      # Ensure session directory exists
      self.session_dir.mkdir(parents=True, exist_ok=True)

      # Store session ID
      self._current_session_id = session_id
      self._block_count = 0

      # Open file for appending (will be opened on first save)
      # We use lazy opening to avoid creating empty files for sessions
      # that don't have any blocks
    except OSError as e:
      raise SessionError(
        session_id=session_id,
        operation="start",
        message=f"Failed to create session directory: {e}",
      ) from e

  def _get_session_file_path(self, session_id: str) -> Path:
    """Get the file path for a session.

    Args:
        session_id: The session identifier.

    Returns:
        Path to the session file.
    """
    return self.session_dir / f"{session_id}.jsonl"

  def _open_file_for_writing(self) -> None:
    """Open the session file for writing if not already open."""
    if self._file_handle is None and self._current_session_id is not None:
      file_path = self._get_session_file_path(self._current_session_id)
      # Use 'a' mode to append to existing file
      self._file_handle = open(file_path, "a", encoding="utf-8")  # noqa: SIM115

  def save_block(self, block: BlockInfo) -> None:
    """Save a block to the session file.

    Serializes the block to JSON and appends it as a new line.
    The write is flushed immediately for durability.

    Args:
        block: The block information to save.

    Raises:
        SessionError: If persistence is not enabled or write fails.
    """
    if not self.persistence_enabled:
      raise SessionError(
        session_id=self._current_session_id,
        operation="save",
        message="Persistence is not enabled",
      )

    if self._current_session_id is None:
      raise SessionError(
        session_id=None,
        operation="save",
        message="No active session",
      )

    try:
      self._open_file_for_writing()

      if self._file_handle is None:
        raise SessionError(
          session_id=self._current_session_id,
          operation="save",
          message="Failed to open session file",
        )

      # Serialize block to JSON
      data = {
        "block_id": block.block_id,
        "role": block.role,
        "content": block.content,
        "metadata": block.metadata,
        "timestamp": block.timestamp.isoformat(),
        "sequence": block.sequence,
      }

      # Write as JSON line with newline
      json_line = json.dumps(data, ensure_ascii=False)
      self._file_handle.write(json_line + "\n")
      self._file_handle.flush()  # Ensure immediate write
      os.fsync(self._file_handle.fileno())
      self._block_count += 1

    except OSError as e:
      raise SessionError(
        session_id=self._current_session_id,
        operation="save",
        message=f"Failed to write block: {e}",
      ) from e

  def close_session(self) -> None:
    """Close the current session file.

    Safe to call even if no session is active.
    """
    if self._file_handle is not None:
      try:
        self._file_handle.close()
      except OSError:
        pass  # Ignore close errors
      finally:
        self._file_handle = None

    self._current_session_id = None
    self._block_count = 0

  def resume_session(self, session_id: str) -> list[BlockInfo]:
    """Resume a session from a previously saved file.

    Loads all blocks from the session file into memory.

    Args:
        session_id: The session ID to resume.

    Returns:
        List of BlockInfo objects from the session.

    Raises:
        SessionError: If session file not found or invalid.
    """
    file_path = self._get_session_file_path(session_id)

    if not file_path.exists():
      raise SessionError(
        session_id=session_id,
        operation="resume",
        message="Session file not found",
      )

    blocks: list[BlockInfo] = []

    try:
      with open(file_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
          line = line.strip()
          if not line:
            continue  # Skip empty lines

          try:
            data = json.loads(line)
          except json.JSONDecodeError as e:
            raise SessionError(
              session_id=session_id,
              operation="resume",
              message=f"Invalid JSON at line {line_num}: {e}",
            ) from e

          try:
            # Parse timestamp from ISO format
            timestamp = datetime.fromisoformat(data["timestamp"])
            # Ensure timezone awareness
            if timestamp.tzinfo is None:
              timestamp = timestamp.replace(tzinfo=timezone.utc)

            block = BlockInfo(
              block_id=data["block_id"],
              role=data["role"],
              content=data["content"],
              metadata=data.get("metadata", {}),
              timestamp=timestamp,
              sequence=data["sequence"],
            )
            blocks.append(block)
          except (KeyError, ValueError) as e:
            raise SessionError(
              session_id=session_id,
              operation="resume",
              message=f"Invalid block data at line {line_num}: {e}",
            ) from e

    except OSError as e:
      raise SessionError(
        session_id=session_id,
        operation="resume",
        message=f"Failed to read session file: {e}",
      ) from e

    return blocks

  def list_sessions(self) -> list[SessionInfo]:
    """List all available sessions.

    Scans the session directory for .jsonl files and returns
    information about each session.

    Returns:
        List of SessionInfo objects for all sessions.
    """
    sessions: list[SessionInfo] = []

    if not self.session_dir.exists():
      return sessions

    for file_path in self.session_dir.glob("*.jsonl"):
      session_id = file_path.stem

      try:
        # Get file stats
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # Count blocks by counting non-empty lines
        block_count = 0
        with open(file_path, encoding="utf-8") as f:
          for line in f:
            if line.strip():
              block_count += 1

        session_info = SessionInfo(
          session_id=session_id,
          block_count=block_count,
          created_at=created_at,
          updated_at=updated_at,
          file_path=file_path,
        )
        sessions.append(session_info)

      except OSError:
        # Skip files that can't be read
        continue

    # Sort by updated_at descending (most recent first)
    sessions.sort(key=lambda s: s.updated_at, reverse=True)

    return sessions

  def delete_session(self, session_id: str) -> None:
    """Delete a session file.

    Args:
        session_id: The session ID to delete.

    Raises:
        SessionError: If session file not found or deletion fails.
    """
    file_path = self._get_session_file_path(session_id)

    if not file_path.exists():
      raise SessionError(
        session_id=session_id,
        operation="delete",
        message="Session file not found",
      )

    try:
      file_path.unlink()
    except OSError as e:
      raise SessionError(
        session_id=session_id,
        operation="delete",
        message=f"Failed to delete session file: {e}",
      ) from e

  def load_block_by_sequence(self, session_id: str, sequence: int) -> BlockInfo | None:
    """Load a single block by its sequence number.

    Scans the session file for a block with the matching sequence number.
    This is used for lazy loading of pruned blocks.

    Args:
        session_id: The session ID to load from.
        sequence: The sequence number of the block to load.

    Returns:
        BlockInfo if found, None otherwise.

    Raises:
        SessionError: If session file not found or invalid.
    """
    file_path = self._get_session_file_path(session_id)

    if not file_path.exists():
      raise SessionError(
        session_id=session_id,
        operation="load_block",
        message="Session file not found",
      )

    try:
      with open(file_path, encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line:
            continue

          try:
            data = json.loads(line)
            if data.get("sequence") == sequence:
              # Found the block
              timestamp = datetime.fromisoformat(data["timestamp"])
              if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

              return BlockInfo(
                block_id=data["block_id"],
                role=data["role"],
                content=data["content"],
                metadata=data.get("metadata", {}),
                timestamp=timestamp,
                sequence=data["sequence"],
              )
          except (json.JSONDecodeError, KeyError, ValueError):
            # Skip malformed lines but continue searching
            continue

      return None

    except OSError as e:
      raise SessionError(
        session_id=session_id,
        operation="load_block",
        message=f"Failed to read session file: {e}",
      ) from e

  def load_blocks_by_sequence_range(
    self, session_id: str, start: int, end: int
  ) -> list[BlockInfo]:
    """Load blocks within a sequence range.

    Loads all blocks with sequence numbers in the range [start, end].
    This is used for restoring pruned blocks.

    Args:
        session_id: The session ID to load from.
        start: The starting sequence number (inclusive).
        end: The ending sequence number (inclusive).

    Returns:
        List of BlockInfo objects sorted by sequence number.

    Raises:
        SessionError: If session file not found or invalid.
    """
    file_path = self._get_session_file_path(session_id)

    if not file_path.exists():
      raise SessionError(
        session_id=session_id,
        operation="load_blocks",
        message="Session file not found",
      )

    blocks: list[BlockInfo] = []

    try:
      with open(file_path, encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line:
            continue

          try:
            data = json.loads(line)
            seq = data.get("sequence")
            if seq is not None and start <= seq <= end:
              timestamp = datetime.fromisoformat(data["timestamp"])
              if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

              block = BlockInfo(
                block_id=data["block_id"],
                role=data["role"],
                content=data["content"],
                metadata=data.get("metadata", {}),
                timestamp=timestamp,
                sequence=seq,
              )
              blocks.append(block)
          except (json.JSONDecodeError, KeyError, ValueError):
            # Skip malformed lines but continue parsing
            continue

    except OSError as e:
      raise SessionError(
        session_id=session_id,
        operation="load_blocks",
        message=f"Failed to read session file: {e}",
      ) from e

    # Sort by sequence number
    blocks.sort(key=lambda b: b.sequence)
    return blocks
