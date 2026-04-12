# Summary: inputbar-autogrow

**Task:** Add auto-grow functionality to InputBar widget
**Date:** 2026-04-12
**Status:** COMPLETED

---

## What Was Implemented

### 1. Auto-Grow Functionality

Implemented auto-grow for InputBar using Textual's built-in `height: auto` CSS property:

- **`max_height` parameter** - Added to `__init__` with default value of 10 lines
- **`DEFAULT_CSS`** - Added CSS with `height: auto` and `min-height: 1`
- **`max_height` property** - Added getter and setter with `refresh()` call on setter
- **`get_content_height()` method** - Override that returns visual line count clamped to `[1, max_height]`

### 2. Key Implementation Details

- **`wrapped_document.height`** returns visual lines (after soft wrapping), not logical lines
- **`max(1, min(content_lines, self._max_height))`** ensures minimum height of 1 line
- **`self.refresh()`** triggers layout recalculation when `max_height` changes
- TextArea's internal ScrollView handles scrolling automatically when content exceeds widget height

### 3. Code Changes

#### `src/clitic/widgets/input_bar.py`
- Added `Size` import from `textual.geometry`
- Added `DEFAULT_CSS` class attribute with `height: auto; min-height: 1;`
- Added `max_height` parameter to `__init__` (default: 10)
- Added `_max_height` instance variable
- Added `max_height` property getter/setter
- Added `get_content_height()` method override

#### `tests/test_input_bar.py`
- Added `TestInputBarAutoGrow` test class with 12 tests

---

## Acceptance Criteria Verification

| Criteria | Status | Notes |
|----------|--------|-------|
| Widget height expands as content grows | ✅ | Via `height: auto` CSS and `get_content_height()` |
| Configurable max_height parameter | ✅ | Default 10, setter triggers refresh |
| Internal scrolling when content exceeds max_height | ✅ | ScrollView handles automatically |
| Visual line wrapping | ✅ | `wrapped_document.height` returns visual lines |

---

## Test Results

- **Total tests:** 218 (up from 205)
- **All passing:** Yes
- **Type checking:** No issues (mypy --strict)
- **Linting:** All checks passed

---

## Technical Approach

The implementation leverages Textual's built-in auto-height mechanism:

1. **`height: auto` CSS** - Tells Textual to call `get_content_height()` during layout
2. **`get_content_height()` override** - Returns the wrapped line count clamped to `max_height`
3. **ScrollView parent class** - Automatically enables scrolling when content exceeds visible area

This approach is elegant because it uses Textual's native layout system rather than manual height calculations.

---

## Next Steps

The next task in the backlog is:
- **inputbar-submit-config**: Add configurable submit behavior