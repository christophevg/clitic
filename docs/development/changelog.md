# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Plugin System Integration**: Content rendering plugins now integrate with Conversation widget
  - Blocks with `content_type` metadata are routed to matching plugins
  - Built-in `MarkdownPlugin` renders Markdown content with formatting
  - Fallback to plain text when no plugin matches or rendering fails
  - Plugin priority ordering (higher priority plugins checked first)
  - Role labels preserved on plugin-rendered content
- **MarkdownPlugin**: Built-in plugin for rendering Markdown content
  - Supports `text/markdown`, `markdown`, and `markdown/*` content types
  - Renders headers, bold, italic, lists, code blocks, and links
  - High priority (10) for default handling
- **App Plugin Methods**: New methods for plugin management
  - `register_plugin(plugin)` - Register a content plugin
  - `unregister_plugin(plugin)` - Unregister a plugin
  - `get_plugins()` - Get list of registered plugins
  - `get_plugin_for_content(content_type, content)` - Find best matching plugin
- **Conversation Plugin Support**: New `plugins` parameter in `__init__`
  - Accepts list of ContentPlugin instances
  - Routes content to plugins based on `content_type` metadata
  - Graceful fallback on plugin failure
- **Block Navigation**: Navigate between conversation blocks with keyboard
  - Alt+Up/Down to select previous/next block
  - Escape to clear selection
  - Cyan highlighting for selected blocks
  - Auto-scroll centers selected block in viewport
  - Configurable wrap behavior and visual bell
  - Transparent loading of pruned blocks during navigation
- `BlockInfo` frozen dataclass for immutable block information
  - `block_id`: Unique identifier with session UUID prefix
  - `role`: Message role (user, assistant, system, tool)
  - `content`: Text content
  - `metadata`: Custom application data (immutable)
  - `timestamp`: UTC-aware creation timestamp
  - `sequence`: 0-indexed position in conversation
  - `relative_timestamp`: Human-readable time property
- `Conversation.session_id` property for session tracking
- `Conversation.get_block(block_id)` method for O(1) block lookup by ID
- `Conversation.get_block_at_index(index)` method for O(1) block lookup by position
- `Conversation.append()` now accepts optional `metadata` parameter
- `Conversation.__init__` now accepts optional `session_uuid` parameter
- `Conversation` navigation properties:
  - `selected_block`: Reactive property for selected block ID
  - `selected_block_index`: 0-indexed position of selected block
  - `selected_block_info`: BlockInfo for selected block
  - `wrap_navigation`: Configurable wrap at boundaries
  - `navigation_bell`: Configurable visual bell at boundaries

### Changed

- Block ID format changed from `block-{counter}` to `{session_uuid}-{sequence}`
- `Conversation.clear()` no longer resets the sequence counter
- Sequence counter continues incrementing across clear operations
- Selected blocks now display in cyan without background highlighting

## [0.1.0] - 2026-04-11

### Added

- Initial package structure with pyproject.toml
- Makefile with development workflow commands
- Basic tests (package import and version)

### Project Setup

- py.typed marker file for PEP 561 compliance
- GitHub Actions CI workflow
  - Test matrix: Python 3.10, 3.11, 3.12
  - OS: macOS, Linux, Windows
  - Typecheck with mypy --strict
  - Lint with ruff

### Foundation

- Exception hierarchy with `CliticError`, `PluginError`, `ConfigurationError`, `RenderError`
- Plugin base classes:
  - `ContentPlugin` ABC for content renderers
  - `ModeProvider` ABC for input mode providers
  - `CompletionProvider` ABC for completion sources
  - `Renderable` and `Highlighter` protocols
- `Completion` dataclass for completion suggestions
- `App` class extending Textual's App
  - Plugin management (`register_plugin`, `unregister_plugin`)
  - Input handling (`@app.on_submit` decorator)
  - Theme support
- Base TCSS stylesheet with color palette

### Widgets

- `InputBar` widget for multiline text input
  - Extends Textual's TextArea
  - Enter to submit, Shift+Enter for newline
  - Placeholder text support
  - Multiple themes (monokai, github_light, etc.)
  - Disabled state handling
  - BINDINGS for proper key handling

### Showcase

- Interactive TUI showcase application
- Light theme with blue accents
- Message display with proper contrast
- Auto-focus on input bar

### Documentation

- CLAUDE.md for Claude Code guidance
- Showcase application demonstrating implemented features
- Sphinx documentation setup for readthedocs.org
- API reference for widgets (InputBar)

### Changed

- Dropped Python 3.9 support (requires Python 3.10+)
- Updated README.md Quick Start example