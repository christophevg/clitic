# Installation

## Requirements

- Python 3.10+
- [pyenv](https://github.com/pyenv/pyenv) with pyenv-virtualenv plugin (recommended)

## Install from PyPI

```bash
pip install clitic
```

## Development Installation

For contributing to clitic development:

```bash
# Clone the repository
git clone https://github.com/xtof/clitic.git
cd clitic

# Create and activate virtual environment
make setup
pyenv activate clitic

# Or for automatic activation:
echo 'clitic' > .python-version

# Install dependencies
make install
```

## Verify Installation

```python
import clitic
print(clitic.__version__)
```

## Dependencies

clitic requires the following packages:

- `textual>=0.50.0` - TUI framework
- `rich>=13.0.0` - Terminal rendering

These are automatically installed with clitic.