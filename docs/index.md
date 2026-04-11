# clitic Documentation

A Python package for building rich, interactive CLI applications.

## Why "clitic"?

The name is a playful linguistic reference. A **clitic** (/ˈklɪtɪk/) is an unstressed word that normally occurs only in combination with another word — like the 'm in "I'm".

The name fits perfectly because:

- It starts with **"CLI"** — Command Line Interface
- Like its linguistic namesake, **clitic** is designed to exist in combination with another project — yours! It's a framework meant to be the foundation for your rich interactive CLI applications.

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/app
api/widgets
api/exceptions
api/plugins
api/completion
```

```{toctree}
:maxdepth: 2
:caption: Development

development/contributing
development/changelog
```

## Overview

clitic provides reusable components for building terminal user interfaces (TUIs) with:

- **Multiline input** with syntax highlighting and history navigation
- **Scrollable content areas** with pluggable renderers
- **Markdown, diff, and terminal content rendering**
- **CSS-like styling and theming**
- **Responsive layouts** that adapt to terminal width

Built on [Textual](https://textual.textualize.io/) for the TUI framework, with [Rich](https://rich.readthedocs.io/) for rendering.

## Showcase

![Current Showcase](_static/current-showcase.png)

The package includes an executable showcase demonstrating all implemented features:

```bash
python -m clitic
# or
make showcase
```

## License

MIT License