"""Tests for syntax highlighting theme utilities.

This module tests the theme mapping functions for converting Textual
app themes to Pygments themes.
"""

from clitic.utils.highlight import THEME_MAP, get_pygments_theme


class TestThemeMap:
  """Tests for THEME_MAP dictionary."""

  def test_theme_map_dark_to_monokai(self) -> None:
    """Dark theme should map to monokai."""
    assert THEME_MAP["dark"] == "monokai"

  def test_theme_map_light_to_github_light(self) -> None:
    """Light theme should map to github-light."""
    assert THEME_MAP["light"] == "github-light"

  def test_theme_map_none_to_monokai(self) -> None:
    """None should map to monokai (default)."""
    assert THEME_MAP[None] == "monokai"


class TestGetPygmentsTheme:
  """Tests for get_pygments_theme function."""

  def test_dark_returns_monokai(self) -> None:
    """get_pygments_theme('dark') should return 'monokai'."""
    assert get_pygments_theme("dark") == "monokai"

  def test_light_returns_github_light(self) -> None:
    """get_pygments_theme('light') should return 'github-light'."""
    assert get_pygments_theme("light") == "github-light"

  def test_none_returns_monokai(self) -> None:
    """get_pygments_theme(None) should return 'monokai'."""
    assert get_pygments_theme(None) == "monokai"

  def test_unknown_returns_monokai(self) -> None:
    """get_pygments_theme with unknown theme should return 'monokai'."""
    assert get_pygments_theme("unknown") == "monokai"
    assert get_pygments_theme("custom-theme") == "monokai"

  def test_empty_string_returns_monokai(self) -> None:
    """get_pygments_theme('') should return 'monokai'."""
    assert get_pygments_theme("") == "monokai"
