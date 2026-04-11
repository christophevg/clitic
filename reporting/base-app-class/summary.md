# Summary: base-app-class

**Task:** Create App class extending Textual App with sensible defaults

## What Was Implemented

Created the main App class that extends Textual's App with plugin management and input handling capabilities.

## Changes Made

### `src/clitic/core/app.py`

- **App class extending TextualApp**:
  - `title` parameter (set via property after super().__init__())
  - `theme_name` parameter (stored internally as `_theme_name`)
  - Avoided conflict with Textual's `theme` property

- **Plugin management**:
  - `_plugins: list[ContentPlugin]` internal registry
  - `register_plugin(plugin)` - calls `plugin.on_register(self)`
  - `unregister_plugin(plugin)` - calls `plugin.on_unregister(self)`
  - `get_plugins()` - returns copy of plugins list

- **Input handling**:
  - `@app.on_submit` decorator for registering handlers
  - `_trigger_submit(text)` for testing

### Files Modified

- `src/clitic/core/app.py` (new)
- `src/clitic/core/__init__.py` (exports)
- `src/clitic/__init__.py` (public API)
- `src/clitic/__main__.py` (updated showcase)
- `tests/test_app.py` (new)

## Key Decisions

- Used `theme_name` instead of `theme` to avoid conflict with Textual's existing `theme` property
- Set `title` via property after `super().__init__()` since Textual's App doesn't accept title in constructor
- Plugin registration calls lifecycle hooks immediately
- Handlers stored in list and called in registration order

## Acceptance Criteria

- [x] `src/clitic/core/app.py` exists with App class
- [x] App accepts title and theme_name parameters
- [x] App provides on_submit event decorator
- [x] App has register_plugin() method for explicit plugin registration
- [x] App exported from `src/clitic/__init__.py`
- [x] Unit tests for App initialization (19 tests)
- [x] Working example: can create and run minimal app