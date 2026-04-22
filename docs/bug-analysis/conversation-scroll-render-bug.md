# Bug Analysis: conversation-scroll-render-bug

**Bug ID:** conversation-scroll-render-bug
**Date:** 2026-04-22
**Status:** Fixed
**Severity:** S2 - Major (Core feature impaired)
**Priority:** P0 - Critical

---

## Summary

When scrolling up in the Conversation widget, lines from different blocks would visually merge/bleed into each other. The first line of markdown/code plugin content would appear to duplicate into the role header line. This bug was introduced in commit `dd5dcfe` when role labels for plugin content were moved to separate lines.

## Symptoms

**Reported Behavior:**
- When scrolling up (using mouse), lines from different blocks merge/bleed into each other
- First line of markdown/code plugin content duplicates into the role header line
- System lines sometimes merge into following blocks

**Expected Behavior:**
- Each line should display its correct content
- Role labels should remain on their own lines
- Plugin content should display correctly below role labels

**Impact:**
- Affects all users using the Conversation widget with plugin-rendered content
- Makes markdown and code blocks unreadable when scrolling
- Significant usability issue for core feature

## Root Cause Analysis

### Technique Used
5 Whys

### Analysis

1. **Why do lines bleed into each other when scrolling?**
   → The strips are not properly padded to the full width.

2. **Why are strips not properly padded?**
   → The `_create_role_label_strip` method creates strips using `Text.__rich_console__()` which doesn't produce properly padded lines.

3. **Why doesn't `__rich_console__()` produce padded lines?**
   → The method is designed for console output without width constraints, not for fixed-width strip rendering.

4. **Why was `__rich_console__()` used instead of `console.render_lines()`?**
   → The comment in the code said "render WITHOUT padding to full width", suggesting an intentional design choice that was incorrect.

5. **Why is proper padding important?**
   → Textual's `Strip` class expects strips to have consistent `cell_length` and `cell_count`. When `crop_extend` is called during rendering, strips with mismatched counts can cause visual artifacts.

### Root Cause

**Type:** Logic error - Incorrect rendering method used for role label strips

The `_create_role_label_strip` method used `Text.__rich_console__()` instead of `Console(width=width).render_lines()` to render role label text. This caused the created strips to have `cell_length=width` but `cell_count` equal to only the text length (e.g., 11 characters for "[Assistant]"), creating a mismatch. Other strips (from plugin content) were properly padded using `console.render_lines()`, causing inconsistency during rendering and scrolling.

## Proposed Fix

### Approach

Change `_create_role_label_strip` to use the same rendering pattern as `_renderable_to_strips`:
1. Create a `Console(width=width)` instance
2. Use `console.render_lines(label_text)` to render the text with proper padding
3. Convert the rendered lines to strips

This ensures all strips have consistent padding and cell counts.

### Code Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `src/clitic/widgets/conversation.py` | Modify | Updated `_create_role_label_strip` method to use `console.render_lines()` |

### Test Strategy

| Test Type | Framework | Description |
|-----------|-----------|-------------|
| Unit | pytest | Verify strips have consistent cell_length and cell_count |
| Unit | pytest | Verify role label strip is correctly created |
| Integration | pytest | Verify scrolling doesn't corrupt strip order |
| Integration | pytest | Verify multiple blocks display correctly |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance impact | Low | Low | `console.render_lines()` is efficient and already used for other content |
| Visual change | Low | Low | Role labels will display the same, just with proper padding |

## UI/UX Impact

**UI Changes Required:** No

This is a pure bug fix with no UI changes. The role labels will display exactly the same visually.

**UX Review Required:** No

## Implementation Notes

The fix was straightforward: replace the `__rich_console__()` approach with `console.render_lines()`:

```python
# Before (buggy):
console = Console()
render_iter = label_text.__rich_console__(console, console.options)
label_segments = []
for segment in render_iter:
    # ... collect segments
return Strip(label_segments, width)

# After (fixed):
console = Console(width=width)
lines = list(console.render_lines(label_text))
if not lines:
    return Strip.blank(width, getattr(self, "rich_style", None))
line = lines[0]
segments = []
for segment in line:
    if len(segment) == 2:
        segments.append(RichSegment(segment[0], segment[1], None))
    else:
        segments.append(segment)
return Strip(segments, width)
```

## Verification

### Before Fix

```python
# Role label strip created with cell_length=80 but cell_count=11
strip = Strip([Segment('[Assistant]', ...)], 80)
# cell_length=80, cell_count=11 - MISMATCH!
```

### After Fix

```python
# Role label strip created with consistent cell_length and cell_count
console = Console(width=80)
lines = console.render_lines(Text('[Assistant]', ...))
strip = Strip(segments, 80)
# cell_length=80, cell_count=80 - CONSISTENT!
```

### Regression Tests

- [x] All existing tests pass (814 passed, 1 xfailed)
- [x] New test added for this bug (test_strips_width_consistency)
- [x] Edge cases covered (test_scroll_up_with_plugin_content_preserves_strip_order)

## Lessons Learned

### Prevention Measures

| Measure | Type | Implementation |
|---------|------|----------------|
| Consistent strip creation | Process | All strip creation methods should use `Console(width=width).render_lines()` for consistent padding |
| Strip width tests | Test | Add tests to verify `cell_length` matches `cell_count` for all strips |
| Code review focus | Process | When changing strip creation methods, verify consistency with other methods |

## Timeline

| Date | Action | Actor |
|------|--------|-------|
| 2026-04-22 | Bug reported in TODO.md | User |
| 2026-04-22 | Analysis started | Agent |
| 2026-04-22 | Root cause identified | Agent |
| 2026-04-22 | Fix implemented | Agent |
| 2026-04-22 | Tests passed | Agent |