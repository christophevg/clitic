# Contributing

Thank you for your interest in contributing to clitic!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/christophevg/clitic.git
cd clitic

# Create and activate virtual environment
make setup
pyenv activate clitic

# Install dependencies
make install
```

## Development Commands

| Command | Description |
|---------|-------------|
| `make test` | Run tests with coverage |
| `make showcase` | Run feature showcase |
| `make typecheck` | Run mypy type checking |
| `make lint` | Run ruff linting |
| `make format` | Format code with ruff |
| `make check` | Run all checks |

## Code Style

- Two-space indentation
- 100 character max line length
- Full type hints (mypy strict mode)
- Follow PEP 8 conventions

## Testing

Tests are located in the `tests/` directory. Run tests with:

```bash
make test
```

### Running Specific Tests

```bash
# Run specific test file
make test-file FILE=tests/test_app.py

# Run specific test function
make test-one TEST=tests/test_app.py::TestApp::test_app_can_be_instantiated
```

## Pre-Commit Checklist

Before committing, ensure:

1. All tests pass: `make test`
2. Showcase runs correctly: `make showcase`
3. Type checking passes: `make typecheck`
4. Linting passes: `make lint`

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Run all checks
4. Submit a pull request

## Documentation

Update documentation when adding new features:

1. Update showcase (`src/clitic/__main__.py`)
2. Update API reference (`docs/api/`)
3. Update README.md if needed
4. Update screenshot if showcase changed:
   ```bash
   make screenshot
   ```