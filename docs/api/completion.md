# Completion System

clitic provides a completion system with pluggable providers.

## Completion

Dataclass representing a single completion suggestion.

```{eval-rst}
.. autoclass:: clitic.completion.Completion
   :members:
```

### Creating Completions

```python
from clitic.completion import Completion

# Basic completion
completion = Completion(
    text="print",
    display_text="print()"
)

# With details
completion = Completion(
    text="function_name",
    display_text="function_name(args)",
    cursor_offset=-1,  # Cursor before closing paren
    description="Call function",
    priority=10,
    metadata={"type": "function"}
)
```

## CompletionProvider

Base class for completion providers.

```{eval-rst}
.. autoclass:: clitic.completion.CompletionProvider
   :members:
   :show-inheritance:
```

### Creating a Completion Provider

```python
from clitic.completion import CompletionProvider, Completion

class PathCompletionProvider(CompletionProvider):
    @property
    def name(self) -> str:
        return "path"

    @property
    def priority(self) -> int:
        return 10

    def get_completions(self, text: str, cursor_position: int) -> list[Completion]:
        # Return completions based on current context
        completions = []

        # Check if we're in a path context
        if "/" in text or text.startswith("~"):
            # Find files matching pattern
            for path in find_matching_paths(text):
                completions.append(Completion(
                    text=path,
                    display_text=path,
                    priority=5
                ))

        return completions

    async def get_completions_async(self, text: str, cursor_position: int) -> list[Completion]:
        # Async version for slow sources
        return self.get_completions(text, cursor_position)
```

## Completion Ordering

Completions are sorted by:
1. Priority (higher first)
2. Display text (alphabetically)

This ensures the most relevant completions appear first.

## Using with InputBar

```python
from clitic import App
from clitic.completion import CompletionProvider

class MyCompletionProvider(CompletionProvider):
    # ... implementation ...

app = App()
# InputBar will use registered providers
# (integration coming in future versions)
```