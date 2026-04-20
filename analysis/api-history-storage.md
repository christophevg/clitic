# API Analysis: History Storage

**Project:** clitic - A Python package for building rich, interactive CLI applications
**Task:** history-storage
**Date:** 2026-04-20
**Analyst:** API Architect Agent

---

## 1. Summary

This document defines the API for the command history storage system (FR-003). The design provides a durable, append-only JSON Lines format for storing input history with metadata support.

**Key Design Decisions:**
- JSON Lines (JSONL) format for atomic appends and easy streaming
- Frozen `HistoryEntry` dataclass for immutability
- Similar patterns to `SessionManager` and `BlockInfo` for consistency
- Configurable history file path with sensible defaults
- Thread-safe operations for concurrent access

---

## 2. Requirements Reference

From TODO.md and functional.md:

| Requirement | Description |
|-------------|-------------|
| FR-003 | History Navigation - Up arrow at cursor start navigates to previous entry, Down arrow at cursor end navigates to next entry |
| Storage | JSON Lines format with timestamp, text, metadata |
| Durability | Append-only writes for durability |
| Configuration | Configurable history file path |
| Initialization | Load history from file on initialization |

---

## 3. Data Model

### 3.1 HistoryEntry Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class HistoryEntry:
    """Immutable history entry representing a single input command.

    Attributes:
        text: The input text that was submitted.
        timestamp: Timezone-aware UTC datetime when the entry was created.
        metadata: Optional metadata dictionary (e.g., session context, source).

    Example:
        >>> entry = HistoryEntry(
        ...     text="ls -la",
        ...     timestamp=datetime.now(timezone.utc),
        ...     metadata={"source": "cli"}
        ... )
        >>> entry.text
        'ls -la'
    """
    text: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"HistoryEntry(text={text_preview!r}, timestamp={self.timestamp.isoformat()})"
```

**Design Rationale:**
- **Frozen dataclass**: Ensures immutability after creation (consistent with `BlockInfo`)
- **text: str**: The submitted input text (required, non-empty)
- **timestamp: datetime**: Timezone-aware UTC datetime (required)
- **metadata: dict[str, Any]**: Optional extensible metadata (default empty dict)

**Why not include sequence/ID?**
- History entries are ordered by timestamp in the file
- Navigation is position-based (previous/next), not ID-based
- No need for unique identifiers like conversation blocks

---

## 4. HistoryManager Class

### 4.1 Class Signature

```python
from pathlib import Path
from typing import Iterator

# Default history file location: ~/.local/share/clitic/history.jsonl
DEFAULT_HISTORY_FILE = Path.home() / ".local" / "share" / "clitic" / "history.jsonl"


class HistoryManager:
    """Manages command history with JSON Lines storage.

    Provides durable storage of input history with append-only writes
    for crash safety. History is loaded on initialization and can be
    navigated sequentially.

    Thread Safety:
        All public methods are thread-safe. Multiple threads can safely
        call add() and navigation methods concurrently.

    Example:
        >>> manager = HistoryManager()
        >>> manager.add("ls -la")
        >>> manager.add("cat file.txt")
        >>> len(manager)
        2
        >>> manager.get_previous()  # Navigate backward
        HistoryEntry(text='cat file.txt', ...)
        >>> manager.get_previous()  # Navigate further back
        HistoryEntry(text='ls -la', ...)
        >>> manager.reset_navigation()  # Return to current
    """

    def __init__(
        self,
        history_file: Path | None = None,
        max_entries: int = 10000,
    ) -> None:
        """Initialize the HistoryManager.

        Args:
            history_file: Optional path to history file. Defaults to
                ~/.local/share/clitic/history.jsonl
            max_entries: Maximum number of entries to keep in memory.
                Older entries are trimmed when limit is exceeded.
                Set to 0 for unlimited. Default: 10000.

        Raises:
            HistoryError: If history file exists but cannot be read.
        """
        ...

    # Properties
    @property
    def history_file(self) -> Path: ...

    @property
    def max_entries(self) -> int: ...

    @property
    def entry_count(self) -> int: ...

    # Navigation
    def get_previous(self) -> HistoryEntry | None: ...
    def get_next(self) -> HistoryEntry | None: ...
    def get_current(self) -> HistoryEntry | None: ...
    def get_entry(self, index: int) -> HistoryEntry | None: ...
    def reset_navigation(self) -> None: ...

    # Modification
    def add(self, text: str, metadata: dict[str, Any] | None = None) -> None: ...
    def clear(self) -> None: ...

    # Search
    def search(self, query: str, limit: int = 10) -> list[HistoryEntry]: ...
    def search_prefix(self, prefix: str, limit: int = 10) -> list[HistoryEntry]: ...

    # Iteration
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[HistoryEntry]: ...
    def __reversed__(self) -> Iterator[HistoryEntry]: ...
```

### 4.2 Navigation State Model

The HistoryManager maintains a navigation cursor for Up/Down arrow key navigation:

```
State Machine:
                                     +-------------------+
                                     |                   |
                                     v                   |
+-----------+   add()    +-----------+-----------+   get_previous()
|  Empty    +----------->|    Navigating       <-------------------+
+-----------+            +-----------+-----------+                   |
     ^                               |                               |
     | reset_navigation()           | get_next()                    |
     |                               |                               |
     |                               v                               |
     |                    +-----------+-----------+                  |
     +------------------->|    At Current        |                  |
                          +-----------+-----------+                  |
                                      ^                              |
                                      | reset_navigation()           |
                                      +------------------------------+

Legend:
- Empty: No history entries (entry_count == 0)
- Navigating: Cursor is within history (not at the end)
- At Current: Cursor is at the end, ready for new input
```

**Navigation Behavior:**

| Method | Precondition | Postcondition | Returns |
|--------|--------------|---------------|---------|
| `get_previous()` | Not at oldest entry | Cursor moves back one | Previous entry or `None` |
| `get_previous()` | At oldest entry | Cursor unchanged | `None` |
| `get_next()` | Not at current position | Cursor moves forward one | Next entry or `None` |
| `get_next()` | At current position | Cursor unchanged | `None` |
| `get_current()` | Any | No change | Current entry or `None` |
| `add()` | Any | Cursor resets to end, entry appended | N/A |
| `reset_navigation()` | Any | Cursor moves to end | N/A |

**Integration with InputBar:**

```python
class InputBar(TextArea):
    def __init__(
        self,
        history_manager: HistoryManager | None = None,
        ...
    ) -> None:
        self._history = history_manager or HistoryManager()
        self._history_cursor: int = -1  # -1 means "current input"
        self._draft: str = ""  # Preserved when navigating history

    def on_key(self, event: Key) -> None:
        # Up arrow at cursor start: navigate backward
        if event.key == "up" and self._cursor_at_start():
            entry = self._history.get_previous()
            if entry:
                self._draft = self.text  # Save current draft
                self.text = entry.text
        # Down arrow at cursor end: navigate forward
        elif event.key == "down" and self._cursor_at_end():
            entry = self._history.get_next()
            if entry:
                self.text = entry.text
            else:
                # Back to current draft
                self.text = self._draft
                self._history.reset_navigation()
```

---

## 5. Methods Specification

### 5.1 Initialization

```python
def __init__(
    self,
    history_file: Path | None = None,
    max_entries: int = 10000,
) -> None:
    """Initialize the HistoryManager.

    Creates the history file if it doesn't exist. Loads existing history
    into memory up to max_entries.

    Args:
        history_file: Path to history file. Defaults to
            ~/.local/share/clitic/history.jsonl. If None, uses default.
        max_entries: Maximum entries in memory. Older entries are
            trimmed. Set to 0 for unlimited. Default: 10000.

    Raises:
        HistoryError: If file exists but cannot be read or parsed.
    """
    self._history_file = history_file or DEFAULT_HISTORY_FILE
    self._max_entries = max_entries
    self._entries: list[HistoryEntry] = []
    self._cursor: int = -1  # -1 = current position (end)
    self._lock = threading.RLock()  # For thread safety

    self._load_from_file()
```

### 5.2 Properties

```python
@property
def history_file(self) -> Path:
    """Path to the history file."""
    return self._history_file

@property
def max_entries(self) -> int:
    """Maximum number of entries kept in memory."""
    return self._max_entries

@property
def entry_count(self) -> int:
    """Number of entries currently in memory."""
    with self._lock:
        return len(self._entries)
```

### 5.3 Navigation Methods

```python
def get_previous(self) -> HistoryEntry | None:
    """Navigate to the previous (older) history entry.

    Returns:
        The previous entry if available, None if at the oldest entry.

    Thread Safety:
        Thread-safe. Acquires lock internally.
    """
    with self._lock:
        if not self._entries or self._cursor == 0:
            return None

        if self._cursor == -1:
            # Move from current position to last entry
            self._cursor = len(self._entries) - 1
        else:
            self._cursor -= 1

        return self._entries[self._cursor]

def get_next(self) -> HistoryEntry | None:
    """Navigate to the next (newer) history entry.

    Returns:
        The next entry if available, None if at the current position.

    Thread Safety:
        Thread-safe. Acquires lock internally.
    """
    with self._lock:
        if not self._entries or self._cursor == -1:
            return None

        self._cursor += 1
        if self._cursor >= len(self._entries):
            self._cursor = -1  # Back to current position
            return None

        return self._entries[self._cursor]

def get_current(self) -> HistoryEntry | None:
    """Get the current entry at the cursor position.

    Returns:
        The current entry if cursor is within history, None if at
        the current position (end).
    """
    with self._lock:
        if self._cursor == -1 or not self._entries:
            return None
        return self._entries[self._cursor]

def get_entry(self, index: int) -> HistoryEntry | None:
    """Get an entry by absolute index.

    Args:
        index: Zero-based index (0 = oldest, -1 = newest).

    Returns:
        The entry at the index, or None if out of bounds.
    """
    with self._lock:
        if not self._entries:
            return None

        # Support negative indexing
        if index < 0:
            index = len(self._entries) + index

        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

def reset_navigation(self) -> None:
    """Reset navigation cursor to the current position.

    Call this after navigating to return to "current input" mode.
    The next get_previous() will start from the newest entry.
    """
    with self._lock:
        self._cursor = -1
```

### 5.4 Modification Methods

```python
def add(
    self,
    text: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Add a new entry to the history.

    Appends the entry to the history file immediately (durable write)
    and adds it to in-memory storage. Resets the navigation cursor.

    Args:
        text: The input text to store. Must not be empty.
        metadata: Optional metadata dictionary.

    Raises:
        ValueError: If text is empty or whitespace only.
        HistoryError: If write to history file fails.

    Thread Safety:
        Thread-safe. Acquires lock internally.
    """
    if not text.strip():
        raise ValueError("History entry text cannot be empty")

    entry = HistoryEntry(
        text=text,
        timestamp=datetime.now(timezone.utc),
        metadata=metadata or {},
    )

    with self._lock:
        self._append_to_file(entry)
        self._entries.append(entry)

        # Trim if exceeds max_entries
        if self._max_entries > 0 and len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        # Reset cursor to end
        self._cursor = -1

def clear(self) -> None:
    """Clear all history entries.

    Removes all entries from memory and deletes the history file.

    Raises:
        HistoryError: If file deletion fails.
    """
    with self._lock:
        self._entries.clear()
        self._cursor = -1

        if self._history_file.exists():
            try:
                self._history_file.unlink()
            except OSError as e:
                raise HistoryError(
                    operation="clear",
                    message=f"Failed to delete history file: {e}",
                ) from e
```

### 5.5 Search Methods

```python
def search(
    self,
    query: str,
    limit: int = 10,
) -> list[HistoryEntry]:
    """Search history for entries containing the query (case-insensitive).

    Args:
        query: Search query string.
        limit: Maximum number of results. Default: 10.

    Returns:
        List of matching entries, newest first.
    """
    with self._lock:
        if not query.strip():
            return []

        query_lower = query.lower()
        results = []

        # Search from newest to oldest
        for entry in reversed(self._entries):
            if query_lower in entry.text.lower():
                results.append(entry)
                if len(results) >= limit:
                    break

        return results

def search_prefix(
    self,
    prefix: str,
    limit: int = 10,
) -> list[HistoryEntry]:
    """Search history for entries starting with the prefix (case-insensitive).

    Used for tab-completion style history search.

    Args:
        prefix: Prefix string to match.
        limit: Maximum number of results. Default: 10.

    Returns:
        List of matching entries, newest first.
    """
    with self._lock:
        if not prefix.strip():
            return []

        prefix_lower = prefix.lower()
        results = []

        # Search from newest to oldest
        for entry in reversed(self._entries):
            if entry.text.lower().startswith(prefix_lower):
                results.append(entry)
                if len(results) >= limit:
                    break

        return results
```

### 5.6 Iteration Methods

```python
def __len__(self) -> int:
    """Return the number of history entries."""
    with self._lock:
        return len(self._entries)

def __iter__(self) -> Iterator[HistoryEntry]:
    """Iterate over entries from oldest to newest."""
    with self._lock:
        return iter(self._entries.copy())

def __reversed__(self) -> Iterator[HistoryEntry]:
    """Iterate over entries from newest to oldest."""
    with self._lock:
        return iter(reversed(self._entries.copy()))
```

### 5.7 Internal Methods

```python
def _load_from_file(self) -> None:
    """Load history from the JSONL file.

    Called during initialization. Creates parent directories if needed.
    Skips malformed lines but logs warnings.

    Raises:
        HistoryError: If file cannot be read.
    """
    if not self._history_file.exists():
        # Ensure parent directory exists
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        return

    entries: list[HistoryEntry] = []

    try:
        with open(self._history_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)

                    entry = HistoryEntry(
                        text=data["text"],
                        timestamp=timestamp,
                        metadata=data.get("metadata", {}),
                    )
                    entries.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    # Log warning but continue loading
                    logger.warning(
                        f"Skipping malformed history entry at line {line_num}: {e}"
                    )

        self._entries = entries[-self._max_entries:] if self._max_entries > 0 else entries

    except OSError as e:
        raise HistoryError(
            operation="load",
            message=f"Failed to read history file: {e}",
        ) from e

def _append_to_file(self, entry: HistoryEntry) -> None:
    """Append an entry to the history file.

    Creates the file if it doesn't exist. Uses atomic write pattern
    with flush and fsync for durability.

    Raises:
        HistoryError: If write fails.
    """
    data = {
        "text": entry.text,
        "timestamp": entry.timestamp.isoformat(),
        "metadata": entry.metadata,
    }

    try:
        # Ensure parent directory exists
        self._history_file.parent.mkdir(parents=True, exist_ok=True)

        # Append to file with flush/fsync for durability
        with open(self._history_file, "a", encoding="utf-8") as f:
            json_line = json.dumps(data, ensure_ascii=False)
            f.write(json_line + "\n")
            f.flush()
            os.fsync(f.fileno())

    except OSError as e:
        raise HistoryError(
            operation="save",
            message=f"Failed to write history entry: {e}",
        ) from e
```

---

## 6. File Format Specification

### 6.1 JSON Lines Format

Each line in the history file is a valid JSON object:

```json
{"text": "ls -la", "timestamp": "2026-04-20T10:30:00Z", "metadata": {}}
{"text": "cat file.txt", "timestamp": "2026-04-20T10:30:15Z", "metadata": {"source": "cli"}}
{"text": "grep pattern *.py", "timestamp": "2026-04-20T10:31:00Z", "metadata": {}}
```

**Format Requirements:**
- One JSON object per line (JSON Lines / NDJSON format)
- UTF-8 encoding
- Each line is self-contained (can be parsed independently)
- Append-only: new entries are added at the end
- Oldest entries at the beginning, newest at the end

### 6.2 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["text", "timestamp"],
  "properties": {
    "text": {
      "type": "string",
      "description": "The input command text",
      "minLength": 1
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp with timezone"
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata dictionary",
      "additionalProperties": true
    }
  }
}
```

### 6.3 Durability Guarantees

| Operation | Guarantee |
|-----------|-----------|
| `add()` | Entry is written, flushed, and fsynced before returning |
| `__init__()` | File is read completely before any operations |
| Concurrent writes | Thread-safe via RLock |
| Crash recovery | All entries successfully added are recoverable |
| Malformed lines | Skipped during load with warning logged |

---

## 7. Error Handling

### 7.1 HistoryError Exception

Add a new exception to `src/clitic/exceptions.py`:

```python
class HistoryError(CliticError):
    """Exception for history-related issues.

    Raised when history operations fail (load, save, delete).

    Attributes:
        operation: The operation that failed (e.g., 'load', 'save', 'clear').
    """

    def __init__(
        self,
        operation: str = "unknown",
        message: str | None = None,
    ) -> None:
        """Initialize HistoryError.

        Args:
            operation: The operation that failed.
            message: Optional additional context for the error.
        """
        self.operation = operation
        self._message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        """Format the error message with operation context."""
        base = f"History error during {self.operation}"
        if self._message:
            return f"{base}: {self._message}"
        return f"{base}."

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return f"HistoryError(operation={self.operation!r}, message={self._message!r})"
```

### 7.2 Error Scenarios

| Scenario | Exception | Recovery |
|----------|-----------|----------|
| File cannot be read | `HistoryError(operation="load")` | Start with empty history |
| File malformed lines | Skip line, log warning | Continue loading valid lines |
| Write fails (disk full) | `HistoryError(operation="save")` | Entry not added to memory |
| Empty text in `add()` | `ValueError` | No change to history |
| Delete fails | `HistoryError(operation="clear")` | Memory cleared, file remains |

---

## 8. Thread Safety

### 8.1 Concurrency Model

The `HistoryManager` uses a reentrant lock (`threading.RLock`) to protect all state:

```python
import threading

class HistoryManager:
    def __init__(self, ...) -> None:
        self._lock = threading.RLock()
        # ...

    def add(self, text: str, ...) -> None:
        with self._lock:
            # ... all operations under lock

    def get_previous(self) -> HistoryEntry | None:
        with self._lock:
            # ...
```

### 8.2 Thread-Safe Patterns

| Use Case | Pattern |
|----------|---------|
| Single thread navigation | No special handling needed |
| Multiple threads adding | Lock ensures atomic add + write |
| Concurrent navigation | Lock ensures consistent state |
| Mixed add + navigate | Lock prevents race conditions |

---

## 9. Integration Points

### 9.1 InputBar Integration

The `InputBar` widget will use `HistoryManager` for history navigation:

```python
# In src/clitic/widgets/input_bar.py

class InputBar(TextArea):
    def __init__(
        self,
        text: str = "",
        *,
        history: HistoryManager | None = None,  # New parameter
        history_file: Path | None = None,       # Convenience parameter
        ...
    ) -> None:
        if history is None and history_file is not None:
            history = HistoryManager(history_file=history_file)
        self._history = history
        self._history_cursor = -1  # -1 = current position
        self._draft = ""
        super().__init__(text, ...)

    def on_key(self, event: Key) -> None:
        # Handle Up/Down for history navigation
        if self._history:
            if event.key == "up" and self._cursor_at_start():
                self._handle_history_previous()
            elif event.key == "down" and self._cursor_at_end():
                self._handle_history_next()

    def submit(self) -> None:
        # Add to history on submit
        if self._history and self.text.strip():
            self._history.add(self.text)
        # ... rest of submit logic
```

### 9.2 Public API Export

Update `src/clitic/__init__.py`:

```python
from clitic.history import HistoryEntry, HistoryManager
from clitic.exceptions import HistoryError

__all__ = [
    # ... existing exports
    "HistoryEntry",
    "HistoryError",
    "HistoryManager",
]
```

---

## 10. Usage Examples

### 10.1 Basic Usage

```python
from clitic import HistoryManager

# Create manager with default location
history = HistoryManager()

# Add entries
history.add("ls -la")
history.add("cat file.txt")
history.add("grep pattern *.py")

# Navigate
entry = history.get_previous()  # Returns "grep pattern *.py"
entry = history.get_previous()  # Returns "cat file.txt"
entry = history.get_next()      # Returns "grep pattern *.py"

# Search
results = history.search("grep")
results = history.search_prefix("ls")

# Reset navigation
history.reset_navigation()
```

### 10.2 Custom Location

```python
from pathlib import Path
from clitic import HistoryManager

# Custom history file
history = HistoryManager(
    history_file=Path("~/.myapp/history.jsonl"),
    max_entries=5000,
)
```

### 10.3 With Metadata

```python
from clitic import HistoryManager

history = HistoryManager()

# Add entry with metadata
history.add(
    text="SELECT * FROM users",
    metadata={"source": "repl", "language": "sql"}
)

# Iterate with metadata
for entry in history:
    print(f"[{entry.timestamp}] {entry.text}")
    if entry.metadata:
        print(f"  Metadata: {entry.metadata}")
```

### 10.4 Integration with InputBar

```python
from textual.app import App, ComposeResult
from clitic import InputBar, Conversation, HistoryManager

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Conversation()
        yield InputBar(history=HistoryManager())

    def on_input_bar_submit(self, message: InputBar.Submit) -> None:
        # History is automatically added by InputBar
        # Process the submitted text
        ...
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

```python
# tests/test_history_manager.py

class TestHistoryEntry:
    def test_frozen_dataclass(self):
        """HistoryEntry should be immutable."""
        entry = HistoryEntry(text="test", timestamp=datetime.now(timezone.utc))
        with pytest.raises(FrozenInstanceError):
            entry.text = "modified"

    def test_repr_truncation(self):
        """__repr__ should truncate long text."""
        long_text = "x" * 100
        entry = HistoryEntry(text=long_text, timestamp=datetime.now(timezone.utc))
        assert "..." in repr(entry)

class TestHistoryManager:
    def test_add_and_retrieve(self, tmp_path):
        """Adding entries should store them correctly."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("first")
        manager.add("second")
        assert len(manager) == 2

    def test_navigation_previous(self, tmp_path):
        """get_previous should navigate backward."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("first")
        manager.add("second")
        manager.add("third")

        entry = manager.get_previous()  # third
        assert entry.text == "third"

        entry = manager.get_previous()  # second
        assert entry.text == "second"

    def test_navigation_next(self, tmp_path):
        """get_next should navigate forward."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("first")
        manager.add("second")

        manager.get_previous()  # second
        manager.get_previous()  # first
        entry = manager.get_next()  # second
        assert entry.text == "second"

    def test_navigation_reset(self, tmp_path):
        """reset_navigation should return to current position."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("first")

        manager.get_previous()
        manager.reset_navigation()
        assert manager.get_current() is None

    def test_persistence(self, tmp_path):
        """History should persist across instances."""
        history_file = tmp_path / "history.jsonl"

        manager1 = HistoryManager(history_file=history_file)
        manager1.add("first")
        manager1.add("second")

        manager2 = HistoryManager(history_file=history_file)
        assert len(manager2) == 2
        assert manager2.get_previous().text == "second"

    def test_thread_safety(self, tmp_path):
        """Concurrent operations should be safe."""
        import threading

        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        errors = []

        def add_entries():
            for i in range(100):
                try:
                    manager.add(f"entry-{threading.current_thread().name}-{i}")
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=add_entries) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert len(manager) == 1000

    def test_search(self, tmp_path):
        """search should find matching entries."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("ls -la")
        manager.add("cat file.txt")
        manager.add("ls -lh")

        results = manager.search("ls")
        assert len(results) == 2
        assert all("ls" in e.text for e in results)

    def test_search_prefix(self, tmp_path):
        """search_prefix should match entry start."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        manager.add("ls -la")
        manager.add("ls -lh")
        manager.add("cat file.txt")

        results = manager.search_prefix("ls")
        assert len(results) == 2
        assert all(e.text.startswith("ls") for e in results)

    def test_empty_text_rejected(self, tmp_path):
        """add should reject empty text."""
        manager = HistoryManager(history_file=tmp_path / "history.jsonl")
        with pytest.raises(ValueError):
            manager.add("")

    def test_max_entries(self, tmp_path):
        """max_entries should trim old entries."""
        manager = HistoryManager(
            history_file=tmp_path / "history.jsonl",
            max_entries=5
        )
        for i in range(10):
            manager.add(f"entry-{i}")

        assert len(manager) == 5
        # Newest entries should be kept
        entry = manager.get_previous()
        assert entry.text == "entry-9"
```

### 11.2 Integration Tests

```python
# tests/test_history_integration.py

class TestHistoryInputBarIntegration:
    def test_up_arrow_navigation(self, app):
        """Up arrow should navigate history at cursor start."""
        input_bar = app.query_one(InputBar)
        history = input_bar._history

        history.add("first command")
        history.add("second command")

        input_bar.text = ""
        input_bar.cursor_position = 0

        # Simulate Up arrow
        input_bar.on_key(Key(key="up"))

        assert input_bar.text == "second command"

    def test_down_arrow_navigation(self, app):
        """Down arrow should navigate forward at cursor end."""
        input_bar = app.query_one(InputBar)
        history = input_bar._history

        history.add("first command")
        history.add("second command")

        # Navigate backward then forward
        input_bar.on_key(Key(key="up"))   # second command
        input_bar.on_key(Key(key="up"))   # first command
        input_bar.on_key(Key(key="down")) # second command

        assert input_bar.text == "second command"

    def test_draft_preserved(self, app):
        """Current input should be preserved when navigating."""
        input_bar = app.query_one(InputBar)
        history = input_bar._history

        history.add("previous command")
        input_bar.text = "my draft"
        input_bar.cursor_position = 0

        input_bar.on_key(Key(key="up"))    # previous command
        input_bar.on_key(Key(key="down"))  # back to draft

        assert input_bar.text == "my draft"

    def test_submit_adds_to_history(self, app):
        """Submitting text should add to history."""
        input_bar = app.query_one(InputBar)
        history = input_bar._history

        input_bar.text = "new command"
        input_bar.submit()

        assert len(history) == 1
        assert history.get_previous().text == "new command"
```

---

## 12. Acceptance Criteria

Based on TODO.md:

| Criterion | Status | Implementation |
|-----------|--------|----------------|
| `src/clitic/history/manager.py` exists with HistoryManager class | PENDING | Section 4 |
| JSON Lines format with timestamp, text, metadata | PENDING | Section 6 |
| Configurable history file path | PENDING | `history_file` parameter |
| Append-only writes for durability | PENDING | `_append_to_file()` with fsync |
| Load history from file on initialization | PENDING | `_load_from_file()` |
| Unit tests for storage format | PENDING | Section 11 |

---

## 13. Action Items

### Implementation Tasks

1. **Create `HistoryError` exception** in `src/clitic/exceptions.py`
2. **Create `HistoryEntry` dataclass** in `src/clitic/history/__init__.py`
3. **Create `HistoryManager` class** in `src/clitic/history/manager.py`
4. **Update `src/clitic/__init__.py`** to export new classes
5. **Write unit tests** in `tests/test_history_manager.py`
6. **Write integration tests** for InputBar integration (after history-navigation task)

### Documentation Tasks

1. **Update API reference** in `docs/api/history.md`
2. **Add usage examples** to docstrings
3. **Update README.md** with history configuration options

---

## 14. Questions for Clarification

1. **Deduplication:** Should duplicate entries be deduplicated? (e.g., consecutive identical commands)
   - **Recommendation:** Add optional `deduplicate: bool` parameter to `add()`, default `False`.

2. **Max file size:** Should there be a maximum file size in addition to `max_entries`?
   - **Recommendation:** Not needed initially. `max_entries` provides sufficient control.

3. **Encoding:** Should `text` be validated for valid UTF-8?
   - **Recommendation:** Python handles this automatically. Invalid UTF-8 will raise on write.

4. **History sharing:** Should multiple InputBar instances share the same HistoryManager?
   - **Recommendation:** Yes, by design. Users create one HistoryManager and pass it to InputBar.

---

## 15. Conclusion

This API design provides a robust, thread-safe history storage system that:

- **Follows existing patterns**: Consistent with `SessionManager`, `BlockInfo`, and exception hierarchy
- **Is durable**: Append-only writes with fsync ensure crash safety
- **Is extensible**: Metadata field allows future extensions without schema changes
- **Is performant**: O(1) navigation, O(n) search, efficient memory usage with `max_entries`
- **Is well-tested**: Comprehensive test strategy covers unit and integration tests

The design is ready for implementation following the patterns established in the clitic codebase.