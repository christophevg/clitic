# UX Analysis: Conversation Resize/Scroll Integration Tests

**Task:** test-conversation-resize-scroll
**Priority:** 8/10 (Critical)
**Date:** 2026-04-18
**Analyst:** UI/UX Designer Agent

---

## 1. Executive Summary

This document provides UX-focused analysis for testing the Conversation widget's resize and scroll behavior. The key user experience concerns are:

1. **Predictable scroll behavior** - Users expect their scroll position to be maintained or updated logically during resize
2. **Clear visual feedback** - The `paused` CSS class must correctly indicate auto-scroll state
3. **Smooth transitions** - Resize and scroll state changes should feel natural, not jarring
4. **Accessibility** - State changes should be communicated to all users, including those using assistive technology

---

## 2. User Interaction Scenarios

### 2.1 Primary User Flow: Auto-Scroll State Management

```
[User Viewing Conversation]
          |
          v
    +-----+-----+
    |           |
    v           v
[At Bottom]  [Scrolled Up]
    |           |
    |           v
    |    [Auto-Scroll Paused]
    |    [Visual Indicator: Border]
    |           |
    v           v
[New Content]  [User Scrolls Down]
    |                  |
    v                  v
[Auto-Scroll]    [Resume Auto-Scroll]
[Scrolls to End] [Indicator Removed]
```

**Test Scenarios:**

| Scenario | Initial State | User Action | Expected State | Visual Feedback |
|----------|--------------|-------------|----------------|-----------------|
| US-001 | At bottom | New content arrives | Scroll to bottom, auto_scroll=True | No "paused" class |
| US-002 | At bottom | User scrolls up | auto_scroll=False | "paused" class added |
| US-003 | Paused (scrolled up) | User scrolls to bottom | auto_scroll=True | "paused" class removed |
| US-004 | Paused | New content arrives | Stay in place, no scroll | "paused" class remains |
| US-005 | Content fits entirely | Any scroll action | auto_scroll=True (always) | No "paused" class |

### 2.2 Resize Flow

```
[User Viewing Content]
          |
          v
[Terminal Resize Detected]
          |
          v
[Content Re-rendered at New Width]
          |
    +-----+-----+
    |           |
    v           v
[Was at Bottom]  [Was Scrolled Up]
    |                  |
    v                  v
[Stay at Bottom]  [Adjust Position]
    |                  |
    v                  v
[Update auto_scroll]  [Keep auto_scroll=False]
```

**Test Scenarios:**

| Scenario | Initial State | Resize Type | Expected Behavior |
|----------|--------------|-------------|-------------------|
| RS-001 | At bottom, auto_scroll=True | Narrower | Stay at bottom, re-render, auto_scroll=True |
| RS-002 | At bottom, auto_scroll=True | Wider | Stay at bottom, re-render, auto_scroll=True |
| RS-003 | Scrolled up, auto_scroll=False | Narrower | Maintain relative position, auto_scroll=False |
| RS-004 | Scrolled up, auto_scroll=False | Wider | Maintain relative position, auto_scroll=False |
| RS-005 | Content fits entirely | Any resize | auto_scroll=True, no class change |

---

## 3. Edge Cases Affecting User Experience

### 3.1 Scroll Position Edge Cases

| Edge Case | Description | UX Concern | Test Priority |
|-----------|-------------|------------|---------------|
| EC-001 | Content height exactly equals viewport height | No scrollbar, auto_scroll should be True | High |
| EC-002 | Content height one line less than viewport | Scrolled to "bottom" but max_scroll_y=0 | High |
| EC-003 | Rapid consecutive resizes | Avoid thrashing re-renders | Medium |
| EC-004 | Resize during content append | Race condition between scroll and resize | High |
| EC-005 | Scroll position at max_scroll_y - 1 | One line from bottom, should auto_scroll=True | High |
| EC-006 | Scroll position at max_scroll_y - 2 | Two lines from bottom, should auto_scroll=False | High |

### 3.2 Content Edge Cases

| Edge Case | Description | UX Concern | Test Priority |
|-----------|-------------|------------|---------------|
| EC-010 | Empty conversation | No content to scroll | Medium |
| EC-011 | Single line content | Minimal scroll behavior | Medium |
| EC-012 | Content with line wrapping changes | Width change affects line count | High |
| EC-013 | Very long single line | Width change dramatically changes height | High |
| EC-014 | Pruned blocks loaded during scroll | Loading indicator interaction | Medium |

### 3.3 Timing Edge Cases

| Edge Case | Description | UX Concern | Test Priority |
|-----------|-------------|------------|---------------|
| EC-020 | Resize during auto_scroll watch | Scroll event during resize | Medium |
| EC-021 | Content append during scroll watch | New content while user scrolling | High |
| EC-022 | Multiple appends during resize | Batch updates | Medium |

---

## 4. Visual Feedback Verification

### 4.1 CSS Class State Matrix

| State | CSS Class | Visual Effect | When Applied | When Removed |
|-------|-----------|---------------|--------------|--------------|
| Auto-scroll active | None | Default appearance | auto_scroll=True | N/A |
| Auto-scroll paused | `paused` | Warning border-top | auto_scroll=False | auto_scroll=True |
| Loading blocks | `loading` | Opacity 0.7 | _is_loading=True | _is_loading=False |

### 4.2 Visual Indicator Test Cases

| Test ID | Description | Verification Method |
|---------|-------------|---------------------|
| VF-001 | `paused` class appears on scroll up | Check `classes` contains "paused" |
| VF-002 | `paused` class disappears on scroll to bottom | Check `classes` does not contain "paused" |
| VF-003 | `paused` class absent when content fits | Check `classes` does not contain "paused" |
| VF-004 | `paused` class persists during resize (scrolled up) | Verify class remains after resize |
| VF-005 | `paused` class not added during resize (at bottom) | Verify class not added after resize |
| VF-006 | `loading` class appears during block restoration | Check `classes` contains "loading" |
| VF-007 | `loading` class removed after restoration complete | Check `classes` does not contain "loading" |

### 4.3 CSS Styling Verification

The CSS classes should provide clear visual distinction:

```css
/* From Conversation.DEFAULT_CSS */
Conversation {
  height: 1fr;
  padding: 1;
  background: $surface;
}

Conversation.paused {
  border-top: thick $warning;  /* Clear visual indicator */
}

Conversation.loading {
  opacity: 0.7;  /* Dimming during load */
}
```

**UX Assessment:**
- `paused` border-top is visible and uses warning color (good)
- `loading` opacity reduction provides subtle feedback (good)
- No text indicator - consider for accessibility (see Section 6)

---

## 5. Integration Test Recommendations

### 5.1 Core Integration Tests

**Test Class: `TestConversationScrollResizeIntegration`**

```python
# Recommended test methods:

async def test_scroll_up_sets_auto_scroll_false():
    """Scrolling up from bottom should set auto_scroll=False."""
    # Setup: conversation with multiple blocks
    # Action: scroll up from bottom
    # Assert: auto_scroll == False, "paused" in classes

async def test_scroll_to_bottom_sets_auto_scroll_true():
    """Scrolling to bottom should set auto_scroll=True."""
    # Setup: conversation with auto_scroll=False
    # Action: scroll to bottom
    # Assert: auto_scroll == True, "paused" not in classes

async def test_resize_at_bottom_maintains_auto_scroll():
    """Resize while at bottom should keep auto_scroll=True."""
    # Setup: conversation at bottom, auto_scroll=True
    # Action: trigger resize
    # Assert: auto_scroll still True

async def test_resize_scrolled_up_keeps_paused():
    """Resize while scrolled up should keep auto_scroll=False."""
    # Setup: conversation scrolled up, auto_scroll=False
    # Action: trigger resize
    # Assert: auto_scroll still False, "paused" in classes

async def test_content_fits_always_auto_scroll():
    """When content fits viewport, auto_scroll should always be True."""
    # Setup: conversation with content smaller than viewport
    # Action: various scroll attempts
    # Assert: auto_scroll always True
```

### 5.2 Edge Case Tests

```python
async def test_near_bottom_threshold():
    """Scrolling to max_scroll_y - 1 should trigger auto_scroll."""
    # Setup: conversation with scrollable content
    # Action: scroll to max_scroll_y - 1
    # Assert: auto_scroll == True

async def test_beyond_threshold_no_auto_scroll():
    """Scrolling to max_scroll_y - 2 should not trigger auto_scroll."""
    # Setup: conversation with scrollable content
    # Action: scroll to max_scroll_y - 2
    # Assert: auto_scroll == False

async def test_resize_recalculates_threshold():
    """After resize, threshold should be recalculated."""
    # Setup: conversation at scroll position
    # Action: resize (changes line wrapping)
    # Assert: _update_auto_scroll_from_scroll_position called
```

### 5.3 Visual Feedback Tests

```python
async def test_paused_class_add_removes():
    """paused class should be added/removed based on auto_scroll."""
    # Test complete cycle: add class -> remove class -> verify state

async def test_loading_class_during_restore():
    """loading class should appear during block restoration."""
    # Setup: conversation with persistence and pruning
    # Action: scroll near top to trigger restoration
    # Assert: "loading" in classes during restoration
```

---

## 6. Accessibility Considerations

### 6.1 Current State

The current implementation uses CSS classes for visual feedback:

| Accessibility Aspect | Current Status | Gap |
|----------------------|---------------|-----|
| Visual indicator | Border-top on paused | Good for sighted users |
| Screen reader support | None | No announcements |
| High contrast | Uses `$warning` color | May not meet WCAG AA |
| Reduced motion | CSS only (opacity) | Good |

### 6.2 Accessibility Test Cases

| Test ID | Description | WCAG Criterion | Priority |
|---------|-------------|----------------|----------|
| AC-001 | Border color contrast for `paused` class | 1.4.11 Non-text Contrast | High |
| AC-002 | Opacity change visibility | 1.4.3 Contrast (Minimum) | Medium |
| AC-003 | State change announcement | 4.1.3 Status Messages | Future |

### 6.3 Recommendations for Future

1. **Screen Reader Announcements**
   - When `auto_scroll` changes, announce to screen readers
   - Example: "Auto-scroll paused" / "Auto-scroll resumed"

2. **Text Alternative**
   - Consider adding a text indicator alongside border
   - Could be a status bar message: "Following: OFF" / "Following: ON"

3. **Keyboard Navigation**
   - Ensure scroll actions work with keyboard
   - Document shortcuts in help overlay

---

## 7. Test Organization Recommendations

### 7.1 File Structure

```
tests/
  test_conversation_scroll_resize.py   # New file for integration tests
    |
    +-- TestScrollStateManagement       # Core scroll state tests
    +-- TestResizeBehavior              # Resize-specific tests
    +-- TestVisualFeedback              # CSS class tests
    +-- TestEdgeCases                   # Edge case tests
    +-- TestAccessibility               # Accessibility-related tests
```

### 7.2 Test Dependencies

| Test Class | Dependencies | Fixtures Needed |
|------------|--------------|-----------------|
| TestScrollStateManagement | Conversation, App context | `conversation_factory`, `mounted_conversation` |
| TestResizeBehavior | Conversation, Resize event | `conversation_factory`, mock Resize event |
| TestVisualFeedback | Conversation, CSS classes | `conversation` |
| TestEdgeCases | Various | Multiple fixtures |
| TestAccessibility | High contrast mode testing | Custom fixtures |

---

## 8. Acceptance Criteria Mapping

From TODO.md:

| Acceptance Criterion | Test Coverage Needed | Priority |
|-----------------------|---------------------|----------|
| Integration tests for resize -> scroll position -> auto_scroll -> CSS class cycle | Test class `TestConversationScrollResizeIntegration` | High |
| Tests for `_update_auto_scroll_from_scroll_position` | Unit tests for each branch | High |

**Expanded Acceptance Criteria:**

- [ ] **AC-1:** Scrolling up from bottom sets `auto_scroll=False` and adds `paused` class
- [ ] **AC-2:** Scrolling to bottom sets `auto_scroll=True` and removes `paused` class
- [ ] **AC-3:** Resize at bottom maintains `auto_scroll=True` and no `paused` class
- [ ] **AC-4:** Resize while scrolled up maintains `auto_scroll=False` and `paused` class
- [ ] **AC-5:** Content that fits viewport always has `auto_scroll=True`
- [ ] **AC-6:** Near-bottom threshold (max_scroll_y - 1) triggers `auto_scroll=True`
- [ ] **AC-7:** `_update_auto_scroll_from_scroll_position` handles max_scroll_y == 0
- [ ] **AC-8:** `_update_auto_scroll_from_scroll_position` handles max_scroll_y > 0, scroll_y near bottom
- [ ] **AC-9:** `_update_auto_scroll_from_scroll_position` handles scroll_y far from bottom

---

## 9. Fixtures to Create

Based on the analysis, these fixtures would be helpful:

```python
@pytest.fixture
async def scrollable_conversation():
    """Conversation with enough content to scroll."""
    # Creates conversation with 50+ blocks for scroll testing

@pytest.fixture
async def conversation_at_bottom():
    """Conversation scrolled to bottom."""
    # Creates conversation and scrolls to end

@pytest.fixture
async def conversation_scrolled_up():
    """Conversation scrolled up from bottom."""
    # Creates conversation and scrolls up

@pytest.fixture
def resize_event_factory():
    """Factory for creating Resize events."""
    # Creates mock Resize events for testing
```

---

## 10. Summary

The resize/scroll integration tests should cover:

1. **Core functionality** - The complete cycle of scroll state changes
2. **Visual feedback** - CSS classes correctly applied/removed
3. **Edge cases** - Boundary conditions that affect user experience
4. **Accessibility** - Ensure feedback is perceivable

Key UX concerns:
- Predictable behavior during resize
- Clear visual feedback for auto-scroll state
- Smooth transitions between states
- Support for users with accessibility needs

The existing `_update_auto_scroll_from_scroll_position` method is the critical integration point that needs thorough testing to ensure the UX is consistent and predictable.