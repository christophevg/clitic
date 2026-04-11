# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

clitic is a Python package for building rich, interactive CLI applications (TUIs). Built on Textual for the TUI framework and Rich for rendering.

## Development Setup

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"
```

## Commands

```bash
# Run tests (coverage enabled by default)
pytest

# Run specific test file
pytest tests/test_package.py

# Run specific test function
pytest tests/test_package.py::test_import

# Type check
mypy src

# Lint
ruff check src tests

# Format code
ruff format src tests

# Build package
python -m build
```

## Architecture

### Package Structure

```
src/clitic/
  __init__.py          # Public API exports
  core/                 # App class, screen management
  widgets/              # InputBar, Conversation, Tree, Table widgets
  plugins/              # Content renderers (Markdown, Diff, Terminal)
  completion/           # Completion provider framework
  history/              # History storage/management
  themes/               # TCSS theme files (dark.tcss, light.tcss)
  styles/               # Base TCSS styles
  utils/                # Utilities (fuzzy matching, ANSI handling)
```

### Plugin System

Content renderers, completion providers, and input modes are implemented as plugins with base classes in:
- `plugins/base.py` - ContentPlugin interface
- `completion/base.py` - CompletionProvider interface

### Styling

Uses Textual's CSS-like styling (TCSS files). Themes are stored in `themes/`, base styles in `styles/`.

## Code Style

- Two-space indentation
- 100 character max line length
- Full type hints required (mypy strict mode)
- Public API explicitly exported via `__init__.py`
- One public class per file
- Private members prefixed with `_`

## Testing

- Test coverage target: >90%
- Tests located in `tests/` directory
- pytest with asyncio mode enabled
- Coverage reporting via pytest-cov

## Dependencies

- `textual>=0.50.0` - TUI framework
- `rich>=13.0.0` - Terminal rendering
- Dev: pytest, pytest-cov, pytest-asyncio, mypy, ruff