# Functional Review: conversation-block-pruning

**Review Date**: 2026-04-14
**Reviewer**: Functional Analyst Agent
**Task**: conversation-block-pruning (FR-007)

## Status: REJECTED

The implementation is mostly correct but has one critical acceptance criterion not met and one minor issue that should be addressed.

---

## Acceptance Criteria Review

| Criterion | Status | Notes |
|-----------|--------|-------|
| Configurable `max_blocks_in_memory` threshold (default: 100, 0 = unlimited) | PASS | Default is 100, setter validates non-negative, 0 disables pruning |
| When exceeded, oldest blocks removed from memory BUT still in JSONL file | PASS | Pruning evicts from `_blocks` list, data persists in file |
| Pruning never deletes data — only evicts from memory | PASS | No file deletion occurs during pruning |
| Track which blocks are in memory vs persisted only | PASS | `_pruned_blocks` dict tracks evicted blocks, `in_memory_block_count` and `pruned_block_count` properties available |
| `get_block(block_id)` retrieves from memory, falls back to file | PASS | Lines 656-685 implement fallback via `load_block_by_sequence()` |
| `_restore_pruned_blocks()` method for transparent reload from file | PASS | Lines 302-401 implement lazy loading with concurrent loading guard |
| Scrolling up to pruned blocks triggers transparent reload from file | **FAIL** | Not implemented |
| Loading indicator briefly shown during block retrieval | N/A | Marked as optional in task description |

---

## Issues Found

### Issue 1: Missing Automatic Block Restoration on Scroll (CRITICAL)

**Location**: `src/clitic/widgets/conversation.py`

**Description**: The acceptance criterion "Scrolling up to pruned blocks triggers transparent reload from file" is not implemented. The `_restore_pruned_blocks()` method exists and works correctly when called explicitly, but there is no code that triggers it automatically when the user scrolls up toward pruned blocks.

**Expected Behavior**: When the user scrolls up and approaches content that has been pruned from memory, the system should automatically detect this and call `_restore_pruned_blocks()` to transparently reload the data from the session file.

**Actual Behavior**: Pruned blocks are only accessible via `get_block(block_id)` for programmatic access. Scroll-based navigation to pruned content does not trigger restoration.

**Code Reference**:
- Lines 472-506: `watch_scroll_y()` and `_update_auto_scroll_from_scroll_position()` only manage auto-scroll state, not block restoration
- No scroll position monitoring exists for proximity to pruned content

**Recommendation**: Implement scroll position monitoring that:
1. Detects when scroll position approaches the top of in-memory content
2. Checks if there are pruned blocks available (via `_pruned_blocks`)
3. Calls `_restore_pruned_blocks()` to load the next batch of pruned blocks
4. Maintains scroll position relative to content after restoration

**Suggested Implementation Location**: Add a method like `_check_and_restore_pruned_blocks()` called from `watch_scroll_y()` or `on_resize()`.

---

### Issue 2: Line Count Placeholder in Resume (MINOR)

**Location**: `src/clitic/widgets/conversation.py`, lines 795-798

**Description**: When resuming a session with pruned blocks, the line count is stored as 0 as a placeholder:

```python
conversation._pruned_blocks[block_info.sequence] = (block_info.block_id, 0)
```

This means if `_restore_pruned_blocks()` is called, the line count tracking will be incorrect until the block is actually rendered.

**Impact**: Minor - The line count is recalculated when the block is rendered in `_restore_pruned_blocks()` (line 364), so this only affects the placeholder value which isn't used elsewhere.

**Recommendation**: This is acceptable as-is since line count is recalculated on render, but adding a comment explaining why 0 is used would improve code clarity.

---

## What Works Well

### Pruning Logic
- Correctly identifies when pruning should occur (`_should_prune()`)
- Properly evicts oldest blocks first (FIFO)
- Maintains data structures consistently after pruning (`_blocks`, `_strips`, `_cumulative_heights`, `_total_lines`, `_block_index`)

### Data Integrity
- Pruned blocks remain in JSONL file
- All 30 tests verify data preservation
- `get_block()` correctly falls back to file lookup

### Edge Cases
- Persistence disabled: pruning disabled correctly
- Unlimited memory (max=0): all blocks stay in memory
- Concurrent loading: `_is_loading` flag prevents race conditions
- `clear()`: properly clears `_pruned_blocks` tracking
- Resume with more blocks than threshold: correctly prunes excess blocks

### Test Coverage
- 30 new pruning tests with excellent coverage
- Performance tests verify bounded memory usage
- Edge cases well covered (exact threshold, exceeding threshold, concurrent loading)

---

## Test Results Verification

All 395 tests pass, including:
- `tests/test_conversation_pruning.py` (30 tests)
- `tests/test_session_manager.py` (existing tests + new load methods)

---

## Recommendations

### Required for Approval

1. **Implement automatic block restoration on scroll**: The system must detect when the user scrolls toward pruned content and transparently restore blocks from the session file.

### Optional Improvements

2. Add a comment explaining the line count placeholder (line 798)
3. Consider adding a visual indicator when blocks are being loaded (optional acceptance criterion)
4. Add integration test for scroll-triggered restoration once implemented

---

## Summary

The core pruning mechanism is well-implemented with proper data integrity, tracking, and fallback retrieval. However, the acceptance criterion for automatic restoration triggered by scrolling is missing. This is a critical gap as users would expect transparent navigation to older content without manual intervention.

**Next Steps**: Implement scroll-triggered block restoration, then re-submit for functional review.