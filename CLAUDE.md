# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

clitic is a Python package for building rich, interactive CLI applications (TUIs). Built on Textual for the TUI framework and Rich for rendering.

## Development Setup

Uses pyenv for virtual environment management. A virtual environment is required for all development operations.

```bash
# Create pyenv virtualenv
make setup

# Activate the virtual environment
pyenv activate clitic

# Install dependencies
make install
```

For automatic activation, create `.python-version`:
```bash
echo 'clitic' > .python-version
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Create pyenv virtualenv |
| `make activate` | Show activation instructions |
| `make install` | Install dev dependencies (venv required) |
| `make test` | Run tests with coverage |
| `make test-file FILE=<path>` | Run specific test file |
| `make test-one TEST=<path>` | Run specific test function |
| `make showcase` | Run feature showcase application |
| `make screenshot` | Capture screenshot of showcase |
| `make docs` | Build HTML documentation |
| `make docs-view` | Build and open documentation in browser |
| `make typecheck` | Run mypy type checking |
| `make lint` | Run ruff linting |
| `make format` | Format code with ruff |
| `make check` | Run all checks (typecheck + lint) |
| `make build` | Build package distributions |
| `make publish` | Build and publish to PyPI |
| `make publish-test` | Build and publish to TestPyPI |
| `make clean` | Remove build artifacts |
| `make clean-all` | Remove build artifacts and virtualenv |

All development targets require an active virtual environment and will fail with instructions if not detected.

## Pre-Commit Requirements

Before any commit, the following must be verified:

1. **All tests pass:** `make test`
2. **Showcase runs correctly:** `make showcase` (user must confirm visually)
3. **Type checking passes:** `make typecheck`
4. **Linting passes:** `make lint`

The showcase application (`python -m clitic`) must demonstrate all currently implemented features and run without errors.

## Documentation Requirements

The project uses Sphinx for documentation, published to readthedocs.org.

### When Adding New Features

1. Update the showcase application (`src/clitic/__main__.py`)
2. Update API reference (`docs/api/`)
3. Update README.md if the feature affects user-facing API
4. Update screenshot if showcase changed:
   - Run `make screenshot` to capture the current showcase
   - Ask user to verify the screenshot is correct before committing
5. Update changelog (`docs/development/changelog.md`)

### Documentation Files

- `docs/index.md` - Documentation home
- `docs/installation.md` - Installation guide
- `docs/quickstart.md` - Quick start guide
- `docs/api/` - API reference (one file per module)
- `docs/development/` - Development guides

### Building Documentation

```bash
# Build HTML documentation
cd docs && make html

# View locally
open docs/_build/html/index.html
```

## Showcase Application

The package is executable and provides a living showcase of implemented features:

```bash
python -m clitic
# or
make showcase
```

The showcase (`src/clitic/__main__.py`) should be updated as features are implemented to demonstrate them.

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
- Dev: pytest, pytest-cov, pytest-asyncio, mypy, ruff, build, twine