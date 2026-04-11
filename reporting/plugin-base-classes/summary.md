# Summary: plugin-base-classes

**Task:** Create abstract base classes for plugin system

## What Was Implemented

Created a comprehensive plugin system with abstract base classes for content renderers, completion providers, and input mode providers.

## Changes Made

### 1. `src/clitic/plugins/base.py`

- **`Renderable` Protocol** - for content type flexibility (just `__str__`)
- **`Highlighter` Protocol** - for syntax highlighting (`highlight(text: str) -> str`)
- **`ContentPlugin` ABC** - base for content renderers:
  - Abstract `name` property
  - `priority` property (default 0)
  - Abstract `can_render()` and `render()` methods
  - `render_async()` with default implementation
  - `on_register()` and `on_unregister()` lifecycle hooks
- **`ModeProvider` ABC** - base for input mode providers:
  - Abstract `name` and `indicator` properties
  - `priority` property (default 0)
  - Abstract `detect()` and `get_highlighter()` methods
  - `on_enter()` and `on_exit()` lifecycle hooks

### 2. `src/clitic/completion/base.py`

- **`Completion` dataclass**:
  - `text: str` - text to insert
  - `display_text: str` - text to display in dropdown
  - `cursor_offset: int = 0`
  - `description: str = ""`
  - `priority: int = 0`
  - `metadata: dict[str, Any]`
  - Sorting, equality, and hashing support
- **`CompletionProvider` ABC**:
  - Abstract `name` property
  - `priority` property (default 0)
  - Abstract `get_completions()` method
  - `get_completions_async()` with default implementation

### 3. Tests

- `tests/test_plugin_base.py` - 37 tests for ContentPlugin and ModeProvider
- `tests/test_completion_base.py` - 25 tests for Completion and CompletionProvider

## Key Decisions

- Used `TYPE_CHECKING` for forward references to avoid circular imports
- Used `# noqa: B027` for intentionally empty lifecycle hook methods
- All plugin interfaces have consistent `priority` property
- `Completion` includes sorting by priority (higher first)

## Files Modified

- `src/clitic/plugins/base.py` (new)
- `src/clitic/completion/base.py` (new)
- `src/clitic/plugins/__init__.py` (exports)
- `src/clitic/completion/__init__.py` (exports)
- `src/clitic/__init__.py` (public API)
- `tests/test_plugin_base.py` (new)
- `tests/test_completion_base.py` (new)

## Acceptance Criteria

- [x] `src/clitic/plugins/base.py` exists with ContentPlugin ABC
- [x] `src/clitic/completion/base.py` exists with CompletionProvider ABC
- [x] Completion dataclass defined with text, display_text, cursor_offset, description, priority, metadata
- [x] Highlighter protocol defined for syntax highlighting
- [x] Renderable protocol defined for content type flexibility
- [x] All plugin interfaces have priority property for consistent ordering
- [x] ContentPlugin has on_register/on_unregister lifecycle hooks
- [x] ContentPlugin has render_async method for async rendering
- [x] ModeProvider has on_enter/on_exit lifecycle hooks
- [x] All base classes have proper type hints and docstrings
- [x] No `Any` type in public signatures (use str | Renderable)
- [x] Unit tests for base class interfaces (62 tests)