# Consensus: conversation-block-model

## Date
2026-04-14

## Reviewers
- functional-analyst
- api-architect
- ui-ux-designer

## Status
**APPROVED** - All reviewers agree on the design.

---

## Final Design Specification

### BlockInfo Frozen Dataclass

```python
@dataclass(frozen=True)
class BlockInfo:
    """Immutable block information for public API access."""
    block_id: str
    role: str
    content: str
    metadata: dict[str, Any]
    timestamp: datetime  # UTC-aware
    sequence: int  # 0-indexed position in conversation

    @property
    def relative_timestamp(self) -> str:
        """Human-readable relative time (e.g., '2 min ago')."""
        ...
```

### Conversation API Additions

```python
class Conversation(ScrollView):
    def __init__(
        self,
        *,
        session_uuid: str | None = None,
        **kwargs
    ) -> None:
        """
        Args:
            session_uuid: Optional session UUID. Auto-generated if not provided.
        """
        ...

    @property
    def session_id(self) -> str:
        """Read-only session UUID."""
        ...

    def get_block(self, block_id: str) -> BlockInfo | None:
        """Get block by ID. O(1) performance."""
        ...

    def get_block_at_index(self, index: int) -> BlockInfo | None:
        """Get block by sequence position. O(1) performance."""
        ...

    def append(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Append a block. Returns block_id."""
        ...
```

### Internal Implementation

1. **_session_uuid: str** - UUID4 generated at init (or passed in)
2. **_sequence_counter: int** - Incremented on append, NEVER reset
3. **_block_index: dict[str, int]** - Maps block_id to list index for O(1) lookup
4. **_BlockData** - Internal dataclass wrapping BlockInfo + line_count

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Timestamp format | datetime (UTC-aware) | Standard, serializable, timezone-safe |
| Metadata mutability | Immutable | Aligned with chat paradigm |
| Session UUID | Auto-generate + optional param | Supports session persistence |
| Public API | get_block() method | Clean encapsulation |
| Block lookup | O(1) via index dict | Performance for 10,000+ blocks |
| Sequence counter | Never reset | Prevents ID collisions |

---

## Reviewer Notes

### functional-analyst
- Task is well-defined and ready for implementation
- Acceptance criteria are specific and testable
- Dependency (conversation-virtual-rendering) is complete

### api-architect
- Frozen dataclass design is correct
- O(1) lookup is critical for performance
- session_id property provides clean encapsulation

### ui-ux-designer
- Sequence field enables display-friendly navigation
- relative_timestamp property essential for UX
- Immutability aligns with chat paradigm

---

## Next Steps

1. Proceed to implementation via python-developer agent
2. Update tests for new block ID format
3. Update showcase to demonstrate new features