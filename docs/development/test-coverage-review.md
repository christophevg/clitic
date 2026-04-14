# Test Coverage Review

**Date:** 2026-04-14
**Reviewer:** testing-engineer agent

## Summary

The clitic project has a well-organized test suite with comprehensive coverage of core functionality. The testing infrastructure uses pytest with asyncio support and coverage reporting. Tests are well-structured and follow good practices. However, there are notable gaps in testing of integration scenarios, asynchronous behavior, and some edge cases.

## Test Infrastructure Review

### Framework Configuration

- pytest with `asyncio_mode = "auto"` - correctly configured for async tests
- Coverage with branch coverage (`branch = true`) - good practice
- Multi-version testing via tox (Python 3.10, 3.11, 3.12) - excellent
- Coverage exclusions for standard cases (`pragma: no cover`, `__repr__`, `NotImplementedError`, `TYPE_CHECKING`)

### Test Organization

- No `conftest.py` for shared fixtures - consider adding one for common test utilities
- Tests mirror source structure - good organization
- Test file naming follows convention (`test_*.py`)

### Test Quality Observations

- Tests use descriptive docstrings - excellent practice
- Tests verify behavior, not implementation details
- Edge cases are well-tested in most areas
- Mock usage is appropriate and minimal

---

## Critical Gaps (Priority 8-10)

### 1. InputBar: Key event integration testing (9/10)

**Issue:** Missing tests for the `action_insert_newline` method. The tests mock `post_message` but don't verify that the newline is actually inserted when Shift+Enter is pressed. Tests verify the submit behavior but not the newline insertion behavior.

**Recommendation:** Add integration tests that verify the actual newline insertion behavior in the TextArea context.

### 2. App: Plugin integration with render cycle (9/10)

**Issue:** The `render_async` method on `ContentPlugin` has tests, but there are no integration tests verifying that plugins work correctly when rendering in an actual Textual app context. The App class `_trigger_submit` method is tested, but there's no test verifying the complete cycle from InputBar submit through App to registered handlers.

**Recommendation:** Add integration tests for:
- ContentPlugin `render_async` in actual app context
- Complete cycle: InputBar -> submit -> handler -> Conversation -> display
- Plugin lifecycle within app

### 3. Conversation: Resize and scroll integration (8/10)

**Issue:** The `on_resize` and `watch_scroll_y` methods are tested individually, but there are no integration tests verifying the complete cycle: content changes -> scroll position updates -> auto_scroll state updates -> CSS class changes. The `_update_auto_scroll_from_scroll_position` method lacks direct testing.

**Recommendation:** Add integration tests for the complete resize/scroll cycle.

---

## Important Improvements (Priority 5-7)

### 4. Session persistence: Concurrent access scenarios (7/10)

**Issue:** No tests for what happens when:
- Multiple `save_block` calls occur simultaneously
- File is locked or corrupted during write
- Session file grows very large (>100MB)

**Recommendation:** Add tests for concurrent access, file locking, and large file handling.

### 5. Conversation: Memory pruning edge cases (7/10)

**Issue:** While pruning is well-tested, missing scenarios:
- `_restore_pruned_blocks` when blocks have different line counts than stored (stale `_pruned_blocks` data)
- What happens if session file is deleted/corrupted after pruning
- Multiple `Conversation` instances with same session id

**Recommendation:** Add tests for pruning edge cases with stale data and corrupted files.

### 6. InputBar: Theme and language parameter behavior (6/10)

**Issue:** The `theme` and `language` parameters for syntax highlighting are passed to TextArea but never tested. No tests verify that syntax highlighting actually works for different languages.

**Recommendation:** Add tests for:
- Different language syntax highlighting
- Theme parameter behavior
- Language switching

### 7. App: Theme loading and CSS path (6/10)

**Issue:** No tests verify that the `CSS_PATH` is correctly loaded or that themes work. The `_theme_name` property is tested, but not its integration with TCSS theme files.

**Recommendation:** Add tests for CSS_PATH loading and theme integration.

### 8. Conversation: Error handling in render_line (6/10)

**Issue:** The `render_line` method doesn't have tests for error conditions like:
- Invalid block data in `_blocks` list
- Corrupted `_strips` list
- Width changes during rendering

**Recommendation:** Add tests for error conditions in rendering.

---

## Consider (Priority 1-4)

### 9. BlockInfo: Timestamp edge cases (4/10)

**Issue:** `relative_timestamp` tests cover common cases but not edge cases:
- Negative time deltas (future timestamps)
- Very large time deltas (years)
- Timezone-naive vs timezone-aware comparisons

**Recommendation:** Add tests for timestamp edge cases.

### 10. ShowcaseApp: Command-line argument handling (4/10)

**Issue:** The `main()` function has argument parsing for `--resume`, `--list-sessions`, and `--persistence`, but no tests for these CLI features.

**Recommendation:** Add tests for CLI argument parsing and functionality.

### 11. CompletionProvider: Async behavior edge cases (3/10)

**Issue:** The `get_completions_async` method is tested for successful completion, but not for:
- Exception handling
- Empty results vs error conditions
- Performance with large result sets

**Recommendation:** Add tests for async edge cases.

### 12. SessionManager: Platform-specific path handling (3/10)

**Issue:** The default session directory uses `Path.home()` which could behave differently across platforms. No tests for permission errors or non-existent home directories.

**Recommendation:** Add platform-specific path handling tests.

---

## Files Not Tested

The following source files have no dedicated tests:

- `/src/clitic/utils/__init__.py` - Empty module (no code to test)
- `/src/clitic/history/__init__.py` - Empty module (no code to test)
- `/src/clitic/themes/__init__.py` - Theme files (TCSS) - would need integration tests
- `/src/clitic/styles/__init__.py` - Style files (TCSS) - would need integration tests

---

## Test Quality Issues

### Tests that verify behavior correctly

- Exception tests in `test_exceptions.py` are exemplary - they test error messages, attributes, and hierarchy
- InputBar tests in `test_input_bar.py` are comprehensive with good edge case coverage
- Conversation tests in `test_conversation.py` cover virtual rendering thoroughly

### Tests that could be improved

- **`test_app.py`**: The `_trigger_submit` tests mock the registered handlers, which is appropriate. However, there's no test verifying that handlers can actually modify state when called by `_trigger_submit`.
- **`test_package.py`**: Only tests imports and basic existence - could be expanded to verify the `__all__` exports are complete and correctly typed.

### Positive Observations

- Tests use `tmp_path` fixture correctly for file operations
- Mock usage is minimal and appropriate
- Performance tests (e.g., `test_100k_lines_performance`) set realistic thresholds
- Memory tests use `tracemalloc` for accurate measurement

---

## Recommendations

### High Priority

1. **Add `tests/conftest.py`** for shared fixtures:
   - Mock Textual app instances
   - Temp session directories
   - Sample BlockInfo/Conversation fixtures

2. **Add integration tests** for:
   - Full app workflow (InputBar -> submit -> handler -> Conversation -> display)
   - Session persistence lifecycle (create -> save -> close -> resume)
   - Memory pruning with scroll restoration

### Medium Priority

3. **Add tests for CLI** (`__main__.py`):
   - Argument parsing
   - `--resume` functionality
   - `--list-sessions` output

4. **Improve coverage for edge cases**:
   - Large content handling (>10MB messages)
   - Unicode in content/metadata
   - Concurrent session access

### Lower Priority

5. **Add property-based testing** for:
   - BlockInfo serialization/deserialization round-trips
   - String handling in content (special characters, escape sequences)

---

## Current Test Files

| File | Purpose |
|------|---------|
| `test_app.py` | App class tests |
| `test_completion_base.py` | Completion provider tests |
| `test_conversation.py` | Conversation widget tests |
| `test_conversation_pruning.py` | Memory pruning tests |
| `test_exceptions.py` | Exception hierarchy tests |
| `test_input_bar.py` | InputBar widget tests |
| `test_package.py` | Package imports tests |
| `test_session_manager.py` | Session persistence tests |

---

## Tasks Created

See `TODO.md` under "Testing Coverage Improvements" section for the task breakdown.