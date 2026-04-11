# clitic - Requirements

**Project:** clitic - A Python package for building rich, interactive CLI applications
**PyPI Name:** `clitic`
**License:** MIT License
**Status:** Requirements Phase
**Date:** 2026-04-11

---

## 1. Executive Summary

This document defines requirements for a Python module that enables developers to build rich, interactive terminal user interfaces (TUIs). The module provides reusable components for chat-style interfaces, multiline input with syntax highlighting, scrollable content areas, and pluggable content renderers.

---

## 2. Target Users and Use Cases

### 2.1 Primary Users

| User Type | Description | Needs |
|-----------|-------------|-------|
| **Application Developers** | Python developers building interactive CLI tools | Reusable widgets, clear APIs, minimal boilerplate |
| **Tool Creators** | Building REPLs, shells, or chat-style interfaces | Input handling, history, completion |
| **Content Application Builders** | Log viewers, monitors, dashboards | Real-time updates, scrolling, rendering |

### 2.2 Target Applications

| Application Type | Example | Key Features Needed |
|------------------|---------|---------------------|
| **AI Chat Interfaces** | Claude Code, Cursor CLI | Multiline input, streaming markdown, diffs |
| **REPL/Shell Wrappers** | IPython, ptpython | History, completion, syntax highlighting |
| **Log/Tail Viewers** | Logs Explorer | Auto-scroll, filtering, ANSI support |
| **Interactive Monitors** | htop, glances | Real-time updates, keyboard navigation |
| **Debug Consoles** | pdb alternatives | Multiline input, rich output |

---

## 3. Functional Requirements

### 3.1 Input Bar Component

**FR-001: Multiline Input Widget**

The framework SHALL provide a multiline text input widget with the following capabilities:

| Requirement | Specification |
|-------------|---------------|
| Text Editing | Full cursor movement, selection, copy/paste |
| Line Wrapping | Visual line wrapping, not logical line breaks |
| Auto-grow | Widget height expands as content grows |
| Maximum Height | Configurable maximum height before scrolling within input |
| Submit Behavior | Enter submits, Shift+Enter inserts newline (configurable) |

**FR-002: Syntax Highlighting**

The input widget SHALL support syntax highlighting:

| Requirement | Specification |
|-------------|---------------|
| Language Modes | Markdown, Shell/Bash, and user-extensible modes |
| Detection | Auto-detect based on content patterns |
| Performance | Highlighting computed asynchronously to avoid blocking |
| Configuration | Support custom syntax highlighters via plugin |

**FR-003: History Navigation**

The input widget SHALL provide history navigation:

| Requirement | Specification |
|-------------|---------------|
| Storage Format | JSON Lines with timestamps |
| Persistence | Per-session or per-application history files |
| Navigation | Up/Down arrows at cursor boundaries (start/end) |
| Draft Preservation | Save current draft when navigating history |
| Search | Optional fuzzy search through history (Ctrl+R) |

**FR-004: Auto-Completion**

The input widget SHALL support auto-completion:

| Requirement | Specification |
|-------------|---------------|
| Trigger | Tab key or configurable trigger |
| Sources | Pluggable completion providers |
| Display | Dropdown overlay with filtered options |
| Selection | Arrow keys + Enter to select |
| Context Awareness | Completion suggestions based on cursor position |

**FR-005: Mode Switching**

The input widget SHALL support input mode switching:

| Requirement | Specification |
|-------------|---------------|
| Modes | At least: text, shell/command modes |
| Indicator | Visual indicator of current mode |
| Hotkey | Single key to toggle modes |
| Extensible | Allow applications to define custom modes |

### 3.2 Conversation/Log Area

**FR-006: Scrollable Content Container**

The framework SHALL provide a scrollable content container:

| Requirement | Specification |
|-------------|---------------|
| Scrolling | Smooth vertical scrolling with mouse and keyboard |
| Auto-scroll | Automatically scroll to bottom on new content |
| Pause on Interaction | Pause auto-scroll when user scrolls up |
| Resume | Resume auto-scroll when user scrolls to bottom |
| Performance | Virtual rendering - only visible content rendered |

**FR-007: Content Block Management**

The container SHALL support content block management:

| Requirement | Specification |
|-------------|---------------|
| Block Types | User messages, system messages, tool outputs, etc. |
| Appending | Append new blocks to the end |
| Pruning | Remove old blocks when memory exceeds threshold |
| Navigation | Move cursor between blocks (Alt+Up/Down) |
| Actions | Per-block actions (expand, collapse, copy, delete) |

**FR-008: Block Interactivity**

Content blocks SHALL support interactivity:

| Requirement | Specification |
|-------------|---------------|
| Expand/Collapse | Toggle visibility of block details |
| Selection | Click to select block |
| Copy | Copy block content to clipboard |
| Context Menu | Right-click or key for context menu |

### 3.3 Content Rendering

**FR-009: Markdown Rendering**

The framework SHALL render Markdown content:

| Requirement | Specification |
|-------------|---------------|
| Elements | Headers, paragraphs, lists, code blocks, links, tables |
| Code Blocks | Syntax highlighting by language tag |
| Streaming | Support incremental/streaming updates |
| Links | Clickable links that open in browser or trigger callback |

**FR-010: Diff Rendering**

The framework SHALL render diffs:

| Requirement | Specification |
|-------------|---------------|
| Modes | Unified diff and side-by-side (split) views |
| Auto-switch | Automatically choose mode based on terminal width |
| Syntax Highlighting | Highlight code in diff context |
| Line Annotations | Show +, -, and ~ symbols for changes |
| Character-level | Highlight character-level changes within lines |

**FR-011: Terminal/ANSI Rendering**

The framework SHALL render terminal output with ANSI support:

| Requirement | Specification |
|-------------|---------------|
| ANSI Codes | Full SGR sequence support (colors, styles) |
| Colors | 16-color, 256-color, and true color (24-bit) |
| Cursor Movement | Handle cursor positioning sequences |
| Alternate Screen | Support for alternate screen buffer |
| Mouse Events | Encode mouse clicks and movements |
| Performance | LRU cache for rendered content |

**FR-012: Tree Rendering**

The framework SHALL render tree structures:

| Requirement | Specification |
|-------------|---------------|
| Collapsible | Expand/collapse nodes |
| Icons | Configurable icons for folders, files, etc. |
| Selection | Keyboard navigation through tree |
| Search | Filter tree by text pattern |

**FR-013: Table Rendering**

The framework SHALL render tables:

| Requirement | Specification |
|-------------|---------------|
| Layout | Auto-sized columns or fixed widths |
| Headers | Optional header row |
| Alignment | Column alignment (left, center, right) |
| Scrolling | Horizontal scrolling for wide tables |
| Sorting | Click header to sort (optional) |

### 3.4 Plugin System

**FR-014: Content Renderer Plugin Interface**

The framework SHALL provide a plugin interface for content renderers:

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

**FR-015: Completion Provider Plugin Interface**

The framework SHALL provide a plugin interface for completion providers:

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

**FR-016: Mode Provider Plugin Interface**

The framework SHALL provide a plugin interface for input modes:

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

### 3.5 Layout and Styling

**FR-017: Responsive Layout**

The framework SHALL support responsive layouts:

| Requirement | Specification |
|-------------|---------------|
| Width Detection | Detect terminal width changes |
| Breakpoints | Define layout changes at width thresholds |
| Auto-switch | Automatically switch between layouts |

**FR-018: CSS-like Styling**

The framework SHALL support CSS-like styling:

| Requirement | Specification |
|-------------|---------------|
| External Files | Styles defined in separate .css/.tcss files |
| Selectors | Widget type, ID, and class selectors |
| Properties | Colors, padding, margin, borders, dimensions |
| Variables | Define and reference style variables |

**FR-019: Themes**

The framework SHALL support theming:

| Requirement | Specification |
|-------------|---------------|
| Built-in Themes | At least light and dark themes |
| Custom Themes | Allow user-defined themes |
| Runtime Switch | Change theme without restart |
| Persistence | Remember user's theme preference |

### 3.6 Animation and Feedback

**FR-020: Loading Indicators**

The framework SHALL provide loading indicators:

| Requirement | Specification |
|-------------|---------------|
| Spinner | Animated spinner for indeterminate progress |
| Progress Bar | Determinate progress bar |
| Customizable | Allow custom animations |
| Visibility | Toggle visibility based on state |

**FR-021: Visual Feedback**

The framework SHALL provide visual feedback:

| Requirement | Specification |
|-------------|---------------|
| Cursor Blink | Blinking cursor in input widget |
| Focus Indication | Visual indication of focused widget |
| Hover States | Visual feedback on mouse hover |
| Error Highlighting | Highlight errors and warnings |

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-001: Rendering Performance**

| Metric | Requirement |
|--------|-------------|
| Initial Render | < 100ms for typical content |
| Update Latency | < 50ms for incremental updates |
| Streaming | Support 60+ updates per second |
| Memory | < 50MB for 10,000 content blocks |

**NFR-002: Input Responsiveness**

| Metric | Requirement |
|--------|-------------|
| Keystroke Latency | < 16ms (60fps) |
| Completion Delay | < 100ms for cached results |
| History Navigation | < 50ms to load history entry |

**NFR-003: Large Content Handling**

| Metric | Requirement |
|--------|-------------|
| Maximum Lines | Support 100,000+ lines in log |
| Diff Size | Handle 10,000+ line diffs |
| Streaming Markdown | Stream unlimited content length |

### 4.2 Compatibility

**NFR-004: Terminal Compatibility**

| Terminal | Support Level |
|----------|---------------|
| iTerm2, Terminal.app (macOS) | Full support |
| Windows Terminal | Full support |
| GNOME Terminal, Konsole (Linux) | Full support |
| VS Code Terminal | Full support |
| tmux, screen | Full support |
| Legacy terminals (xterm) | Basic support (16 colors) |

**NFR-005: Python Version**

| Requirement | Specification |
|-------------|---------------|
| Minimum Version | Python 3.9+ |
| Tested Versions | Python 3.9, 3.10, 3.11, 3.12 |

**NFR-006: Operating Systems**

| OS | Support Level |
|----|---------------|
| macOS | Full support |
| Linux | Full support |
| Windows 10/11 | Full support (WSL included) |

### 4.3 Usability

**NFR-007: API Design**

| Requirement | Specification |
|-------------|---------------|
| Discoverable | Clear naming, type hints, docstrings |
| Minimal Boilerplate | Working example in < 20 lines |
| Progressive Disclosure | Simple defaults, advanced options available |
| Error Messages | Clear, actionable error messages |

**NFR-008: Documentation**

| Requirement | Specification |
|-------------|---------------|
| API Reference | Complete docstrings for all public APIs |
| Examples | Working examples for common use cases |
| Tutorial | Step-by-step getting started guide |
| Migration | Guide for migrating from prompt-toolkit |

### 4.4 Extensibility

**NFR-009: Plugin Architecture**

| Requirement | Specification |
|-------------|---------------|
| Registration | Simple decorator or function call |
| Discovery | Automatic discovery of installed plugins |
| Dependencies | Plugin dependencies handled gracefully |
| Isolation | Plugin failures don't crash application |

---

## 5. Architecture Recommendations

### 5.1 Framework Choice

**Recommendation: Build on Textual**

| Factor | Textual | Alternative (Rich + prompt-toolkit) |
|--------|---------|-------------------------------------|
| Development Time | Low | Very High (5000-10000 LOC) |
| Maintenance | Low | High |
| Features | Full TUI framework | Requires assembly |
| Community | Active | Fragmented |
| Documentation | Excellent | Varies by package |
| License | MIT | MIT + BSD-3 |

**Rationale:** Textual provides reactive state management, widget composition, event handling, CSS-like styling, and layout engine that would require thousands of lines of custom code to replicate.

### 5.2 Proposed Package Structure

```
clitic/
  __init__.py              # Public API
  core/
    __init__.py
    app.py                 # Base application class
    screen.py              # Screen management
  widgets/
    __init__.py
    input_bar.py           # Multiline input with history
    conversation.py        # Scrollable content container
    tree.py                # Collapsible tree
    table.py               # Table renderer
  plugins/
    __init__.py
    base.py                # Plugin base classes
    markdown.py            # Markdown renderer plugin
    diff.py                # Diff renderer plugin
    terminal.py            # Terminal renderer plugin
  completion/
    __init__.py
    base.py                # Completion provider interface
    path.py                # File path completion
    history.py             # History-based completion
  history/
    __init__.py
    manager.py             # History storage/management
  themes/
    __init__.py
    dark.tcss              # Dark theme
    light.tcss             # Light theme
  styles/
    __init__.py
    base.tcss              # Base styles
  utils/
    __init__.py
    fuzzy.py               # Fuzzy matching
    ansi.py                # ANSI utilities
```

### 5.3 Public API Design

```python
# Example usage
from clitic import App, InputBar, Conversation
from clitic.plugins import MarkdownPlugin, DiffPlugin

# Create application
app = App(
  title="My CLI Tool",
  theme="dark"
)

# Add input bar with history
input_bar = InputBar(
  history_file="~/.my_cli_history.jsonl",
  completion_providers=[PathCompletion()]
)

# Add conversation area
conversation = Conversation(
  plugins=[
    MarkdownPlugin(),
    DiffPlugin(),
  ],
  auto_scroll=True,
  max_blocks=1000
)

# Register handlers
@input_bar.on_submit
def handle_submit(text: str):
  conversation.append("user", text)
  # Process input...

# Run
app.run()
```

### 5.4 Implementation Principles

| Principle | Description |
|-----------|-------------|
| **Clean architecture** | Clear separation of concerns, single responsibility |
| **Consistent naming** | snake_case for functions/variables, PascalCase for classes |
| **Type hints** | Full type annotations on all public APIs |
| **Documentation** | Docstrings on all public classes and methods |
| **Testing** | Unit tests for core functionality from day one |
| **Modern Python** | Python 3.9+ features (dataclasses, typing, asyncio) |

**Code Organization:**
- One public class per file (exceptions for small related classes)
- `__init__.py` exports public API explicitly
- Private members prefixed with `_`
- No star imports in production code

**Styling:**
- Two-space indentation (project convention)
- Max line length: 100 characters
- Blank lines between logical sections

---

## 6. Implementation Phases

### Phase 1: Core Framework

**Priority: P1 - Essential**

| Task | Description | Estimate |
|------|-------------|----------|
| Project Setup | Package structure, pyproject.toml, CI | 1 day |
| Base App Class | Textual App wrapper with sensible defaults | 1 day |
| Input Bar | Multiline input with history | 3 days |
| Conversation | Scrollable content container | 2 days |
| Basic Styling | Dark/light themes, base styles | 1 day |

### Phase 2: Content Renderers

**Priority: P1 - Essential**

| Task | Description | Estimate |
|------|-------------|----------|
| Markdown Plugin | Streaming markdown with code blocks | 3 days |
| Diff Plugin | Unified/split diff with highlighting | 2 days |
| Terminal Plugin | ANSI terminal emulator | 4 days |
| Tree Plugin | Collapsible tree widget | 2 days |

### Phase 3: Completion & History

**Priority: P2 - Important**

| Task | Description | Estimate |
|------|-------------|----------|
| Completion Framework | Provider interface, overlay | 2 days |
| Path Completion | File path fuzzy completion | 1 day |
| History System | JSON Lines storage, navigation | 2 days |
| History Search | Ctrl+R fuzzy search | 1 day |

### Phase 4: Polish & Documentation

**Priority: P2 - Important**

| Task | Description | Estimate |
|------|-------------|----------|
| Theme System | Multiple themes, runtime switch | 2 days |
| Responsive Layout | Breakpoints, auto-switch | 2 days |
| Animation | Loading indicators, transitions | 2 days |
| Examples | Working examples for each widget | 2 days |
| Documentation | API docs, tutorial, guide | 3 days |

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lines of Code (User) | < 50 lines for chat app | Example application |
| Startup Time | < 200ms | Benchmark on reference hardware |
| Memory Usage | < 50MB for 1000 blocks | Memory profiler |
| Test Coverage | > 90% | pytest-cov |
| Documentation Coverage | 100% public APIs | Docstring check |
| Issue Resolution | < 7 days average | GitHub metrics |

---

## 8. Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| textual | >=0.50.0 | MIT | TUI framework |
| rich | >=13.0.0 | MIT | Terminal rendering |

All dependencies are MIT or MIT-compatible (BSD-3-Clause) licensed.
