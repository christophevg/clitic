# Summary: base-styles

**Task:** Create base .tcss stylesheet for widgets

## What Was Implemented

Created the base TCSS (Textual CSS) stylesheet with color palette and widget styling definitions.

## Changes Made

### `src/clitic/styles/base.tcss`

- **Color palette**:
  - `$accent` - primary accent color (#3B82F6)
  - `$background` / `$background-light` - background colors
  - `$foreground` / `$foreground-muted` - text colors
  - `$error`, `$success`, `$warning`, `$info` - status colors

- **Widget styles**:
  - App base styling
  - Content blocks (user, assistant, system, tool)
  - Input bar styling
  - Scrollbar styling
  - Focus indicators
  - Button styling

### `src/clitic/core/app.py`

- Added `CSS_PATH` class variable to load base styles from package
- Uses `importlib.resources.files()` for package resource access

## Key Decisions

- Used TCSS variables for consistent color palette
- Defined styles for future widgets (input-bar, content-block)
- Focus indicators follow accent color theme
- Used `importlib.resources` for Python 3.10+ compatibility

## Files Modified

- `src/clitic/styles/base.tcss` (new)
- `src/clitic/core/app.py` (CSS_PATH)

## Acceptance Criteria

- [x] `src/clitic/styles/base.tcss` exists
- [x] Defines base widget styles (colors, padding, margins)
- [x] Included in package data via pyproject.toml (already configured)
- [x] App loads base styles automatically