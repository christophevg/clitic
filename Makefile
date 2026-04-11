-include ~/.claude/Makefile

.PHONY: install test test-file typecheck lint format build publish clean help

# Default target
all: help

## Development

install: ## Install package in development mode with dev dependencies
	pip install -e ".[dev]"

test: ## Run all tests with coverage
	pytest

test-file: ## Run specific test file (usage: make test-file FILE=tests/test_package.py)
	pytest $(FILE)

test-one: ## Run specific test function (usage: make test-one TEST=tests/test_package.py::test_import)
	pytest $(TEST)

## Code Quality

typecheck: ## Run mypy type checking
	mypy src

lint: ## Run ruff linting
	ruff check src tests

format: ## Format code with ruff
	ruff format src tests

check: typecheck lint ## Run all checks (typecheck + lint)

## Build & Publish

build: ## Build package distributions
	python -m build

publish: build ## Build and publish to PyPI
	twine upload dist/*

publish-test: build ## Build and publish to TestPyPI
	twine upload --repository testpypi dist/*

## Cleanup

clean: ## Remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

## Help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'