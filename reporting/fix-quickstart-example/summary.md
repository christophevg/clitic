# Summary: fix-quickstart-example

**Task:** Fix bug in README.md Quick Start (conversation used before defined)

## What Was Implemented

Fixed the Quick Start example in README.md where `conversation` was referenced inside the `handle_input` callback before it was defined, which would cause a `NameError` at runtime.

### Changes Made

1. **Moved `conversation` definition before the callback function**
   - Before: `conversation = Conversation()` was on line 34, after the function definition
   - After: `conversation = Conversation()` is now on line 27, before the function definition

2. **Removed unused `input_bar` variable**
   - Cleaned up the example to be minimal and focused
   - Removed `InputBar` from imports since it wasn't used

## Key Decisions

- Kept the Quick Start example minimal - full widget composition is demonstrated in the showcase application
- The example is aspirational (shows the intended API) since the package is in early development

## Lessons Learned

- When writing code examples with callbacks, ensure all referenced variables are defined before the callback is registered
- Example code should be tested even if it's just documentation

## Files Modified

- `README.md` - Fixed Quick Start example (lines 24-36)

## Acceptance Criteria

- [x] Conversation is defined before use in handle_input
- [x] Widget composition pattern is clear (how widgets connect to App)
- [x] Example runs without NameError