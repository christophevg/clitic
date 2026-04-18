"""Base classes for completion providers.

This module defines the data structures and abstract base classes for
the completion system in clitic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Completion:
    """Represents a single completion suggestion.

    Attributes:
        text: The text to insert when the completion is selected.
        display_text: The text to display in the completion dropdown.
        cursor_offset: Offset to move cursor after insertion (default 0).
        description: Optional description shown in the dropdown.
        priority: Priority for ordering (higher = shown first).
        metadata: Additional data associated with the completion.
    """

    text: str
    display_text: str
    cursor_offset: int = 0
    description: str = ""
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "Completion") -> bool:
        """Compare completions for sorting.

        Higher priority completions come first, then alphabetically by display_text.

        Args:
            other: Another Completion to compare against.

        Returns:
            True if this completion should come before other.
        """
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.display_text < other.display_text

    def __eq__(self, other: object) -> bool:
        """Check equality based on text and display_text.

        Args:
            other: Object to compare with.

        Returns:
            True if both are Completions with same text and display_text.
        """
        if not isinstance(other, Completion):
            return NotImplemented
        return self.text == other.text and self.display_text == other.display_text

    def __hash__(self) -> int:
        """Hash based on text and display_text.

        Returns:
            Hash value for use in sets and dicts.
        """
        return hash((self.text, self.display_text))


class CompletionProvider(ABC):
    """Abstract base class for completion providers.

    Completion providers generate completion suggestions based on the
    current input context. They are called as the user types to provide
    context-aware completions.

    Attributes:
        name: Human-readable name of the provider.
        priority: Priority for provider ordering (higher = preferred).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of this provider."""
        ...

    @property
    def priority(self) -> int:
        """Return the priority for this provider.

        Higher priority providers are queried first. Default is 0.

        Returns:
            Priority value (higher = more preferred).
        """
        return 0

    @abstractmethod
    def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        """Get completion suggestions for the current input.

        Args:
            text: Current input text.
            cursor_position: Current cursor position in the text.

        Returns:
            List of Completion suggestions, sorted by priority.
        """
        ...

    async def get_completions_async(self, text: str, cursor_position: int) -> list[Completion]:
        """Asynchronously get completion suggestions.

        Default implementation calls the synchronous method.
        Subclasses may override for async completion generation.

        Args:
            text: Current input text.
            cursor_position: Current cursor position in the text.

        Returns:
            List of Completion suggestions, sorted by priority.
        """
        return self.get_completions(text, cursor_position)
