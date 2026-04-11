"""Basic tests for clitic package."""

import subprocess
import sys


def test_import() -> None:
  """Test that the package can be imported."""
  import clitic

  assert clitic.__version__ == "0.1.0"


def test_version() -> None:
  """Test version is accessible."""
  from clitic import __version__

  assert isinstance(__version__, str)
  assert len(__version__) > 0


def test_main_module_exists() -> None:
  """Test that __main__.py exists and is importable."""
  from clitic import __main__

  assert hasattr(__main__, "main")


def test_showcase_runs() -> None:
  """Test that the showcase application runs without error."""
  result = subprocess.run(
    [sys.executable, "-m", "clitic"],
    capture_output=True,
    text=True,
    timeout=10,
  )
  assert result.returncode == 0
  assert "clitic" in result.stdout.lower()
  assert "Version:" in result.stdout
