# API Architecture Analysis: clitic

**Project:** clitic - A Python package for building rich, interactive CLI applications
**Date:** 2026-04-11
**Analyst:** API Architect Agent

---

## 1. Executive Summary

This analysis reviews the proposed API design for clitic from an architecture perspective. The project aims to provide a Python package for building terminal user interfaces with a focus on chat-style interfaces, multiline input, and pluggable content renderers.

**Overall Assessment:** The API design is well-structured with clear separation of concerns. The plugin architecture follows sound design principles. Several recommendations are provided to enhance consistency, type completeness, and extensibility.

**Key Findings:**
- Plugin interfaces are well-designed but need minor consistency improvements
- Public API surface is minimal and discoverable
- Type hints are planned but need explicit enforcement via py.typed
- Quick Start example has a bug (conversation used before defined)
- Extension points need clearer documentation

---

## 2. Public API Surface Review

### 2.1 Current State

The public API is defined in `src/clitic/__init__.py`:

```python
__version__ = "0.1.0"

__all__ = [
  "__version__",
  # "App",
  # "InputBar",
  # "Conversation",
]
```

### 2.2 Proposed Public API (from README.md)

```python
from clitic import App, InputBar, Conversation

app = App(title="My CLI Tool")

@app.on_submit
def handle_input(text: str):
    conversation.append("user", text)

conversation = Conversation()
input_bar = InputBar(history_file="~/.my_cli_history.jsonl")

app.run()
```

### 2.3 Issues Found

#### Bug in Quick Start Example

The `conversation` variable is used in `handle_input` before it is defined. The correct order should be:

```python
from clitic import App, InputBar, Conversation

app = App(title="My CLI Tool")
conversation = Conversation()
input_bar = InputBar(history_file="~/.my_cli_history.jsonl")

@app.on_submit
def handle_input(text: str):
    conversation.append("user", text)
    # Process input...

app.run()
```

#### Missing Integration in Quick Start

The `input_bar` is created but not connected to the `app`. The API should clarify how widgets are composed:

```python
# Option A: Explicit composition
app = App(title="My CLI Tool")
app.add_input_bar(input_bar)
app.add_conversation(conversation)

# Option B: Constructor composition
app = App(
  title="My CLI Tool",
  input_bar=input_bar,
  conversation=conversation
)

# Option C: Decorator pattern
@app.conversation
def conversation():
  return Conversation()

@app.input_bar
def input_bar():
  return InputBar(history_file="~/.my_cli_history.jsonl")
```

**Recommendation:** Document the composition pattern explicitly in the API design.

### 2.4 Recommended Public API Exports

The `__init__.py` should export:

| Symbol | Module | Description |
|--------|--------|-------------|
| `App` | `core.app` | Main application class |
| `InputBar` | `widgets.input_bar` | Multiline input widget |
| `Conversation` | `widgets.conversation` | Scrollable content container |
| `Tree` | `widgets.tree` | Collapsible tree widget |
| `Table` | `widgets.table` | Table renderer widget |
| `ContentPlugin` | `plugins.base` | Base class for content renderers |
| `CompletionProvider` | `completion.base` | Base class for completion providers |
| `ModeProvider` | `plugins.base` | Base class for input mode providers |

---

## 3. Plugin Interface Assessment

### 3.1 ContentPlugin Interface (FR-014)

**From requirements.md:**

```python
class ContentPlugin(ABC):
  """Base class for content rendering plugins."""

  @property
  @abstractmethod
  def name(self) -> str:
    """Unique identifier for this plugin."""
    pass

  @property
  def priority(self) -> int:
    """Higher priority plugins are checked first. Default: 0."""
    return 0

  @abstractmethod
  def can_render(self, content_type: str, content: Any) -> bool:
    """Return True if this plugin handles the content type."""
    pass

  @abstractmethod
  def render(self, content: Any) -> Widget:
    """Return a widget for the content."""
    pass
```

**Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clarity | Good | Clear responsibility, single purpose |
| Extensibility | Good | ABC pattern allows easy extension |
| Type Hints | Needs Work | `Any` type is too broad |
| Documentation | Good | Docstrings present |

**Recommendations:**

1. **Replace `Any` with `Union` or `Protocol`:**

   ```python
   from typing import Protocol, Union

   class Renderable(Protocol):
       """Protocol for renderable content."""
       def __str__(self) -> str: ...

   @abstractmethod
   def can_render(self, content_type: str, content: Union[str, Renderable]) -> bool:
       """Return True if this plugin handles the content type."""
       pass

   @abstractmethod
   def render(self, content: Union[str, Renderable]) -> Widget:
       """Return a widget for the content."""
       pass
   ```

2. **Add async rendering support:**

   ```python
   async def render_async(self, content: Any) -> Widget:
       """Async version for slow rendering operations."""
       return self.render(content)
   ```

3. **Add lifecycle hooks:**

   ```python
   def on_register(self, app: "App") -> None:
       """Called when plugin is registered with app."""
       pass

   def on_unregister(self, app: "App") -> None:
       """Called when plugin is unregistered."""
       pass
   ```

### 3.2 CompletionProvider Interface (FR-015)

**From requirements.md:**

```python
class CompletionProvider(ABC):
  """Base class for completion providers."""

  @property
  @abstractmethod
  def name(self) -> str:
    """Unique identifier for this provider."""
    pass

  @abstractmethod
  def get_completions(
    self,
    text: str,
    cursor_position: int
  ) -> list[Completion]:
    """Return completion suggestions for the current context."""
    pass

  async def get_completions_async(
    self,
    text: str,
    cursor_position: int
  ) -> list[Completion]:
    """Async version for slow completion sources."""
    return self.get_completions(text, cursor_position)
```

**Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clarity | Good | Clear interface |
| Async Support | Good | Template method pattern |
| Type Hints | Good | Uses Completion dataclass |

**Issues:**

1. **Missing Completion dataclass definition:** The `Completion` type is referenced but not defined. Need to add:

   ```python
   @dataclass
   class Completion:
       """A single completion suggestion."""
       text: str                    # Text to insert
       display_text: str            # Text to display in dropdown
       cursor_offset: int = 0       # Cursor position after insert
       description: str = ""        # Optional description
       priority: int = 0            # Higher = shown first
       metadata: dict[str, Any] = field(default_factory=dict)
   ```

2. **Add context parameter for richer completion:**

   ```python
   @dataclass
   class CompletionContext:
       """Context for completion request."""
       text: str
       cursor_position: int
       history: list[str] = field(default_factory=list)
       file_path: str | None = None
       environment: dict[str, str] = field(default_factory=dict)

   @abstractmethod
   def get_completions(self, context: CompletionContext) -> list[Completion]:
       pass
   ```

### 3.3 ModeProvider Interface (FR-016)

**From requirements.md:**

```python
class ModeProvider(ABC):
  """Base class for input mode providers."""

  @property
  @abstractmethod
  def name(self) -> str:
    """Unique identifier for this mode."""
    pass

  @property
  @abstractmethod
  def indicator(self) -> str:
    """Visual indicator for this mode (e.g., '>', '$', '!')."""
    pass

  @abstractmethod
  def detect(self, text: str, cursor_position: int) -> bool:
    """Return True if this mode should be activated."""
    pass

  @abstractmethod
  def get_highlighter(self) -> Highlighter | None:
    """Return syntax highlighter for this mode."""
    pass
```

**Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clarity | Good | Clear interface |
| Type Hints | Needs Work | `Highlighter` type not defined |
| Extensibility | Good | Easy to add new modes |

**Recommendations:**

1. **Define Highlighter protocol:**

   ```python
   class Highlighter(Protocol):
       """Protocol for syntax highlighters."""
       def highlight(self, text: str) -> str:
           """Return highlighted text with ANSI codes."""
           ...
   ```

2. **Add priority for mode detection:**

   ```python
   @property
   def priority(self) -> int:
       """Higher priority modes are checked first. Default: 0."""
       return 0
   ```

3. **Add mode transition hooks:**

   ```python
   def on_enter(self, text: str) -> str:
       """Called when entering this mode. Returns transformed text."""
       return text

   def on_exit(self, text: str) -> str:
       """Called when exiting this mode. Returns transformed text."""
       return text
   ```

---

## 4. Consistency Analysis

### 4.1 Naming Conventions

| Convention | Current | Recommendation |
|------------|---------|----------------|
| Classes | PascalCase | Consistent |
| Methods | snake_case | Consistent |
| Properties | snake_case | Consistent |
| Parameters | snake_case | Consistent |

### 4.2 Interface Consistency

All three plugin interfaces share:
- `name` property (unique identifier)
- `priority` property (ordering)

**Issue:** `priority` is only defined on `ContentPlugin`, not on `CompletionProvider` or `ModeProvider`.

**Recommendation:** Add `priority` to all plugin interfaces for consistency:

```python
@property
def priority(self) -> int:
    """Higher priority plugins are checked first. Default: 0."""
    return 0
```

### 4.3 Async Pattern Consistency

| Interface | Async Support |
|-----------|---------------|
| ContentPlugin | Missing |
| CompletionProvider | Present (template method) |
| ModeProvider | Not applicable |

**Recommendation:** Add async support to ContentPlugin for consistency.

---

## 5. Type Completeness (PEP 561)

### 5.1 Requirements for PEP 561 Compliance

| Requirement | Status | Action Needed |
|-------------|--------|---------------|
| `py.typed` marker file | NOT DONE | Create in Phase 0 |
| Type hints on all public APIs | Planned | Document requirement |
| No `Any` in public signatures | Needs Work | Replace with specific types |
| Typed dependencies (textual, rich) | External | Verify stubs available |

### 5.2 Recommendations

1. **Create py.typed marker file** (already in TODO.md):
   ```
   src/clitic/py.typed
   ```

2. **Replace `Any` with specific types:**
   - Use `Protocol` for duck-typed parameters
   - Use `Union` for multiple known types
   - Use `TypeVar` with bounds for generic containers

3. **Add type stubs for external dependencies if needed:**

   ```python
   # src/clitic/_types.py
   from typing import TypeVar
   from textual.widget import Widget

   WidgetType = TypeVar("WidgetType", bound=Widget)
   ```

4. **Document type completeness requirement:**

   Add to development guidelines:
   - All public functions must have complete type hints
   - No `Any` in public signatures without justification
   - Run mypy with `--strict` mode

---

## 6. Extension Points Analysis

### 6.1 Primary Extension Points

| Extension Point | Mechanism | Use Case |
|------------------|-----------|----------|
| Content renderers | `ContentPlugin` subclass | Custom content types |
| Completion sources | `CompletionProvider` subclass | Custom completion logic |
| Input modes | `ModeProvider` subclass | Custom input modes |
| Themes | `.tcss` files | Custom styling |
| Widgets | Textual `Widget` subclass | Custom widgets |

### 6.2 Plugin Registration Pattern

**Current:** Not specified in requirements.

**Recommended:**

```python
# Decorator pattern (Pythonic, discoverable)
@App.content_plugin
class MyPlugin(ContentPlugin):
    ...

# Explicit registration (more control)
app.register_plugin(MyPlugin())

# Auto-discovery (convenient)
# Scans entry_points group "clitic.plugins"
```

**Recommendation:** Support both decorator and explicit registration:

```python
class App:
    def __init__(self):
        self._plugins: list[ContentPlugin] = []

    def register_plugin(self, plugin: ContentPlugin) -> None:
        """Register a content plugin."""
        self._plugins.append(plugin)

    @classmethod
    def content_plugin(cls, plugin_class: type[ContentPlugin]) -> type[ContentPlugin]:
        """Decorator to register a plugin class."""
        # Store for auto-registration
        return plugin_class
```

### 6.3 Entry Points for Discovery

Add to `pyproject.toml`:

```toml
[project.entry-points."clitic.plugins"]
markdown = "clitic.plugins.markdown:MarkdownPlugin"
diff = "clitic.plugins.diff:DiffPlugin"
terminal = "clitic.plugins.terminal:TerminalPlugin"
```

---

## 7. Error Handling Patterns

### 7.1 Recommended Exception Hierarchy

```python
class CliticError(Exception):
    """Base exception for all clitic errors."""
    pass

class PluginError(CliticError):
    """Error in plugin loading or execution."""
    pass

class ConfigurationError(CliticError):
    """Error in configuration."""
    pass

class RenderError(CliticError):
    """Error during content rendering."""
    pass
```

### 7.2 Plugin Error Handling

```python
class ContentPlugin(ABC):
    def render_safe(self, content: Any) -> Widget:
        """Render with error handling. Returns fallback on error."""
        try:
            return self.render(content)
        except Exception as e:
            logger.error(f"Plugin {self.name} failed: {e}")
            return self._fallback_widget(content, e)

    def _fallback_widget(self, content: Any, error: Exception) -> Widget:
        """Return fallback widget when rendering fails."""
        # Return plain text widget
        ...
```

---

## 8. API Design Recommendations

### 8.1 High Priority (P1)

| Recommendation | Impact | Effort |
|----------------|--------|--------|
| Fix Quick Start example bug | High | Low |
| Add py.typed marker | High | Low |
| Define Completion dataclass | High | Low |
| Add priority to all plugin interfaces | Medium | Low |
| Replace `Any` with specific types | High | Medium |
| Document widget composition pattern | High | Low |

### 8.2 Medium Priority (P2)

| Recommendation | Impact | Effort |
|----------------|--------|--------|
| Add async render to ContentPlugin | Medium | Medium |
| Define Highlighter protocol | Medium | Low |
| Add plugin lifecycle hooks | Medium | Medium |
| Define exception hierarchy | Medium | Low |
| Add plugin error handling | Medium | Medium |

### 8.3 Low Priority (P3)

| Recommendation | Impact | Effort |
|----------------|--------|--------|
| Add entry points for auto-discovery | Low | Low |
| Add mode transition hooks | Low | Low |
| Add CompletionContext dataclass | Low | Medium |

---

## 9. Proposed Interface Definitions

### 9.1 ContentPlugin (Revised)

```python
from abc import ABC, abstractmethod
from typing import Protocol, Union
from textual.widget import Widget

class Renderable(Protocol):
    """Protocol for renderable content."""
    def __str__(self) -> str: ...

class ContentPlugin(ABC):
    """Base class for content rendering plugins.

    Subclass this to create custom content renderers.
    Register with App.register_plugin() or use @App.content_plugin decorator.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this plugin.

        Used for logging, debugging, and plugin configuration.
        """
        pass

    @property
    def priority(self) -> int:
        """Higher priority plugins are checked first.

        Returns:
            int: Priority value (default: 0)
        """
        return 0

    @abstractmethod
    def can_render(self, content_type: str, content: Union[str, Renderable]) -> bool:
        """Check if this plugin can render the given content.

        Args:
            content_type: MIME type or custom type identifier
            content: The content to potentially render

        Returns:
            bool: True if this plugin should render the content
        """
        pass

    @abstractmethod
    def render(self, content: Union[str, Renderable]) -> Widget:
        """Render content as a Textual widget.

        Args:
            content: The content to render

        Returns:
            Widget: A Textual widget containing the rendered content
        """
        pass

    async def render_async(self, content: Union[str, Renderable]) -> Widget:
        """Async version for slow rendering operations.

        Default implementation calls render() synchronously.
        Override for I/O-bound rendering (e.g., network fetches).

        Args:
            content: The content to render

        Returns:
            Widget: A Textual widget containing the rendered content
        """
        return self.render(content)

    def on_register(self, app: "App") -> None:
        """Called when plugin is registered with an App.

        Override to perform initialization that requires app context.

        Args:
            app: The App instance registering this plugin
        """
        pass

    def on_unregister(self, app: "App") -> None:
        """Called when plugin is unregistered from an App.

        Override to perform cleanup.

        Args:
            app: The App instance unregistering this plugin
        """
        pass
```

### 9.2 CompletionProvider (Revised)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Completion:
    """A single completion suggestion.

    Attributes:
        text: The text to insert when selected
        display_text: Text shown in the completion dropdown
        cursor_offset: Cursor position offset after insertion
        description: Optional description shown in dropdown
        priority: Higher priority items appear first
        metadata: Additional context-specific data
    """
    text: str
    display_text: str
    cursor_offset: int = 0
    description: str = ""
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

class CompletionProvider(ABC):
    """Base class for completion providers.

    Subclass this to create custom completion sources.
    Register with InputBar.add_completion_provider().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider.

        Used for logging and provider configuration.
        """
        pass

    @property
    def priority(self) -> int:
        """Higher priority providers are queried first.

        Returns:
            int: Priority value (default: 0)
        """
        return 0

    @abstractmethod
    def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        """Return completion suggestions for the current context.

        Args:
            text: Current input text
            cursor_position: Current cursor position in text

        Returns:
            List of Completion objects, sorted by priority
        """
        pass

    async def get_completions_async(self, text: str, cursor_position: int) -> list[Completion]:
        """Async version for slow completion sources.

        Default implementation calls get_completions() synchronously.
        Override for I/O-bound sources (e.g., network, file system).

        Args:
            text: Current input text
            cursor_position: Current cursor position in text

        Returns:
            List of Completion objects, sorted by priority
        """
        return self.get_completions(text, cursor_position)
```

### 9.3 ModeProvider (Revised)

```python
from abc import ABC, abstractmethod
from typing import Protocol

class Highlighter(Protocol):
    """Protocol for syntax highlighters."""

    def highlight(self, text: str) -> str:
        """Return highlighted text with ANSI codes.

        Args:
            text: Plain text input

        Returns:
            Text with ANSI escape sequences for highlighting
        """
        ...

class ModeProvider(ABC):
    """Base class for input mode providers.

    Subclass this to create custom input modes (e.g., shell, python, sql).
    Register with InputBar.add_mode_provider().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this mode.

        Used for logging and mode configuration.
        """
        pass

    @property
    @abstractmethod
    def indicator(self) -> str:
        """Visual indicator for this mode.

        Shown in the input bar prefix area.

        Returns:
            str: Single character or short string (e.g., '>', '$', '!')
        """
        pass

    @property
    def priority(self) -> int:
        """Higher priority modes are checked first.

        Returns:
            int: Priority value (default: 0)
        """
        return 0

    @abstractmethod
    def detect(self, text: str, cursor_position: int) -> bool:
        """Check if this mode should be activated.

        Called on each input change to determine mode.

        Args:
            text: Current input text
            cursor_position: Current cursor position

        Returns:
            bool: True if this mode should be active
        """
        pass

    @abstractmethod
    def get_highlighter(self) -> Highlighter | None:
        """Return syntax highlighter for this mode.

        Returns:
            Highlighter instance or None for no highlighting
        """
        pass

    def on_enter(self, text: str) -> str:
        """Called when entering this mode.

        Override to transform text on mode entry.

        Args:
            text: Current input text

        Returns:
            Transformed text
        """
        return text

    def on_exit(self, text: str) -> str:
        """Called when exiting this mode.

        Override to transform text on mode exit.

        Args:
            text: Current input text

        Returns:
            Transformed text
        """
        return text
```

---

## 10. Action Items

### Immediate (Phase 0-1)

- [ ] Fix Quick Start example in README.md (conversation defined before use)
- [ ] Create py.typed marker file
- [ ] Define Completion dataclass in completion/base.py
- [ ] Add priority property to CompletionProvider and ModeProvider interfaces
- [ ] Document widget composition pattern in requirements

### Short Term (Phase 1-2)

- [ ] Replace `Any` with specific types in plugin interfaces
- [ ] Define Highlighter protocol in plugins/base.py
- [ ] Add async render method to ContentPlugin
- [ ] Add plugin lifecycle hooks (on_register, on_unregister)
- [ ] Define exception hierarchy (CliticError, PluginError, etc.)

### Medium Term (Phase 3-5)

- [ ] Add plugin error handling with fallback widgets
- [ ] Add entry points for auto-discovery
- [ ] Create type stubs for any missing dependencies
- [ ] Add mypy --strict to CI

### Documentation

- [ ] Document all public APIs with complete docstrings
- [ ] Add examples for creating custom plugins
- [ ] Add examples for widget composition
- [ ] Document error handling patterns

---

## 11. Conclusion

The clitic API design is well-conceived with clear separation of concerns and a clean plugin architecture. The main recommendations are:

1. **Type Completeness:** Ensure all public APIs have complete type hints and create the py.typed marker file early.

2. **Consistency:** Add `priority` property to all plugin interfaces for consistent ordering behavior.

3. **Error Handling:** Define a clear exception hierarchy and add graceful degradation for plugin failures.

4. **Documentation:** The Quick Start example has a bug and widget composition needs clearer documentation.

5. **Extensibility:** The plugin interfaces are well-designed but would benefit from lifecycle hooks and async support.

The project is ready to proceed with implementation following the phased approach outlined in the functional analysis.

---

## 12. Task-Specific Review: conversation-block-model

**Date:** 2026-04-14
**Reviewer:** API Architect Agent
**Task:** Review API design for conversation-block-model task

### 12.1 Summary

This section reviews the API design for the conversation-block-model task, which refines the block data model for the Conversation widget. The design introduces a public `BlockInfo` dataclass, session UUID management, timestamps, and metadata support.

**Verdict:** Approved with minor recommendations

### 12.2 Current Implementation

**Existing Internal Dataclass:**

```python
@dataclass
class _BlockData:
    block_id: str
    role: str
    content: str
    line_count: int = 0
```

**Issues:**
- NOT frozen (mutable)
- No timestamp
- No metadata
- Block ID format is `block-{counter}` (no session context)

**Missing Public API:**
- `get_block(block_id)` method
- Session UUID management
- Metadata support

### 12.3 Proposed BlockInfo Dataclass

```python
from datetime import datetime, timezone
from typing import Any
from dataclasses import dataclass

@dataclass(frozen=True)
class BlockInfo:
    """Immutable block metadata container.

    Attributes:
        id: Unique identifier in format "{session_uuid}-{sequence_number}"
        role: Generic role identifier (e.g., "user", "assistant", "system")
        content: Full block content text
        metadata: Immutable metadata dictionary set at creation
        timestamp: Timezone-aware UTC datetime of block creation
    """
    id: str
    role: str
    content: str
    metadata: dict[str, Any]
    timestamp: datetime
```

**API Design Review:**

| Aspect | Assessment | Notes |
|--------|------------|-------|
| Frozen dataclass | APPROVED | Ensures immutability, prevents accidental modification |
| Field ordering | APPROVED | Logical order: id, role, content, metadata, timestamp |
| Type hints | APPROVED | Full type annotations, mypy compatible |
| Field naming | APPROVED | Clear, self-documenting names |
| Documentation | APPROVED | Docstring with attributes listed |

**Recommendation:** Add custom `__repr__` to truncate long content:

```python
def __repr__(self) -> str:
    content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
    return f"BlockInfo(id={self.id!r}, role={self.role!r}, content={content_preview!r}, ...)"
```

### 12.4 Internal _BlockData Design

**Question:** Should `_BlockData` remain as a separate internal class or be replaced by `BlockInfo`?

**Recommendation:** Keep `_BlockData` as internal implementation detail, but derive from `BlockInfo`:

```python
@dataclass
class _BlockData:
    """Internal block data with rendering metadata."""
    info: BlockInfo  # Public immutable data
    line_count: int = 0  # Internal rendering state
```

This approach:
- Maintains separation between public API and internal state
- Avoids duplication of fields
- Makes conversion to `BlockInfo` trivial (just return `self._blocks[i].info`)

### 12.5 Session UUID Management

```python
import uuid

class Conversation(ScrollView):
    def __init__(
        self,
        *,
        session_uuid: str | None = None,
        auto_scroll: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self._session_uuid = session_uuid or str(uuid.uuid4())
        self._sequence_counter: int = 0
        # ... rest of init
```

**API Design Review:**

| Aspect | Assessment | Notes |
|--------|------------|-------|
| Optional parameter | APPROVED | Defaults to auto-generated UUID4 |
| Type hint | APPROVED | `str | None` is correct |
| UUID format | APPROVED | Standard UUID4 format |
| Private attribute | APPROVED | `_session_uuid` properly encapsulated |

**Recommendation:** Add a read-only property for session UUID:

```python
@property
def session_id(self) -> str:
    """The unique identifier for this conversation session."""
    return self._session_uuid
```

### 12.6 Block ID Generation

**Proposed format:** `{session_uuid}-{sequence_number}`

```python
def append(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> str:
    block_id = f"{self._session_uuid}-{self._sequence_counter}"
    self._sequence_counter += 1
    # ...
```

**API Design Review:**

| Aspect | Assessment | Notes |
|--------|------------|-------|
| Format | APPROVED | Globally unique, includes session context |
| Atomicity | NEEDS ATTENTION | Counter increment must be atomic with ID generation |
| Collision resistance | APPROVED | UUID4 + sequential counter = no collisions within session |

**Critical Recommendation:** Never reset sequence counter, even on `clear()`. This ensures ID uniqueness across the session lifetime.

### 12.7 append() Method Signature

**Proposed signature:**

```python
def append(
    self,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Add a new content block to the conversation.

    Args:
        role: The role of the message (user, assistant, system, tool, etc.)
        content: The text content of the message.
        metadata: Optional metadata dictionary (immutable after creation).

    Returns:
        The unique ID of the created block.
    """
```

**API Design Review:**

| Aspect | Assessment | Notes |
|--------|------------|-------|
| Parameter ordering | APPROVED | Required params first, optional last |
| Default for metadata | APPROVED | `None` converted to `{}` at creation |
| Return type | APPROVED | Returns `str` (block ID) for consistency |
| Backward compatible | APPROVED | Optional param doesn't break existing code |

**Recommendation:** Document that metadata is copied at creation:

```python
# In append() implementation:
block_metadata = dict(metadata) if metadata else {}
# This creates a copy, ensuring caller can't modify after
```

### 12.8 get_block() Method

**Proposed signature:**

```python
def get_block(self, block_id: str) -> BlockInfo | None:
    """Retrieve block metadata by ID.

    Args:
        block_id: The unique identifier of the block.

    Returns:
        BlockInfo if found, None if block doesn't exist.
    """
```

**Performance Concern:** The current implementation stores blocks in a list. `get_block()` would require O(n) linear search.

**Critical Recommendation:** Add a block ID index for O(1) lookup:

```python
def __init__(self, ...) -> None:
    self._blocks: list[_BlockData] = []
    self._block_index: dict[str, int] = {}  # block_id -> list index
    # ...

def append(...) -> str:
    block_id = f"{self._session_uuid}-{self._sequence_counter}"
    index = len(self._blocks)
    self._block_index[block_id] = index
    # ... create and append block
    self._sequence_counter += 1
    return block_id

def get_block(self, block_id: str) -> BlockInfo | None:
    if block_id not in self._block_index:
        return None
    index = self._block_index[block_id]
    return self._blocks[index].info

def clear(self) -> None:
    self._blocks.clear()
    self._block_index.clear()
    # DO NOT reset sequence counter
```

### 12.9 Type Safety Analysis

**Metadata Type:** `dict[str, Any]` - APPROVED for maximum flexibility. Users can define their own TypedDict for type checking if needed.

**Timestamp Type:** `datetime` with timezone-aware UTC - APPROVED. Standard library type, prevents local/UTC confusion, serializable to ISO 8601.

### 12.10 Future-Proofing

**Session Persistence (conversation-session-persistence):**
The `BlockInfo` dataclass is well-suited for JSONL serialization:

```python
import json

def block_to_json(block: BlockInfo) -> str:
    return json.dumps({
        "id": block.id,
        "role": block.role,
        "content": block.content,
        "metadata": block.metadata,
        "timestamp": block.timestamp.isoformat(),
    })
```

**Block Pruning (conversation-block-pruning):**
The `get_block()` method is the foundation for transparent retrieval. The O(1) index design supports this pattern.

### 12.11 Recommendations Summary

**Required Changes:**

1. Add `session_id` property for read-only access to session UUID
2. Add `_block_index: dict[str, int]` for O(1) block lookup
3. Never reset sequence counter on `clear()` to prevent ID collisions

**Suggested Improvements:**

4. Custom `__repr__` for `BlockInfo` to truncate long content
5. Document metadata immutability in docstrings
6. Add `__slots__` to `BlockInfo` for memory efficiency (optional)

### 12.12 Acceptance Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| `BlockInfo` dataclass with `frozen=True` | APPROVED | Design is correct |
| Block ID format: `{session_uuid}-{sequence_number}` | APPROVED | Add atomicity note |
| `role: str` generic type | APPROVED | Extensible design |
| `content: str` full content | APPROVED | Correct |
| `metadata: dict[str, Any]` immutable | APPROVED | Design ensures immutability via frozen dataclass |
| `timestamp: datetime` with UTC | APPROVED | Standard approach |
| Session UUID auto-generated | APPROVED | UUID4 is appropriate |
| Optional `session_uuid` parameter | APPROVED | Keyword-only, correct position |
| `get_block(block_id) -> BlockInfo | None` | APPROVED | Add O(1) index for performance |

### 12.13 Action Items for conversation-block-model

- [ ] Implement `BlockInfo` frozen dataclass with custom `__repr__`
- [ ] Add `session_id` property to `Conversation`
- [ ] Add `_block_index` for O(1) block lookup
- [ ] Update `_BlockData` to wrap `BlockInfo` + `line_count`
- [ ] Update `append()` to accept `metadata` parameter
- [ ] Update `clear()` to NOT reset sequence counter
- [ ] Implement `get_block()` with index-based lookup
- [ ] Update all docstrings
- [ ] Add unit tests for new functionality

### 12.14 Conclusion

The proposed API design for conversation-block-model is **approved** with the recommendations noted above. The design follows Python best practices, maintains consistency with the existing codebase, and provides a clean foundation for future features (persistence, pruning, navigation).

**Key strengths:**
- **Immutability:** `BlockInfo` is frozen, preventing accidental modification
- **Extensibility:** Generic `role: str` and `metadata: dict[str, Any]` support future use cases
- **Type safety:** Full type hints throughout
- **Performance:** O(1) block lookup with index (once implemented)

**Critical considerations:**
- Ensure `_block_index` is properly maintained for O(1) lookup
- Never reset sequence counter to prevent ID collisions

---

## 13. Related Documents

- `analysis/functional.md` - Functional analysis with task breakdown
- `docs/requirements.md` - Full requirements specification
- `README.md` - Project overview and quick start
- `TODO.md` - Implementation backlog