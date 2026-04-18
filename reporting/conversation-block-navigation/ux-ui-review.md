# UX/UI Review: conversation-block-navigation

**Task:** Add block navigation and selection to the Conversation widget
**Date:** 2026-04-18
**Reviewer:** UI/UX Designer Agent

---

## 1. Executive Summary

This review analyzes the UX design requirements for adding block navigation and selection to the Conversation widget. The feature enables users to navigate between message blocks using `Alt+Up`/`Alt+Down` keyboard shortcuts, with visual feedback and support for loading pruned blocks from disk.

**Key Recommendations:**
1. Use subtle background highlight (not border) for selected blocks to maintain visual hierarchy
2. Implement smooth auto-scroll to center selected block in viewport
3. Support both keyboard navigation and click-to-select interactions
4. Provide configurable wrap behavior with audio/visual feedback at boundaries
5. Expose block navigation state through reactive properties for accessibility

---

## 2. Visual Design Analysis

### 2.1 Selected Block Visual Treatment

**Question:** What is the best visual treatment for selected blocks?

**Recommendation:** Use a subtle background color shift combined with a left border accent, NOT a full border change.

**Rationale:**
- The Conversation already uses role-based colors (blue=user, green=assistant, yellow=system, magenta=tool)
- Adding a border would conflict with the existing left border that indicates role
- A background highlight is more discoverable than a border change in a scrollable context
- Subtle background preserves the role color hierarchy while adding selection indication

**CSS Implementation:**

```css
/* Selected block styling - add to base.tcss */
Conversation {
  /* ... existing styles ... */
}

/* Selected block: subtle background highlight */
Conversation .selected-block {
  background: $accent 10%;
  border-left: thick $accent;  /* Accent color left border */
}

/* Role colors are preserved with selection overlay */
Conversation .selected-block.user {
  background: $accent 15%;  /* Slightly more visible for user */
}

Conversation .selected-block.assistant {
  background: $success 15%;
  border-left: thick $success;
}

Conversation .selected-block.system {
  background: $warning 15%;
  border-left: thick $warning;
}

Conversation .selected-block.tool {
  background: $info 15%;
  border-left: thick $info;
}
```

**Visual Mockup:**

```
Normal blocks:
+------------------------------------------------------------------+
| [You] Hello, how can I help you today?                           |
+------------------------------------------------------------------+
| [Assistant] I can assist you with various tasks...               |
| Would you like to see the documentation?                         |
+------------------------------------------------------------------+

Selected block (with Alt+Up/Down):
+------------------------------------------------------------------+
| [You] Hello, how can I help you today?                           |  <- Normal
+------------------------------------------------------------------+
|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓|
| [Assistant] I can assist you with various tasks...               |  <- Selected
| Would you like to see the documentation?                         |
|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓|
+------------------------------------------------------------------+
```

### 2.2 Integration with Role Styling

**Recommendation:** Selection should enhance, not override, the role-based visual hierarchy.

**Implementation:**
- Add `selected` CSS class to the block container
- Selection adds a subtle tint (10-15% opacity) of the accent color over the role color
- Border accent color matches the role color (not accent) to maintain visual consistency

### 2.3 Selection State Indicators

**Additional Visual Feedback:**

| Indicator | Implementation | Purpose |
|-----------|----------------|---------|
| Block number in status | Status bar: "Block 3/15" | Shows position in conversation |
| Scroll position indicator | Thin scrollbar highlight | Shows selected block position |
| Focus ring on Conversation | Border when focused | Shows keyboard navigation is active |

---

## 3. Navigation Feedback Analysis

### 3.1 Wrap-Around Behavior

**Question:** Should there be visual/audio feedback when wrapping?

**Recommendation:** Implement wrap with visual bell and optional audio.

**Behavior Specification:**

```python
# Configuration
wrap_navigation: reactive[bool] = reactive(True)
navigation_bell: reactive[bool] = reactive(True)

# At top boundary (first block)
async def action_nav_up(self) -> None:
    if self._selected_index == 0:
        if self.wrap_navigation:
            # Jump to last block
            self._selected_index = len(self._blocks) - 1
            if self.navigation_bell:
                self.app.bell()  # Visual bell
        else:
            # Stay at first, provide feedback
            self.app.bell()  # Indicate boundary
            return
    else:
        self._selected_index -= 1
    await self._scroll_to_selected()
```

**Visual Feedback:**
- `app.bell()` triggers Textual's visual bell (screen flash)
- Optional: Add a transient toast "Wrapped to last block"
- Selected block highlights briefly (100ms pulse)

### 3.2 Pruned Block Loading

**Question:** What feedback when loading pruned blocks?

**Recommendation:** Use existing loading indicator with context.

**Current Implementation:** The Conversation already has:
- `Conversation.loading` CSS class (opacity: 0.7)
- `_is_loading` flag to prevent concurrent loading

**Enhancement:** Add loading context message:

```python
# When triggering pruned block load
self.add_class("loading")
self._loading_context = f"Loading block {target_sequence}..."
try:
    await self._restore_pruned_blocks(target_sequence)
finally:
    self.remove_class("loading")
    self._loading_context = None
```

**CSS Enhancement:**

```css
Conversation.loading {
  opacity: 0.7;
}

Conversation.loading::after {
  content: "Loading...";
  position: absolute;
  top: 1;
  right: 1;
  background: $warning;
  color: $background;
  padding: 0 1;
}
```

### 3.3 Boundary Reached (No Wrap)

**Question:** What feedback at boundaries when wrap is disabled?

**Recommendation:** Visual bell + brief status message.

**Behavior:**
1. `Alt+Up` at first block: Visual bell, status shows "Already at first block"
2. `Alt+Down` at last block: Visual bell, status shows "Already at last block"

---

## 4. Interaction Model Analysis

### 4.1 Auto-Scroll to Selected Block

**Question:** Should navigation auto-scroll to center the selected block?

**Recommendation:** Yes, use smooth scroll-to-center behavior.

**Implementation:**

```python
async def _scroll_to_selected(self) -> None:
    """Scroll to center the selected block in viewport."""
    if self._selected_index < 0 or self._selected_index >= len(self._blocks):
        return

    block = self._blocks[self._selected_index]

    # Get the line range for this block
    block_start_line = 0
    for i in range(self._selected_index):
        block_start_line += self._blocks[i].line_count
    block_end_line = block_start_line + block.line_count

    # Calculate center position
    viewport_height = self.size.height
    block_height = block.line_count
    center_line = block_start_line + (block_height // 2)

    # Scroll to center
    target_y = max(0, center_line - (viewport_height // 2))
    self.scroll_to(y=target_y, animate=True, duration=200)
```

**Animation Timing:**
- Duration: 200ms (consistent with Textual's scroll animations)
- Easing: ease-out (smooth deceleration)

### 4.2 Scroll Position Preservation

**Question:** Should scroll position be preserved relative to selected block?

**Recommendation:** No, always center the selected block for visibility.

**Rationale:**
- Centering ensures the full block is visible
- Prevents partial visibility that could confuse users
- Consistent with navigation patterns in other TUIs (less, tmux)

### 4.3 Click-to-Select Interaction

**Question:** Should clicking on a block select it?

**Recommendation:** Yes, clicking should select the clicked block.

**Implementation:**

```python
def on_click(self, event: Click) -> None:
    """Handle click to select block."""
    # Convert click coordinates to line number
    line = self._y_to_line(event.y)

    # Find block at this line
    block_id = self.get_block_id_at_line(line)
    if block_id is not None:
        self._selected_index = self._block_index.get(block_id, -1)
        if self._selected_index >= 0:
            self._update_selected_visual()
            # Don't scroll on click - user already positioned
```

**Note:** Click should NOT trigger scroll - the user has already positioned their view.

---

## 5. State Management Analysis

### 5.1 Initial State

**Question:** Should `selected_block` return None initially?

**Recommendation:** Yes, no block should be selected by default.

**Rationale:**
- Avoids visual clutter on initial view
- Users may not need navigation in small conversations
- Selection is an intentional action (Alt+Up/Down or click)

**Implementation:**

```python
class Conversation(ScrollView):
    # Reactive property for selection
    selected_block: reactive[str | None] = reactive(None)

    def __init__(self, ...):
        ...
        self._selected_index: int = -1  # -1 means no selection
```

### 5.2 Persistence Across Sessions

**Question:** Should selection persist across session persistence?

**Recommendation:** No, selection should not persist.

**Rationale:**
- Selection is transient navigation state, not conversation content
- Pruned blocks may not be immediately available on restore
- Users expect to start fresh when resuming a session

**Implementation:**

```python
def clear(self) -> None:
    """Clear all content blocks from the conversation."""
    self._blocks.clear()
    ...
    self._selected_index = -1  # Reset selection
    self.selected_block = None
```

### 5.3 Clear on Content Clear

**Question:** Should selection clear when content is cleared?

**Recommendation:** Yes, reset to no selection.

**Implementation:** Already shown in `clear()` method above.

---

## 6. Accessibility Analysis

### 6.1 Screen Reader Announcements

**Question:** How should screen readers announce block navigation?

**Recommendation:** Use ARIA live regions to announce block role and content preview.

**Implementation:**

```python
def _announce_selected_block(self) -> None:
    """Announce selected block for screen readers."""
    if self._selected_index < 0 or self._selected_index >= len(self._blocks):
        return

    block = self._blocks[self._selected_index]
    # Get first 100 chars of content for preview
    content_preview = block.info.content[:100]
    if len(block.info.content) > 100:
        content_preview += "..."

    # Announce: "Block 3 of 15, user message: Hello, how can I..."
    position = f"Block {self._selected_index + 1} of {len(self._blocks)}"
    role_label = block.info.role.capitalize()
    message = f"{position}, {role_label} message: {content_preview}"

    # Use Textual's screen reader support
    self.screen._screen_reader_update(message)
```

### 6.2 Keyboard-Only Navigation

**Recommendation:** Ensure all navigation is keyboard-accessible.

**Bindings:**

```python
BINDINGS = [
    # ... existing bindings ...
    ("alt+up", "nav_prev_block", "Previous block"),
    ("alt+down", "nav_next_block", "Next block"),
    ("escape", "deselect_block", "Deselect block"),
]
```

### 6.3 Focus Management

**Question:** How should focus interact with selection?

**Recommendation:** Selection and focus are independent but related.

**Behavior:**
- `Alt+Up/Down` works when Conversation has focus OR when it's the active scrollable widget
- `Escape` clears selection (deselects)
- Tab/Shift+Tab navigates between InputBar and Conversation (focus), not between blocks
- Block navigation is always within the Conversation widget

---

## 7. Key Bindings Analysis

### 7.1 Binding Names and Descriptions

**Recommended Bindings:**

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Alt+Up` | `nav_prev_block` | "Previous message" |
| `Alt+Down` | `nav_next_block` | "Next message" |
| `Escape` | `deselect_block` | "Clear selection" |
| `Home` | `scroll_home` | "To start" (existing) |
| `End` | `scroll_end` | "To end" (existing) |

**Alternative Shortcuts (for terminals where Alt is problematic):**

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Up` | `nav_prev_block` | "Previous message" |
| `Ctrl+Down` | `nav_next_block` | "Next message" |

**Rationale:**
- `Alt+Up/Down` is standard for "element navigation" in GUI applications
- `Escape` to deselect is consistent with cancel patterns
- Alternative `Ctrl` shortcuts for terminals where `Alt` key sends escape sequences

### 7.2 Binding Conflicts

**Analysis of Potential Conflicts:**

| Existing Binding | Conflict Risk | Resolution |
|-----------------|---------------|------------|
| `Up` / `Down` | None - scroll vs. navigate | Different scope (Alt modifier) |
| `Home` / `End` | None - scroll | Different scope (navigate vs. scroll) |
| `Escape` | Potential - could mean "exit input" | Context-aware: clear selection if any, otherwise pass through |

**Implementation:**

```python
def action_deselect_block(self) -> None:
    """Deselect the current block, or pass through if no selection."""
    if self._selected_index >= 0:
        self._selected_index = -1
        self.selected_block = None
        self._update_selected_visual()
    else:
        # No selection - let the app handle Escape (e.g., exit)
        pass
```

---

## 8. Reactive Properties

### 8.1 Selection State Properties

**Recommended Reactive Properties:**

```python
class Conversation(ScrollView):
    # Primary selection property
    selected_block: reactive[str | None] = reactive(None)

    # Configuration properties
    wrap_navigation: reactive[bool] = reactive(True)
    navigation_bell: reactive[bool] = reactive(True)

    # Computed properties (read-only)
    @property
    def selected_block_index(self) -> int | None:
        """0-indexed position of selected block, or None."""
        return self._selected_index if self._selected_index >= 0 else None

    @property
    def selected_block_info(self) -> BlockInfo | None:
        """BlockInfo for selected block, or None."""
        if self._selected_index < 0 or self._selected_index >= len(self._blocks):
            return None
        return self._blocks[self._selected_index].info
```

### 8.2 Watch Callbacks

**Implementation:**

```python
def watch_selected_block(self, old: str | None, new: str | None) -> None:
    """React to selection changes."""
    if new is None:
        # Clear selection
        self._selected_index = -1
        self._update_selected_visual()
    else:
        # Find block by ID
        if new in self._block_index:
            self._selected_index = self._block_index[new]
            self._update_selected_visual()
            self.call_after_refresh(self._scroll_to_selected)
```

---

## 9. Pruned Block Navigation

### 9.1 Navigation to Pruned Blocks

**Question:** What happens when navigating to a pruned block?

**Recommendation:** Trigger transparent load, then scroll to block.

**Behavior Flow:**

```
User presses Alt+Up
      |
      v
Check if previous block is pruned
      |
      +-- Yes --> Check if already loading
      |                |
      |                +-- Yes --> Ignore (debounce)
      |                |
      |                +-- No --> Show loading indicator
      |                            |
      |                            v
      |                      Load block from file
      |                            |
      |                            v
      |                      Restore to memory
      |                            |
      |                            v
      |                      Update selection
      |                            |
      |                            v
      |                      Scroll to block
      |
      +-- No --> Update selection
                  |
                  v
             Scroll to block
```

**Implementation:**

```python
async def action_nav_prev_block(self) -> None:
    """Navigate to the previous block."""
    if len(self._blocks) == 0:
        return

    # Check if we need to wrap
    if self._selected_index <= 0:
        if self.wrap_navigation:
            # Check if there are pruned blocks before first in-memory block
            if self._blocks[0].info.sequence > 0 and self._session_manager:
                # Need to load pruned block
                await self._load_and_select_pruned_block(
                    self._blocks[0].info.sequence - 1
                )
                return
            # No pruned blocks, wrap to last
            self._selected_index = len(self._blocks) - 1
        else:
            self.app.bell()
            return
    else:
        self._selected_index -= 1

    await self._select_and_scroll()

async def _load_and_select_pruned_block(self, target_sequence: int) -> None:
    """Load a pruned block and select it."""
    if self._is_loading:
        return  # Debounce

    self.add_class("loading")
    try:
        restored = await self._restore_pruned_blocks(target_sequence, count=1)
        if restored:
            # Find the newly loaded block
            for i, block in enumerate(self._blocks):
                if block.info.sequence == target_sequence:
                    self._selected_index = i
                    self.selected_block = block.info.block_id
                    await self._scroll_to_selected()
                    break
    finally:
        self.remove_class("loading")
```

### 9.2 Loading State During Navigation

**Visual Feedback:**

```css
Conversation.loading {
  opacity: 0.7;
}

Conversation.loading .loading-indicator {
  dock: top;
  height: 1;
  background: $warning;
  color: $background;
  content-align: center;
}
```

---

## 10. Implementation Recommendations

### 10.1 CSS Class Names

**Add to `base.tcss`:**

```css
/* Block selection styles */
Conversation .block {
  /* Base block styling - applies to all blocks */
}

Conversation .block.selected {
  /* Selected block - background tint */
  background: $accent 10%;
}

Conversation .block.selected.user {
  background: $accent 15%;
  border-left: thick $accent;
}

Conversation .block.selected.assistant {
  background: $success 15%;
  border-left: thick $success;
}

Conversation .block.selected.system {
  background: $warning 15%;
  border-left: thick $warning;
}

Conversation .block.selected.tool {
  background: $info 15%;
  border-left: thick $info;
}
```

### 10.2 Implementation Order

**Recommended Implementation Sequence:**

1. **Add reactive properties:** `selected_block`, `wrap_navigation`, `navigation_bell`
2. **Add internal state:** `_selected_index`, `_is_loading_context`
3. **Add CSS classes:** Update `base.tcss` with selection styles
4. **Implement navigation actions:** `action_nav_prev_block`, `action_nav_next_block`, `action_deselect_block`
5. **Add key bindings:** Update `BINDINGS`
6. **Implement visual update:** `_update_selected_visual()` method
7. **Implement scroll-to-selected:** `_scroll_to_selected()` method
8. **Add click-to-select:** `on_click` handler
9. **Handle pruned block loading:** `_load_and_select_pruned_block()` method
10. **Add accessibility:** Screen reader announcements

### 10.3 Test Coverage Requirements

**Required Tests:**

1. **Navigation Actions:**
   - `Alt+Down` selects next block
   - `Alt+Up` selects previous block
   - `Escape` clears selection
   - Navigation wraps when `wrap_navigation=True`
   - Navigation stops at boundaries when `wrap_navigation=False`

2. **Visual Feedback:**
   - Selected block has `.selected` CSS class
   - Role colors are preserved on selection
   - Selection clears on `clear()`

3. **State Management:**
   - `selected_block` property returns correct ID
   - `selected_block` returns None when no selection
   - Selection clears when content is cleared
   - Selection does not persist across sessions

4. **Pruned Block Loading:**
   - Navigation triggers load for pruned blocks
   - Loading indicator shown during load
   - Concurrent navigation blocked during load
   - Selection updated after successful load

5. **Click-to-Select:**
   - Click on block selects it
   - Click updates `selected_block` property

6. **Accessibility:**
   - Screen reader announcement on selection change

---

## 11. Acceptance Criteria Refinement

**Original Acceptance Criteria:**

- [ ] `Alt+Up` / `Alt+Down` navigate between blocks
- [ ] Navigation triggers load when reaching pruned blocks
- [ ] Selected block has visual highlight (distinct border/background)
- [ ] `selected_block` property returns current selection (or None)
- [ ] Navigation wraps at top/bottom (configurable)

**Refined Acceptance Criteria:**

- [ ] `Alt+Up` navigates to previous block, `Alt+Down` to next block
- [ ] `Escape` clears selection (deselects current block)
- [ ] Navigation triggers transparent load when reaching pruned blocks
- [ ] Loading indicator shown during pruned block restoration
- [ ] Selected block has subtle background highlight (10-15% opacity)
- [ ] Role colors preserved on selection (blue=user, green=assistant, etc.)
- [ ] `selected_block: reactive[str | None]` returns current block ID or None
- [ ] `selected_block_index` property returns 0-indexed position or None
- [ ] `selected_block_info` property returns BlockInfo or None
- [ ] `wrap_navigation: reactive[bool]` configures wrap behavior (default: True)
- [ ] `navigation_bell: reactive[bool]` configures audio/visual bell (default: True)
- [ ] Visual bell when wrapping or at boundary with wrap disabled
- [ ] Click on block selects that block
- [ ] Auto-scroll centers selected block in viewport
- [ ] Selection cleared on `clear()`
- [ ] Selection not persisted across sessions
- [ ] Screen reader announces selected block role and content preview

---

## 12. API Dependencies

**No new API endpoints required.** This is a pure frontend/UX feature.

**Internal Dependencies:**

| Component | Dependency | Status |
|-----------|------------|--------|
| Block rendering | `_render_block_to_strips()` | Existing |
| Block lookup | `get_block_id_at_line()` | Existing |
| Pruned block loading | `_restore_pruned_blocks()` | Existing |
| Session manager | `SessionManager.load_block_by_sequence()` | Existing |

---

## 13. Summary

This UX review provides comprehensive design guidance for implementing block navigation and selection in the Conversation widget. The key design decisions are:

1. **Visual Treatment:** Subtle background highlight (10-15% opacity) with role-based border accent
2. **Navigation Model:** Alt+Up/Down for navigation, Escape to deselect, click to select
3. **Scroll Behavior:** Auto-scroll to center selected block with 200ms animation
4. **Wrap Behavior:** Configurable with visual bell feedback at boundaries
5. **State Management:** Transient selection, reactive properties, no persistence
6. **Accessibility:** Screen reader announcements with role and content preview
7. **Pruned Block Handling:** Transparent loading with visual indicator

The implementation should follow the recommended sequence and include comprehensive test coverage for all navigation, visual, and state management scenarios.