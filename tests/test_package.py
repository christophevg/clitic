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