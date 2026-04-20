# Summary: test-app-theme-css

## Task

Add App theme loading and CSS path tests to close testing coverage gap identified in `docs/development/test-coverage-review.md`.

## Implementation

Created `tests/test_app_theme_css.py` with 16 tests organized in 3 test classes:

### TestAppCSSPath (6 tests)
- CSS_PATH class attribute verification
- CSS file accessibility via importlib.resources
- CSS content validation (App styles, color variables)

### TestAppThemeProperty (6 tests)
- theme_name default value ("dark")
- theme_name initialization via constructor
- theme_name read-only property verification
- _theme_name internal storage

### TestAppThemeIntegration (4 tests)
- Document: theme_name does NOT change CSS_PATH (current behavior)
- Document: CSS_PATH is class-level, shared across instances
- Async test: theme_name persists in mounted app
- xfail test: marks desired future behavior for theme switching

## Key Findings

- **Theme switching is NOT implemented**: `theme_name` is stored but NOT used to load different CSS files
- **CSS_PATH is hardcoded** to `clitic/styles/base.tcss`
- **No theme TCSS files exist** in `src/clitic/themes/`

## Files Modified

- `tests/test_app_theme_css.py` - New test file (177 lines)
- `TODO.md` - Task marked complete, added to Done section

## Test Results

```
16 tests collected
15 passed, 1 xfailed (expected)
```

## Verification

```bash
make test-file FILE=tests/test_app_theme_css.py  # All tests pass
make typecheck  # Success: no issues found
make lint       # All checks passed
make test       # 647 tests passing, 85% coverage
```

## Completed

2026-04-20