# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-11

### Added

- Initial package structure with pyproject.toml
- Makefile with development workflow commands
- Basic tests (package import and version)

### Project Setup

- py.typed marker file for PEP 561 compliance
- GitHub Actions CI workflow
  - Test matrix: Python 3.10, 3.11, 3.12
  - OS: macOS, Linux, Windows
  - Typecheck with mypy --strict
  - Lint with ruff

### Foundation

- Exception hierarchy with `CliticError`, `PluginError`, `ConfigurationError`, `RenderError`
- Plugin base classes:
  - `ContentPlugin` ABC for content renderers
  - `ModeProvider` ABC for input mode providers
  - `CompletionProvider` ABC for completion sources
  - `Renderable` and `Highlighter` protocols
- `Completion` dataclass for completion suggestions
- `App` class extending Textual's App
  - Plugin management (`register_plugin`, `unregister_plugin`)
  - Input handling (`@app.on_submit` decorator)
  - Theme support
- Base TCSS stylesheet with color palette

### Documentation

- CLAUDE.md for Claude Code guidance
- Showcase application demonstrating implemented features
- Sphinx documentation setup for readthedocs.org

### Changed

- Dropped Python 3.9 support (requires Python 3.10+)
- Updated README.md Quick Start example