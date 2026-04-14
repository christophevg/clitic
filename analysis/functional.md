# Functional Analysis: clitic

**Project:** clitic - A Python package for building rich, interactive CLI applications
**Date:** 2026-04-11
**Analyst:** Functional Analyst Agent

---

## 1. Current State Assessment

### 1.1 Project Initialization Status

| Component | Status | Details |
|-----------|--------|---------|
| Package Structure | DONE | Directory structure matches requirements spec |
| pyproject.toml | DONE | Complete with dependencies, dev tools, mypy, ruff, pytest configs |
| Makefile | DONE | Full development workflow support |
| Basic Tests | DONE | Package import and version tests exist |
| CI/CD | NOT STARTED | No .github/workflows present |
| Implementation | NOT STARTED | All modules are empty stubs |

### 1.2 Module Status

| Module | Planned Files | Status | Notes |
|--------|---------------|--------|-------|
| `clitic.core` | app.py, screen.py | EMPTY | Only `__init__.py` |
| `clitic.widgets` | input_bar.py, conversation.py, tree.py, table.py | EMPTY | Only `__init__.py` |
| `clitic.plugins` | base.py, markdown.py, diff.py, terminal.py | EMPTY | Only `__init__.py` |
| `clitic.completion` | base.py, path.py, history.py | EMPTY | Only `__init__.py` |
| `clitic.history` | manager.py | EMPTY | Only `__init__.py` |
| `clitic.themes` | dark.tcss, light.tcss | EMPTY | Only `__init__.py` |
| `clitic.styles` | base.tcss | EMPTY | Only `__init__.py` |
| `clitic.utils` | fuzzy.py, ansi.py | EMPTY | Only `__init__.py` |

### 1.3 Test Coverage

| Metric | Current | Target |
|--------|---------|--------|
| Test Files | 1 | TBD |
| Test Cases | 2 | TBD |
| Coverage | N/A | >90% |

---

## 2. Requirements Coverage Analysis

### 2.1 Functional Requirements Mapping

**FR-001 to FR-005: Input Bar Component**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-001: Multiline Input Widget | P1 | TODO: InputBar widget | Needs atomic breakdown |
| FR-002: Syntax Highlighting | P2 | TODO: InputBar widget | Missing task |
| FR-003: History Navigation | P2 | TODO: History system | Needs atomic breakdown |
| FR-004: Auto-Completion | P2 | TODO: Completion framework | Needs atomic breakdown |
| FR-005: Mode Switching | P3 | Not in TODO | Missing task |

**FR-006 to FR-008: Conversation/Log Area**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-006: Scrollable Content Container | P1 | TODO: Conversation container | Needs atomic breakdown |
| FR-007: Content Block Management | P1 | TODO: Conversation container | Missing virtual rendering task |
| FR-008: Block Interactivity | P2 | Not in TODO | Missing task |

**FR-009 to FR-013: Content Rendering**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-009: Markdown Rendering | P1 | TODO: Markdown plugin | Needs atomic breakdown |
| FR-010: Diff Rendering | P1 | TODO: Diff plugin | Needs atomic breakdown |
| FR-011: Terminal/ANSI Rendering | P1 | TODO: Terminal plugin | Needs atomic breakdown |
| FR-012: Tree Rendering | P2 | TODO: Tree plugin | Needs atomic breakdown |
| FR-013: Table Rendering | P2 | Not in TODO | Missing task |

**FR-014 to FR-016: Plugin System**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-014: Content Renderer Plugin Interface | P1 | Not in TODO | Missing task |
| FR-015: Completion Provider Plugin Interface | P2 | Not in TODO | Missing task |
| FR-016: Mode Provider Plugin Interface | P3 | Not in TODO | Missing task |

**FR-017 to FR-019: Layout and Styling**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-017: Responsive Layout | P2 | TODO: Responsive layout | Needs atomic breakdown |
| FR-018: CSS-like Styling | P1 | TODO: Basic styling/theming | Needs atomic breakdown |
| FR-019: Themes | P2 | TODO: Theme system | Needs atomic breakdown |

**FR-020 to FR-021: Animation and Feedback**

| Requirement | Priority | Task Coverage | Gap |
|-------------|----------|---------------|-----|
| FR-020: Loading Indicators | P3 | TODO: Animation | Needs atomic breakdown |
| FR-021: Visual Feedback | P3 | Not in TODO | Missing task |

### 2.2 Non-Functional Requirements Coverage

| NFR | Priority | Current Coverage | Gap |
|-----|----------|------------------|-----|
| NFR-001: Rendering Performance | P1 | Not addressed | Need performance tests |
| NFR-002: Input Responsiveness | P1 | Not addressed | Need latency benchmarks |
| NFR-003: Large Content Handling | P1 | Not addressed | Need virtual rendering |
| NFR-004: Terminal Compatibility | P2 | Not addressed | Need compatibility matrix |
| NFR-005: Python Version | DONE | pyproject.toml has >=3.9 | Complete |
| NFR-006: Operating Systems | P2 | Not addressed | Need CI matrix |
| NFR-007: API Design | P1 | Design in requirements | Needs implementation |
| NFR-008: Documentation | P2 | README exists | Need API docs |
| NFR-009: Plugin Architecture | P1 | Not addressed | Need plugin base classes |

---

## 3. Missing Tasks Identified

### 3.1 Project Setup (Not in TODO)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Create py.typed marker file | P1 | None |
| Set up GitHub Actions CI | P1 | None |
| Add pre-commit hooks | P2 | None |

### 3.2 Core Framework (Partial)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Define plugin base classes (FR-014, FR-015, FR-016) | P1 | None |
| Create App base class | P1 | Plugin base classes |

### 3.3 Input Bar (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| InputBar: Basic multiline text widget | P1 | None |
| InputBar: Cursor movement and selection | P1 | Basic widget |
| InputBar: Auto-grow with max height | P1 | Basic widget |
| InputBar: Submit behavior configuration | P1 | Basic widget |
| InputBar: Syntax highlighting integration | P2 | Basic widget |
| InputBar: Mode switching | P3 | Basic widget |

### 3.4 Conversation (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Conversation: Basic scrollable container | P1 | None |
| Conversation: Auto-scroll with pause/resume | P1 | Basic container |
| Conversation: Virtual rendering for performance | P1 | Basic container |
| Conversation: Content block management | P1 | Basic container |
| Conversation: Block interactivity (expand/collapse/copy) | P2 | Block management |

### 3.5 Content Renderers (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Markdown: Headers, paragraphs, lists | P1 | Plugin interface |
| Markdown: Code blocks with syntax highlighting | P1 | Markdown basic |
| Markdown: Streaming updates | P2 | Markdown basic |
| Diff: Unified diff view | P1 | Plugin interface |
| Diff: Side-by-side (split) view | P2 | Unified diff |
| Diff: Character-level highlighting | P2 | Unified diff |
| Terminal: ANSI SGR sequence support | P1 | Plugin interface |
| Terminal: 256-color and true color | P1 | Terminal basic |
| Terminal: Cursor movement | P2 | Terminal basic |
| Tree: Collapsible nodes | P2 | Plugin interface |
| Table: Auto-sized columns with scrolling | P2 | Plugin interface |

### 3.6 Completion & History (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Completion: Provider interface | P1 | None |
| Completion: Dropdown overlay widget | P1 | Provider interface |
| Completion: Path completion provider | P2 | Provider interface |
| History: JSON Lines storage format | P1 | None |
| History: Navigation (Up/Down at boundaries) | P1 | Storage format |
| History: Fuzzy search (Ctrl+R) | P2 | Navigation |

### 3.7 Styling & Theming (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Styles: Base .tcss file | P1 | None |
| Themes: Dark theme .tcss | P1 | Base styles |
| Themes: Light theme .tcss | P1 | Base styles |
| Themes: Runtime theme switching | P2 | Themes basic |
| Responsive: Width detection | P2 | None |
| Responsive: Breakpoint system | P2 | Width detection |

### 3.8 Animation & Feedback (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Loading: Spinner widget | P3 | None |
| Loading: Progress bar widget | P3 | None |
| Feedback: Cursor blink | P3 | InputBar |
| Feedback: Focus indication | P3 | InputBar |

### 3.9 Documentation (Needs Breakdown)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Docstrings for all public APIs | P1 | Implementation |
| Getting started tutorial | P2 | Core features |
| Example applications | P2 | Core features |
| API reference generation | P2 | Docstrings |

### 3.10 Testing (Missing)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Unit tests for core widgets | P1 | Implementation |
| Integration tests for plugins | P1 | Implementation |
| Performance benchmarks | P2 | Core features |
| Compatibility test matrix | P2 | CI setup |

---

## 4. Dependency Graph

```
Phase 0: Project Setup
  |-- Create py.typed marker
  |-- Set up GitHub Actions CI

Phase 1: Foundation
  |-- Plugin base classes (ContentPlugin, CompletionProvider, ModeProvider)
  |-- Base App class
  |-- Base styles (.tcss)

Phase 2: Core Widgets (parallel)
  |-- InputBar basic
  |     |-- InputBar auto-grow
  |     |-- InputBar submit behavior
  |     |-- InputBar cursor/selection
  |-- Conversation basic
  |     |-- Conversation auto-scroll
  |     |-- Conversation virtual rendering
  |     |-- Conversation block management

Phase 3: History (parallel with Phase 2)
  |-- History storage format
  |     |-- History navigation
  |     |-- History search

Phase 4: Content Plugins (parallel)
  |-- Markdown basic
  |     |-- Markdown code blocks
  |     |-- Markdown streaming
  |-- Diff unified
  |     |-- Diff split view
  |     |-- Diff char-level
  |-- Terminal basic
  |     |-- Terminal colors
  |     |-- Terminal cursor

Phase 5: Completion
  |-- Completion provider interface
  |     |-- Completion overlay
  |     |-- Path completion

Phase 6: Polish
  |-- Themes (dark/light)
  |-- Theme switching
  |-- Responsive layout
  |-- Animation (spinner, progress)
  |-- Documentation
```

---

## 5. Recommendations

### 5.1 Immediate Priorities (P1 - Essential)

1. **Complete Project Setup**
   - Add py.typed marker file
   - Set up GitHub Actions CI with test matrix

2. **Define Plugin Architecture**
   - Create base classes for ContentPlugin, CompletionProvider, ModeProvider
   - This unblocks all plugin development

3. **Implement Core Widgets**
   - InputBar with basic multiline support
   - Conversation with scrollable container and virtual rendering
   - These are the primary user-facing components

4. **Essential Plugins**
   - Markdown rendering (headers, paragraphs, code blocks)
   - Diff unified view
   - Terminal ANSI support

### 5.2 Implementation Approach

1. **Test-Driven Development**
   - Write tests before implementation for each feature
   - Maintain 90%+ coverage from the start

2. **Incremental Delivery**
   - Each task should produce a working, testable artifact
   - Avoid large "integrate everything" tasks

3. **API-First Design**
   - Define public interfaces before implementation
   - Ensure examples in README work after each phase

### 5.3 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Textual API changes | Pin textual version, abstract Textual details |
| Performance issues | Design virtual rendering from start |
| Terminal compatibility | Test matrix on CI, document limitations |

---

## 6. Updated Task Breakdown

See updated TODO.md for the prioritized, atomic task breakdown derived from this analysis.

---

## 7. Acceptance Criteria Template

Each task in TODO.md should have:

```markdown
- [ ] **task-name**
  - Description of what needs to be done
  - **Acceptance Criteria:**
    - [ ] Criterion 1 (testable)
    - [ ] Criterion 2 (testable)
  - **Dependencies:** task-x, task-y
  - **Priority:** P1/P2/P3
```

---

## 8. Task-Specific Design Decisions

### 8.1 conversation-block-model Design Decisions

**Date:** 2026-04-14

#### Design Decision Record

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Timestamp format | `datetime` (timezone-aware UTC) | Standard library type, timezone-safe, serializable to ISO 8601 |
| Metadata mutability | Immutable - set once at block creation | Prevents accidental modification, supports reproducibility, simplifies caching |
| Session UUID | Auto-generate + optional constructor parameter | Defaults to UUID4 for convenience, allows explicit setting for session resumption |
| Public API | Add `get_block(block_id) -> BlockInfo` method | Read-only access pattern, returns copy to maintain immutability |

#### Refined Implementation Specification

**Block Data Model**

```python
@dataclass(frozen=True)
class BlockInfo:
    """Immutable block metadata container."""
    id: str                      # Format: "{session_uuid}-{sequence_number}"
    role: str                    # Generic role identifier (e.g., "user", "assistant", "system")
    content: str                 # Block content text
    metadata: dict[str, Any]     # Immutable dict set at creation
    timestamp: datetime          # Timezone-aware UTC datetime
```

**Session UUID Management**

```python
class Conversation(Widget):
    def __init__(
        self,
        session_uuid: str | None = None,
        **kwargs: Any
    ) -> None:
        self._session_uuid = session_uuid or str(uuid.uuid4())
        self._sequence_counter = 0
```

**Public API**

```python
def get_block(self, block_id: str) -> BlockInfo | None:
    """Retrieve block by ID. Returns None if not found."""
    # Search in-memory blocks
    # Return a copy to maintain immutability
```

#### Updated Acceptance Criteria

The task `conversation-block-model` should verify:

- [ ] `BlockInfo` dataclass defined with `frozen=True`
- [ ] Block ID format: `{session_uuid}-{sequence_number}` with atomic increment
- [ ] `role: str` (generic, extensible string type)
- [ ] `content: str` (full block content)
- [ ] `metadata: dict[str, Any]` immutable after creation (frozen dataclass)
- [ ] `timestamp: datetime` with UTC timezone (`datetime.now(timezone.utc)`)
- [ ] Session UUID auto-generated via `uuid.uuid4()` if not provided
- [ ] Optional `session_uuid` parameter in `Conversation.__init__`
- [ ] `get_block(block_id) -> BlockInfo | None` method for read-only access
- [ ] Unit tests for all BlockInfo properties
- [ ] Unit tests for session UUID generation and custom values
- [ ] Unit tests for timestamp timezone handling

#### Integration Points

| Component | Integration |
|-----------|-------------|
| `Conversation.append()` | Creates BlockInfo, increments sequence, stores in blocks dict |
| `Conversation.get_block()` | Returns BlockInfo copy or None |
| `SessionManager` (future) | Uses session_uuid for persistence |
| Pruning (future) | Uses get_block() for transparent retrieval |

#### UX Recommendations (2026-04-14)

| Recommendation | Rationale | Implementation |
|----------------|----------|----------------|
| Add `sequence: int` field | Display-friendly numbering for navigation ("Block 3 of 15") | Include in BlockInfo dataclass |
| Add `relative_timestamp` property | Human-readable display for timestamps | Computed property returning "2 min ago", "Yesterday", etc. |
| Add `get_block_at_index(index)` | O(1) navigation by sequence for smooth UX | Method to access block by sequential position |

#### Updated BlockInfo Specification

```python
@dataclass(frozen=True)
class BlockInfo:
    """Immutable block metadata container."""
    id: str                      # Format: "{session_uuid}-{sequence_number}"
    sequence: int                # Sequential number (0-indexed) for display
    role: str                    # Generic role identifier (e.g., "user", "assistant", "system")
    content: str                 # Block content text
    metadata: dict[str, Any]     # Immutable dict set at creation
    timestamp: datetime          # Timezone-aware UTC datetime

    @property
    def relative_timestamp(self) -> str:
        """Human-readable relative time (e.g., '2 min ago', 'Yesterday')."""
        # Calculate delta from now
        ...
```

#### Review Status

- [x] Functional analysis complete
- [ ] API Architect review pending
- [x] UI/UX Designer review complete

---

## 9. Next Steps

1. Review and approve this analysis
2. Update TODO.md with atomic tasks
3. Begin implementation with Phase 0 (Project Setup)
4. Request functional review after each task completion