# TODO

## Backlog

### Phase 2: InputBar Widget (P1 - Essential)

- [x] **inputbar-basic**
  - Create basic multiline input widget (FR-001 partial)
  - **Acceptance Criteria:**
    - [x] `src/clitic/widgets/input_bar.py` exists with InputBar class
    - [x] InputBar extends Textual Widget
    - [x] Supports multiline text editing
    - [x] Enter submits, Shift+Enter inserts newline (default behavior)
    - [x] Exported from `src/clitic/__init__.py`
    - [x] Unit tests for InputBar
  - **Dependencies:** base-app-class
  - **Priority:** P1

- [x] **inputbar-cursor**
  - Add cursor movement and selection support (FR-001)
  - **Acceptance Criteria:**
    - [x] Full cursor movement (arrows, Home, End, Ctrl+arrows)
    - [x] Text selection (Shift+arrows, Ctrl+A)
    - [x] Copy/paste support (Ctrl+C, Ctrl+V)
    - [x] Visual selection highlighting
  - **Dependencies:** inputbar-basic
  - **Priority:** P1

- [x] **inputbar-autogrow**
  - Add auto-grow with configurable max height (FR-001)
  - **Acceptance Criteria:**
    - [x] Widget height expands as content grows
    - [x] Configurable max_height parameter (default: 10 lines)
    - [x] Internal scrolling when content exceeds max_height
    - [x] Visual line wrapping (not logical line breaks)
  - **Dependencies:** inputbar-basic
  - **Priority:** P1

- [x] **inputbar-submit-config**
  - Add configurable submit behavior (FR-001)
  - **Acceptance Criteria:**
    - [x] Configurable: Enter submits vs Shift+Enter submits
    - [x] on_submit event/decorator for handling submissions
    - [x] Submit returns text and clears input
  - **Dependencies:** inputbar-basic
  - **Priority:** P1

### Phase 3: Conversation Widget (P1 - Essential)

- [x] **conversation-basic**
  - Create basic scrollable content container (FR-006)
  - **Acceptance Criteria:**
    - [x] `src/clitic/widgets/conversation.py` exists with Conversation class
    - [x] Scrollable vertical container
    - [x] append(role, content) method to add blocks
    - [x] Mouse scroll and keyboard scroll support
    - [x] Exported from `src/clitic/__init__.py`
    - [x] Unit tests for Conversation
  - **Dependencies:** base-app-class
  - **Priority:** P1

- [ ] **conversation-auto-scroll**
  - Add auto-scroll with pause/resume (FR-006)
  - **Acceptance Criteria:**
    - [ ] Auto-scroll to bottom on new content (configurable)
    - [ ] Pause auto-scroll when user scrolls up
    - [ ] Resume auto-scroll when user scrolls to bottom
    - [ ] Visual indicator when auto-scroll is paused
  - **Dependencies:** conversation-basic
  - **Priority:** P1

- [ ] **conversation-virtual-rendering**
  - Add virtual rendering for performance (FR-006, NFR-003)
  - **Acceptance Criteria:**
    - [ ] Only visible content blocks are rendered
    - [ ] Supports 100,000+ lines without performance degradation
    - [ ] Memory usage < 50MB for 10,000 blocks
    - [ ] Benchmark test for large content
  - **Dependencies:** conversation-basic
  - **Priority:** P1

- [ ] **conversation-block-management**
  - Add content block management (FR-007)
  - **Acceptance Criteria:**
    - [ ] Block types: user, assistant, system, tool
    - [ ] Pruning: remove old blocks when count exceeds threshold
    - [ ] Navigation: Alt+Up/Down to move between blocks
    - [ ] Each block has unique ID and metadata
  - **Dependencies:** conversation-virtual-rendering
  - **Priority:** P1

### Phase 4: History System (P1 - Essential)

- [ ] **history-storage**
  - Create JSON Lines storage format (FR-003)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/history/manager.py` exists with HistoryManager class
    - [ ] JSON Lines format with timestamp, text, metadata
    - [ ] Configurable history file path
    - [ ] Append-only writes for durability
    - [ ] Load history from file on initialization
    - [ ] Unit tests for storage format
  - **Dependencies:** None
  - **Priority:** P1

- [ ] **history-navigation**
  - Add history navigation in InputBar (FR-003)
  - **Acceptance Criteria:**
    - [ ] Up arrow at cursor start navigates to previous entry
    - [ ] Down arrow at cursor end navigates to next entry
    - [ ] Draft preserved when navigating (saved/restored)
    - [ ] HistoryManager integrated with InputBar
    - [ ] Integration tests for navigation
  - **Dependencies:** history-storage, inputbar-basic
  - **Priority:** P1

### Phase 5: Content Plugins (P1 - Essential)

- [ ] **plugin-markdown-basic**
  - Create Markdown renderer with basic elements (FR-009)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/plugins/markdown.py` exists with MarkdownPlugin class
    - [ ] Renders headers (h1-h6), paragraphs, lists
    - [ ] Renders inline code and code blocks
    - [ ] Renders links (clickable)
    - [ ] Integrates with Conversation via plugin interface
    - [ ] Unit tests for markdown rendering
  - **Dependencies:** plugin-base-classes, conversation-basic
  - **Priority:** P1

- [ ] **plugin-markdown-code-blocks**
  - Add syntax highlighting in code blocks (FR-009)
  - **Acceptance Criteria:**
    - [ ] Syntax highlighting by language tag
    - [ ] Support common languages (Python, JavaScript, Bash)
    - [ ] Extensible highlighter interface
    - [ ] Fallback to plain text for unknown languages
  - **Dependencies:** plugin-markdown-basic
  - **Priority:** P1

- [ ] **plugin-diff-unified**
  - Create unified diff renderer (FR-010)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/plugins/diff.py` exists with DiffPlugin class
    - [ ] Parses unified diff format
    - [ ] Shows +, -, ~ line annotations
    - [ ] Syntax highlighting in diff context
    - [ ] Unit tests for diff parsing and rendering
  - **Dependencies:** plugin-base-classes, conversation-basic
  - **Priority:** P1

- [ ] **plugin-terminal-ansi**
  - Create terminal/ANSI renderer (FR-011)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/plugins/terminal.py` exists with TerminalPlugin class
    - [ ] Full SGR sequence support (colors, styles)
    - [ ] 16-color, 256-color, and true color support
    - [ ] Handles malformed sequences gracefully
    - [ ] Unit tests for ANSI parsing
  - **Dependencies:** plugin-base-classes, conversation-basic
  - **Priority:** P1

- [ ] **plugin-error-handling**
  - Add graceful error handling for plugin failures
  - **Acceptance Criteria:**
    - [ ] ContentPlugin.render_safe() method wraps render() with error handling
    - [ ] Plugin failures logged with context
    - [ ] Fallback widget returned on error (plain text)
    - [ ] Plugin errors don't crash the application
    - [ ] Integration tests for error scenarios
  - **Dependencies:** plugin-base-classes, plugin-markdown-basic
  - **Priority:** P1

### Phase 6: Themes (P1 - Essential)

- [ ] **themes-basic**
  - Create dark and light themes (FR-019)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/themes/dark.tcss` exists with dark theme
    - [ ] `src/clitic/themes/light.tcss` exists with light theme
    - [ ] Themes define: colors, backgrounds, borders, accents
    - [ ] App accepts theme parameter ("dark" or "light")
    - [ ] Theme loaded on app start
  - **Dependencies:** base-styles
  - **Priority:** P1

### Phase 7: Completion (P2 - Important)

- [ ] **completion-provider-interface**
  - Integrate completion provider interface with InputBar (FR-004, FR-015)
  - **Acceptance Criteria:**
    - [ ] CompletionProvider ABC from Phase 1 integrated
    - [ ] Completion dataclass from Phase 1 used
    - [ ] Provider registry in App
    - [ ] InputBar accepts completion_providers parameter
    - [ ] Unit tests for provider integration
  - **Dependencies:** plugin-base-classes, inputbar-basic
  - **Priority:** P2

- [ ] **completion-overlay**
  - Create completion dropdown overlay (FR-004)
  - **Acceptance Criteria:**
    - [ ] Overlay widget appears on Tab trigger
    - [ ] Shows filtered completion suggestions
    - [ ] Arrow keys + Enter to select
    - [ ] Escape to dismiss
    - [ ] Integration with InputBar
  - **Dependencies:** completion-provider-interface, inputbar-basic
  - **Priority:** P2

- [ ] **completion-path**
  - Create file path completion provider (FR-004)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/completion/path.py` exists with PathCompletion class
    - [ ] Fuzzy matching for file paths
    - [ ] Handles ~ expansion
    - [ ] Respects .gitignore by default
    - [ ] Unit tests for path completion
  - **Dependencies:** completion-provider-interface
  - **Priority:** P2

- [ ] **history-search**
  - Add fuzzy history search (FR-003)
  - **Acceptance Criteria:**
    - [ ] Ctrl+R opens history search overlay
    - [ ] Fuzzy matching through history entries
    - [ ] Arrow keys to navigate matches
    - [ ] Enter to select and insert
    - [ ] Unit tests for history search
  - **Dependencies:** history-storage
  - **Priority:** P2

### Phase 8: Advanced Features (P2 - Important)

- [ ] **conversation-block-interactivity**
  - Add block interactivity (FR-008)
  - **Acceptance Criteria:**
    - [ ] Expand/collapse toggle for block details
    - [ ] Click to select block
    - [ ] Copy block content to clipboard
    - [ ] Right-click or key for context menu
  - **Dependencies:** conversation-block-management
  - **Priority:** P2

- [ ] **plugin-markdown-streaming**
  - Add streaming markdown support (FR-009)
  - **Acceptance Criteria:**
    - [ ] Incremental updates without full re-render
    - [ ] Supports 60+ updates per second
    - [ ] Smooth rendering of streaming content
    - [ ] Performance benchmark test
  - **Dependencies:** plugin-markdown-basic
  - **Priority:** P2

- [ ] **plugin-diff-split**
  - Add side-by-side diff view (FR-010)
  - **Acceptance Criteria:**
    - [ ] Split view with original and modified side by side
    - [ ] Auto-switch between unified/split based on terminal width
    - [ ] Synchronized scrolling
    - [ ] Character-level highlighting within lines
  - **Dependencies:** plugin-diff-unified
  - **Priority:** P2

- [ ] **plugin-tree**
  - Create collapsible tree widget (FR-012)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/widgets/tree.py` exists with Tree class
    - [ ] Expand/collapse nodes
    - [ ] Configurable icons for folders, files
    - [ ] Keyboard navigation through tree
    - [ ] Filter/search by text pattern
  - **Dependencies:** base-app-class
  - **Priority:** P2

- [ ] **plugin-table**
  - Create table widget (FR-013)
  - **Acceptance Criteria:**
    - [ ] `src/clitic/widgets/table.py` exists with Table class
    - [ ] Auto-sized columns or fixed widths
    - [ ] Optional header row
    - [ ] Column alignment (left, center, right)
    - [ ] Horizontal scrolling for wide tables
    - [ ] Optional sorting on header click
  - **Dependencies:** base-app-class
  - **Priority:** P2

### Phase 9: Polish (P3 - Nice-to-have)

- [ ] **inputbar-syntax-highlighting**
  - Add syntax highlighting in InputBar (FR-002)
  - **Acceptance Criteria:**
    - [ ] Markdown and Shell modes supported
    - [ ] Auto-detect based on content patterns
    - [ ] Async highlighting to avoid blocking
    - [ ] Custom syntax highlighters via plugin
  - **Dependencies:** inputbar-basic
  - **Priority:** P3

- [ ] **inputbar-mode-switching**
  - Add input mode switching (FR-005)
  - **Acceptance Criteria:**
    - [ ] At least text and shell/command modes
    - [ ] Visual indicator of current mode
    - [ ] Single hotkey to toggle modes
    - [ ] Extensible: custom modes via ModeProvider
  - **Dependencies:** inputbar-basic, plugin-base-classes
  - **Priority:** P3

- [ ] **theme-switching**
  - Add runtime theme switching (FR-019)
  - **Acceptance Criteria:**
    - [ ] Change theme without restart
    - [ ] Persist theme preference
    - [ ] Hotkey to cycle themes
  - **Dependencies:** themes-basic
  - **Priority:** P3

- [ ] **responsive-layout**
  - Add responsive layout system (FR-017)
  - **Acceptance Criteria:**
    - [ ] Detect terminal width changes
    - [ ] Define layout changes at width thresholds
    - [ ] Auto-switch between layouts
  - **Dependencies:** base-app-class
  - **Priority:** P3

- [ ] **animation-loading**
  - Add loading indicators (FR-020)
  - **Acceptance Criteria:**
    - [ ] Spinner widget for indeterminate progress
    - [ ] Progress bar widget
    - [ ] Customizable animations
    - [ ] Toggle visibility based on state
  - **Dependencies:** base-app-class
  - **Priority:** P3

- [ ] **animation-feedback**
  - Add visual feedback (FR-021)
  - **Acceptance Criteria:**
    - [ ] Blinking cursor in input widget
    - [ ] Focus indication for widgets
    - [ ] Hover states on mouse hover
    - [ ] Error highlighting
  - **Dependencies:** inputbar-basic
  - **Priority:** P3

### Phase 9.5: UX Polish (P2 - Important)

- [ ] **keyboard-shortcuts-help**
  - Create help overlay with shortcut reference (UX-004)
  - **Acceptance Criteria:**
    - [ ] F1 shows shortcut overlay
    - [ ] Overlay lists all shortcuts by context (Global, InputBar, Conversation)
    - [ ] Escape dismisses overlay
    - [ ] `?` key also triggers help overlay
    - [ ] Shortcuts categorized and searchable
  - **Dependencies:** base-app-class, base-styles
  - **Priority:** P2

- [ ] **focus-indication**
  - Implement visible focus indicators for all widgets (UX-001)
  - **Acceptance Criteria:**
    - [ ] InputBar has distinct focused/unfocused states
    - [ ] Focus ring/outline visible on focused widget
    - [ ] Focus moves logically with Tab
    - [ ] Focus restoration after actions
    - [ ] Focus states defined in base styles
  - **Dependencies:** base-styles
  - **Priority:** P2

- [ ] **contextual-hints**
  - Add contextual hints bar below InputBar (UX-005)
  - **Acceptance Criteria:**
    - [ ] Hints bar shows current context (e.g., "Enter to submit | Shift+Enter for newline")
    - [ ] Hints update based on current widget focus
    - [ ] Hints can be disabled via configuration
    - [ ] Hints fade/compact in narrow terminals
  - **Dependencies:** inputbar-basic, base-styles
  - **Priority:** P2

### Phase 9.6: Accessibility (P1 - Essential)

- [ ] **accessibility-high-contrast**
  - Ensure WCAG AA contrast in themes (UX-006)
  - **Acceptance Criteria:**
    - [ ] Dark theme: minimum 4.5:1 contrast ratio for text
    - [ ] Light theme: minimum 4.5:1 contrast ratio for text
    - [ ] Contrast verified via automated testing (e.g., contrast-ratio tool)
    - [ ] Color not sole information indicator (icons + text + color)
    - [ ] Documentation of color choices and contrast ratios
  - **Dependencies:** themes-basic
  - **Priority:** P1

- [ ] **accessibility-reduced-motion**
  - Implement reduced motion option (UX-007)
  - **Acceptance Criteria:**
    - [ ] `animations=False` parameter on App
    - [ ] All animations respect the setting
    - [ ] Instant transitions when animations disabled
    - [ ] Cursor blink respects reduced-motion
    - [ ] Documentation of accessibility options
  - **Dependencies:** base-app-class
  - **Priority:** P1

- [ ] **accessibility-screen-reader**
  - Add screen reader compatibility (UX-008)
  - **Acceptance Criteria:**
    - [ ] Content blocks have accessible names
    - [ ] State changes announced (new messages, errors)
    - [ ] InputBar state is accessible
    - [ ] Conversation acts as live region for updates
    - [ ] Test with at least one screen reader
  - **Dependencies:** conversation-basic, inputbar-basic
  - **Priority:** P2

### Phase 9.7: Error Handling UX (P2 - Important)

- [ ] **error-inline-validation**
  - Add inline validation error display (UX-009)
  - **Acceptance Criteria:**
    - [ ] Validation errors appear below InputBar
    - [ ] Errors clear when input is corrected
    - [ ] Error messages are specific and actionable
    - [ ] Visual styling distinct from normal text (red/error color)
  - **Dependencies:** inputbar-basic, base-styles
  - **Priority:** P2

- [ ] **error-toast-notifications**
  - Add toast notification system (UX-010)
  - **Acceptance Criteria:**
    - [ ] Toast appears at top-right of screen
    - [ ] Toast auto-dismisses after configurable duration (default 3s)
    - [ ] Toast has dismiss button (x)
    - [ ] Multiple toasts queue properly
    - [ ] Toast types: info, success, warning, error
  - **Dependencies:** base-app-class, base-styles
  - **Priority:** P2

- [ ] **error-fullscreen**
  - Add full-screen error for critical issues (UX-011)
  - **Acceptance Criteria:**
    - [ ] Full-screen overlay for critical errors
    - [ ] Clear error title and description
    - [ ] Actionable next steps
    - [ ] Recovery options (Retry, Reset, Exit)
  - **Dependencies:** base-app-class, base-styles
  - **Priority:** P2

### Phase 10: Documentation (P2 - Important)

- [ ] **docstrings**
  - Add docstrings for all public APIs (NFR-008)
  - **Acceptance Criteria:**
    - [ ] All public classes have docstrings
    - [ ] All public methods have docstrings
    - [ ] Examples in docstrings where appropriate
    - [ ] Docstring coverage check passes
  - **Dependencies:** All implementation tasks
  - **Priority:** P2

- [ ] **api-reference**
  - Generate API reference documentation
  - **Acceptance Criteria:**
    - [ ] API reference generated from docstrings (e.g., Sphinx, MkDocs)
    - [ ] All public exports documented
    - [ ] Type hints rendered in documentation
    - [ ] Examples linked from API reference
  - **Dependencies:** docstrings
  - **Priority:** P2

- [ ] **plugin-development-guide**
  - Create guide for plugin developers
  - **Acceptance Criteria:**
    - [ ] `docs/plugin-development.md` exists
    - [ ] Covers ContentPlugin, CompletionProvider, ModeProvider
    - [ ] Working example plugin with tests
    - [ ] Plugin registration patterns documented
  - **Dependencies:** Phase 1-5 complete
  - **Priority:** P2

- [ ] **examples**
  - Create working example applications
  - **Acceptance Criteria:**
    - [ ] `examples/chat.py`: minimal chat interface
    - [ ] `examples/markdown_viewer.py`: markdown rendering demo
    - [ ] `examples/diff_viewer.py`: diff rendering demo
    - [ ] All examples run without errors
  - **Dependencies:** Phase 1-5 complete
  - **Priority:** P2

- [ ] **tutorial**
  - Create getting started tutorial (NFR-008)
  - **Acceptance Criteria:**
    - [ ] `docs/tutorial.md` exists
    - [ ] Step-by-step guide for building chat app
    - [ ] Covers InputBar, Conversation, plugins
    - [ ] All code snippets tested
  - **Dependencies:** Phase 1-5 complete
  - **Priority:** P2

## Done

- [x] **conversation-basic**
  - Created Conversation widget extending VerticalScroll
  - Internal _ContentBlock widget for each message
  - append(role, content) method adds blocks
  - Supports user, assistant, system, tool roles
  - clear() method removes all blocks
  - block_count property
  - Scroll actions: up, down, pageup, pagedown, home, end
  - 23 new tests for Conversation
  - Total: 251 tests passing

- [x] **inputbar-submit-config**
  - Added configurable submit behavior to InputBar
  - `submit_on_enter` parameter (default: True)
  - When True: Enter submits, Shift+Enter inserts newline (default)
  - When False: Shift+Enter submits, Enter inserts newline
  - Property `submit_on_enter` for runtime access
  - Updated key handling logic in `on_key()` method
  - 9 new tests for configurable submit behavior
  - Total: 228 tests passing

- [x] **inputbar-autogrow**
  - Added auto-grow functionality to InputBar
  - Widget height expands as content grows (height: auto CSS)
  - Configurable max_height parameter (default: 10 lines)
  - Internal scrolling when content exceeds max_height (via ScrollView)
  - Visual line wrapping via wrapped_document.height
  - 12 new tests for auto-grow functionality
  - Total: 218 tests passing

- [x] **inputbar-cursor**
  - Added cursor movement and selection support to InputBar
  - Full cursor movement (arrows, Home, End, Ctrl+arrows) inherited from TextArea
  - Text selection (Shift+arrows, Ctrl+A) inherited from TextArea
  - Copy/paste support (Ctrl+C, Ctrl+V) inherited from TextArea
  - Visual selection highlighting via TextArea CSS class
  - Added read_only parameter to InputBar constructor
  - 54 new tests for cursor/selection/clipboard functionality
  - Total: 205 tests passing

- [x] **inputbar-basic**
  - Created InputBar widget extending TextArea
  - Enter submits, Shift+Enter inserts newline
  - 26 tests with full coverage

- [x] **base-styles**
  - Created base.tcss with color palette and widget styles
  - App loads styles automatically via CSS_PATH

- [x] **base-app-class**
  - Created App class extending Textual's App
  - Plugin management with register/unregister
  - on_submit decorator for input handling
  - 19 tests with full coverage

- [x] **plugin-base-classes**
  - Created ContentPlugin, ModeProvider, CompletionProvider ABCs
  - Defined Renderable, Highlighter protocols
  - Created Completion dataclass
  - 62 tests with full coverage

- [x] **exception-hierarchy**
  - Created CliticError, PluginError, ConfigurationError, RenderError
  - Full test coverage (39 tests)
  - Updated project to Python 3.10+ for modern syntax

- [x] **showcase-application**
  - Executable module showcasing implemented features
  - `python -m clitic` runs the showcase
  - Tests verify showcase runs without error

- [x] **setup-ci**
  - Created `.github/workflows/ci.yml` with test matrix
  - Tests run on Python 3.9, 3.10, 3.11, 3.12
  - Tests run on macOS, Linux, Windows
  - Typecheck and lint jobs with mypy --strict

- [x] **setup-py.typed**
  - Created `src/clitic/py.typed` marker file for PEP 561 compatibility
  - Package configured with `Typing :: Typed` classifier

- [x] **fix-quickstart-example**
  - Fixed bug in README.md Quick Start (conversation defined before use)
  - Removed unused input_bar variable for cleaner example

- [x] **package-structure**
  - Created src/clitic package structure
  - Created tests directory
  - pyproject.toml configured with dependencies and dev tools

- [x] **makefile**
  - Created Makefile with development workflow commands
  - setup, install, test, typecheck, lint, format, build, publish targets

- [x] **basic-tests**
  - Created tests/test_package.py with import and version tests