"""Basic tests for clitic package."""


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
  """Test that the showcase application can be imported and has required components."""
  from clitic.__main__ import ShowcaseApp

  # Verify the showcase app class exists and has required methods
  assert hasattr(ShowcaseApp, "compose")
  assert hasattr(ShowcaseApp, "on_input_bar_submit")
