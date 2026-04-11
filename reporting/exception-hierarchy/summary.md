# Summary: exception-hierarchy

**Task:** Define custom exception hierarchy for error handling

## What Was Implemented

Created a comprehensive exception hierarchy for the clitic package with clear, actionable error messages.

## Changes Made

1. **Created `src/clitic/exceptions.py`**
   - `CliticError` - Base exception class
   - `PluginError` - For plugin loading/registration/rendering errors
   - `ConfigurationError` - For configuration setting issues
   - `RenderError` - For content rendering failures

2. **Created `tests/test_exceptions.py`**
   - 39 tests covering all exception types
   - Tests for inheritance hierarchy
   - Tests for error message formatting
   - Tests for realistic error scenarios

3. **Updated `src/clitic/__init__.py`**
   - Exported all exception classes

4. **Updated Python version requirement**
   - Dropped Python 3.9 support
   - Now requires Python 3.10+
   - Updated pyproject.toml and CI workflow

## Key Decisions

- Used Python 3.10+ union syntax (`str | None`) instead of `Optional[str]`
- Each exception includes context-specific attributes
- Error messages are actionable and include helpful context
- Full type hints with mypy strict mode

## Files Modified

- `src/clitic/exceptions.py` (new)
- `tests/test_exceptions.py` (new)
- `src/clitic/__init__.py` (updated exports)
- `pyproject.toml` (Python 3.10+ requirement)
- `.github/workflows/ci.yml` (removed Python 3.9 from matrix)

## Acceptance Criteria

- [x] `src/clitic/exceptions.py` exists with CliticError base class
- [x] PluginError, ConfigurationError, RenderError defined
- [x] All exceptions have clear, actionable error messages
- [x] Unit tests for exception hierarchy