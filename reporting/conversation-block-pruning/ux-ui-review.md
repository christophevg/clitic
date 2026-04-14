# UI/UX Review: conversation-block-pruning

**Task:** Add memory-aware pruning with transparent retrieval (FR-007)
**Reviewer:** UI/UX Designer Agent
**Date:** 2026-04-14
**Status:** REJECTED

---

## 1. Executive Summary

The implementation provides the core memory-aware pruning mechanism but fails to meet critical UX acceptance criteria. The user experience is incomplete because scrolling to pruned content does not trigger automatic restoration, and there is no loading indicator during block retrieval.

---

## 2. Acceptance Criteria Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| Configurable `max_blocks_in_memory` threshold | IMPLEMENTED | Default 100, configurable, validates >= 0 |
| Pruning removes oldest from memory, preserves in file | IMPLEMENTED | `_prune_oldest_blocks()` correctly evicts |
| Pruning never deletes data | IMPLEMENTED | Blocks remain in JSONL file |
| Track which blocks are in memory vs persisted | IMPLEMENTED | `_pruned_blocks` dict tracks sequences |
| `get_block(block_id)` retrieves from memory or file | IMPLEMENTED | Falls back to file for pruned blocks |
| **Scrolling up to pruned blocks triggers transparent reload** | **NOT IMPLEMENTED** | Critical UX feature missing |
| **Loading indicator briefly shown during block retrieval** | **NOT IMPLEMENTED** | No visual feedback for loading |

---

## 3. Critical UX Issues

### 3.1 Missing: Scroll-Triggered Restoration (BLOCKER)

**Issue:** The `_restore_pruned_blocks()` method exists but is never called in response to user scrolling.

**User Impact:**
- User scrolls up to view older messages
- Pruned content is not visible (blank space or missing content)
- No automatic restoration occurs
- User cannot access historical content through natural scrolling

**Expected Behavior (from TODO.md):**
```
Scrolling up to pruned blocks triggers transparent reload from file
```

**Current Behavior:**
- `_restore_pruned_blocks()` is only called manually (not from any user action)
- No integration with `watch_scroll_y` or scroll position monitoring
- `render_line()` cannot render pruned content

**Recommended Fix:**
1. Add scroll position monitoring in `watch_scroll_y()`
2. Detect when user scrolls near pruned block boundaries
3. Trigger `_restore_pruned_blocks()` with appropriate count
4. Consider loading a "window" of blocks (e.g., 5 blocks) for smooth scrolling

**Code Location:** `/Users/xtof/Workspace/agentic/clitic/src/clitic/widgets/conversation.py` lines 472-481 (`watch_scroll_y`)

---

### 3.2 Missing: Loading Indicator (BLOCKER)

**Issue:** No visual feedback when blocks are being loaded from file.

**User Impact:**
- User scrolls up, nothing appears to happen
- No indication that content is loading
- Perceived as unresponsive or broken

**Expected Behavior (from TODO.md):**
```
Loading indicator briefly shown during block retrieval
```

**Current Behavior:**
- `_is_loading` flag exists but is not exposed to the UI
- No visual indication during file I/O
- No skeleton loading or spinner

**Recommended Fix:**
1. Expose `is_loading` as a reactive property
2. Add CSS class `loading` when blocks are being restored
3. Consider brief "Loading historical messages..." indicator
4. For instant loads (< 100ms), consider a subtle flash instead

**Code Location:** `/Users/xtof/Workspace/agentic/clitic/src/clitic/widgets/conversation.py` lines 179, 333-335

---

## 4. Secondary UX Issues

### 4.1 Scroll Position Not Adjusted During Pruning

**Issue:** When pruning occurs, the scroll position is not clamped or adjusted.

**Scenario:**
1. User has scrolled up to view message #50 of 100
2. New messages arrive, triggering pruning
3. Messages #1-20 are pruned
4. The scroll position (pointing to what was line X) now points to different content

**User Impact:**
- Content appears to "jump" unexpectedly
- User loses their reading position
- Disorienting experience

**Recommended Fix:**
After pruning, clamp scroll position:
```python
def _prune_oldest_blocks(self) -> None:
    # ... existing pruning code ...

    # Clamp scroll position to valid range
    if self.scroll_y > self.max_scroll_y:
        self.scroll_to(y=self.max_scroll_y, animate=False)
```

**Code Location:** `/Users/xtof/Workspace/agentic/clitic/src/clitic/widgets/conversation.py` lines 251-300

---

### 4.2 `get_block_id_at_line()` Returns None for Pruned Blocks

**Issue:** This method returns `None` when the line corresponds to pruned content.

**User Impact:**
- Block navigation (Alt+Up/Down) would fail silently
- Cannot show block information for pruned content
- Edge case: If user tries to select/copy while viewing pruned content

**Recommendation:**
Document this behavior or return a sentinel value indicating "pruned" status:
```python
def get_block_id_at_line(self, line: int) -> str | None:
    """Returns block ID or None if line is in pruned region."""
```

**Code Location:** `/Users/xtof/Workspace/agentic/clitic/src/clitic/widgets/conversation.py` lines 700-718

---

### 4.3 No User-Visible Pruning Statistics

**Issue:** The widget tracks pruning internally but doesn't expose useful stats to the user.

**Missing:**
- Indicator showing "X older messages available" when scrolled to top
- Status bar showing total vs visible message count
- Way to manually trigger loading all content

**Recommendation:**
Add visual indicator when user is at the scroll boundary with pruned content:
```
+------------------------------------------------------------------+
|  ^ 5 older messages available - scroll up to load                |
+------------------------------------------------------------------+
```

---

## 5. Performance Assessment

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pruning overhead | < 10ms | Fast (pop operations) | APPROVED |
| Memory bounded | Bounded at threshold | Yes | APPROVED |
| Restore speed | < 100ms for typical load | Fast | APPROVED |
| Concurrent loading prevented | Yes | `_is_loading` flag | APPROVED |

**Performance Notes:**
- The implementation efficiently removes strips from the beginning of the list
- Memory usage stays bounded at the configured threshold
- The `_is_loading` flag prevents race conditions
- Performance tests in `test_conversation_pruning.py` verify timing

---

## 6. Edge Cases Analysis

### 6.1 User Scrolls Up During Active Pruning

**Scenario:** New messages arrive while user is viewing historical content.

**Current Behavior:**
- Pruning happens immediately
- User's scroll position may become invalid
- No warning that content is being removed

**Recommended Fix:**
- Pause pruning when user is scrolled up (auto_scroll is False)
- Resume pruning when user scrolls back to bottom
- Alternative: Increase threshold temporarily when user is viewing older content

---

### 6.2 Rapid Scrolling Through Pruned Region

**Scenario:** User holds Page Up to scroll rapidly through content.

**Risk:**
- Multiple restore operations triggered
- Could cause visual glitches

**Current Mitigation:**
- `_is_loading` flag prevents concurrent loads
- Second restore request returns False

**Recommendation:**
- Debounce restore triggers
- Load a "window" of blocks (e.g., 10) to reduce restore frequency

---

### 6.3 Resume Session with Large History

**Scenario:** User resumes a session with 1000 messages, max_blocks_in_memory=100.

**Current Behavior:**
- Only newest 100 blocks loaded to memory
- Older 900 blocks marked as pruned
- No indication that older content is available

**Recommendation:**
- Show "900 older messages available" indicator on first display
- Consider progressive loading (load more as user scrolls up)
- Or load last N blocks + first M blocks for context

---

## 7. Manual Testing Scenarios

The following scenarios should be tested manually after the blockers are fixed:

### 7.1 Basic Pruning Visibility

1. Create conversation with `max_blocks_in_memory=5`
2. Append 10 messages
3. Verify first 5 messages are pruned (check `pruned_block_count`)
4. Scroll to bottom - should see messages 5-9
5. **EXPECTED:** Scroll up should trigger loading of older messages

### 7.2 Scroll-Triggered Restoration

1. Create conversation with `max_blocks_in_memory=5`, persistence enabled
2. Append 15 messages
3. Scroll to top of visible content
4. **EXPECTED:** Loading indicator appears briefly
5. **EXPECTED:** Messages 0-4 become visible
6. **EXPECTED:** `pruned_block_count` decreases

### 7.3 Auto-Scroll Interaction

1. Create conversation with auto_scroll enabled
2. Append messages to trigger pruning
3. Verify auto-scroll stays at bottom
4. Scroll up to pause auto-scroll
5. New message arrives
6. **EXPECTED:** New message appears but scroll stays in place
7. **EXPECTED:** Pruning may be paused when scrolled up

### 7.4 Resume and Scroll

1. Create session with 20 messages, `max_blocks_in_memory=10`
2. Close session
3. Resume session
4. Scroll to top
5. **EXPECTED:** Older messages load transparently

---

## 8. Accessibility Considerations

### 8.1 Screen Reader Announcement

**Missing:** No announcement when older messages are loaded.

**Recommendation:**
When blocks are restored, announce:
```
"Loaded 5 older messages"
```

### 8.2 Keyboard Navigation to Pruned Content

**Missing:** Alt+Up navigation doesn't trigger loading.

**Recommendation:**
When `conversation-block-navigation` is implemented, ensure:
- Navigating to a pruned block triggers restoration
- Loading state is announced
- Focus moves to the newly loaded block

---

## 9. API Dependencies

This feature requires coordination with:

| Feature | Dependency | Status |
|---------|------------|--------|
| `conversation-block-navigation` | Alt+Up/Down navigation triggers restore | Not yet implemented |
| Loading indicator widget | `animation-loading` (Phase 9) | Not yet implemented |
| Session persistence | `SessionManager.load_blocks_by_sequence_range` | IMPLEMENTED |

---

## 10. Recommendations

### 10.1 Required Changes (for approval)

1. **Implement scroll-triggered restoration**
   - Monitor scroll position in `watch_scroll_y`
   - Detect when user scrolls near top boundary
   - Trigger `_restore_pruned_blocks()` proactively

2. **Implement loading indicator**
   - Add `loading` CSS class
   - Show brief visual feedback during file I/O
   - For instant loads, use subtle flash

3. **Handle scroll position during pruning**
   - Clamp scroll_y to valid range after pruning
   - Consider offset adjustment for smooth experience

### 10.2 Suggested Enhancements

1. **Pause pruning when scrolled up**
   - Only prune when auto_scroll is True
   - Prevents content displacement during viewing

2. **Progressive loading**
   - Load blocks in batches (5-10 at a time)
   - Reduce restore frequency during rapid scrolling

3. **User-visible statistics**
   - "X older messages available" indicator
   - Status bar integration

---

## 11. Conclusion

The implementation provides a solid foundation for memory-aware pruning but is missing two critical user-facing features required by the acceptance criteria:

1. **Scroll-triggered transparent restoration** - Essential for natural user workflow
2. **Loading indicator** - Essential for user feedback

Without these features, the user experience is incomplete. Users cannot access historical content through normal scrolling, and have no feedback when content is being loaded.

**Recommendation:** Implement the required changes before marking the task complete.

---

## 12. File References

| File | Path | Lines |
|------|------|-------|
| Conversation widget | `/Users/xtof/Workspace/agentic/clitic/src/clitic/widgets/conversation.py` | 1-823 |
| Pruning tests | `/Users/xtof/Workspace/agentic/clitic/tests/test_conversation_pruning.py` | 1-597 |
| Task definition | `/Users/xtof/Workspace/agentic/clitic/TODO.md` | 95-107 |
| UX analysis | `/Users/xtof/Workspace/agentic/clitic/analysis/ui-ux.md` | 890-894 |