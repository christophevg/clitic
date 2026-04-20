"""Tests for App CSS_PATH and theme configuration."""

from __future__ import annotations

import pytest


class TestAppCSSPath:
  """Tests for CSS_PATH configuration and file accessibility."""

  def test_css_path_is_class_attribute(self) -> None:
    """CSS_PATH should be a class attribute on App."""
    from clitic import App

    assert hasattr(App, "CSS_PATH")
    assert isinstance(App.CSS_PATH, str)

  def test_css_path_points_to_base_tcss(self) -> None:
    """CSS_PATH should point to base.tcss."""
    from clitic import App

    assert "base.tcss" in App.CSS_PATH

  def test_css_path_resolves_via_importlib_resources(self) -> None:
    """CSS_PATH should be resolvable via importlib.resources."""
    from importlib.resources import files

    from clitic import App

    expected_path = str(files("clitic.styles").joinpath("base.tcss"))
    assert App.CSS_PATH == expected_path

  def test_css_file_exists_and_is_readable(self) -> None:
    """The CSS file should exist and be readable."""
    from importlib.resources import files

    css_path = files("clitic.styles").joinpath("base.tcss")
    content = css_path.read_text()
    assert len(content) > 0

  def test_css_file_contains_base_styles(self) -> None:
    """The CSS file should contain base app styles."""
    from importlib.resources import files

    content = files("clitic.styles").joinpath("base.tcss").read_text()
    # Verify key style components exist
    assert "App {" in content or "App{" in content

  def test_css_file_contains_color_variables(self) -> None:
    """The CSS file should define color variables."""
    from importlib.resources import files

    content = files("clitic.styles").joinpath("base.tcss").read_text()
    # Verify color variable definitions
    assert "$background" in content
    assert "$foreground" in content


class TestAppThemeProperty:
  """Tests for theme_name property getter and setter."""

  def test_theme_name_default_value(self) -> None:
    """App should default to 'dark' theme."""
    from clitic import App

    app = App()
    assert app.theme_name == "dark"

  def test_theme_name_can_be_set_at_init(self) -> None:
    """theme_name should be settable via constructor."""
    from clitic import App

    app = App(theme_name="light")
    assert app.theme_name == "light"

  def test_theme_name_custom_value(self) -> None:
    """theme_name should accept any string value."""
    from clitic import App

    app = App(theme_name="custom_theme")
    assert app.theme_name == "custom_theme"

  def test_theme_name_is_read_only_property(self) -> None:
    """theme_name should be a read-only property (no setter)."""
    from clitic import App

    app = App()
    # Verify it's a property with no setter
    # Attempting to set should raise AttributeError
    with pytest.raises(AttributeError):
      app.theme_name = "new_theme"  # type: ignore[misc]

  def test_theme_name_internal_storage(self) -> None:
    """theme_name should be stored in _theme_name attribute."""
    from clitic import App

    app = App(theme_name="stored")
    assert app._theme_name == "stored"

  def test_theme_name_with_title_parameter(self) -> None:
    """theme_name should work alongside title parameter."""
    from clitic import App

    app = App(title="My App", theme_name="light")
    assert app.title == "My App"
    assert app.theme_name == "light"


class TestAppThemeIntegration:
  """Tests documenting current theme integration behavior.

  NOTE: Theme switching is NOT currently implemented. These tests
  document the current behavior where theme_name is stored but
  does NOT affect CSS loading.
  """

  def test_theme_name_does_not_change_css_path(self) -> None:
    """Changing theme_name should NOT change CSS_PATH (current behavior).

    This test documents that theme switching is NOT implemented.
    The CSS_PATH remains hardcoded to base.tcss regardless of theme_name.
    """
    from clitic import App

    app_dark = App(theme_name="dark")
    app_light = App(theme_name="light")
    app_custom = App(theme_name="custom")

    # All apps use the same CSS_PATH
    assert app_dark.CSS_PATH == app_light.CSS_PATH
    assert app_light.CSS_PATH == app_custom.CSS_PATH
    assert "base.tcss" in app_dark.CSS_PATH

  def test_css_path_is_class_level_not_instance_level(self) -> None:
    """CSS_PATH is a class attribute, not affected by instance theme_name.

    This documents that CSS_PATH cannot be customized per-instance.
    """
    from clitic import App

    # Create multiple apps with different themes
    apps = [
      App(theme_name="dark"),
      App(theme_name="light"),
      App(theme_name="solarized"),
    ]

    # All share the same CSS_PATH from the class
    css_paths = [app.CSS_PATH for app in apps]
    assert len(set(css_paths)) == 1  # All identical

  async def test_theme_name_persists_in_mounted_app(self) -> None:
    """theme_name should persist when app is mounted.

    This verifies theme_name survives the app lifecycle.
    """
    from clitic import App

    async with App(theme_name="custom").run_test() as pilot:
      assert pilot.app.theme_name == "custom"

  @pytest.mark.xfail(reason="Theme switching not implemented")
  def test_theme_switching_would_load_different_css(self) -> None:
    """FAILING: Theme switching is not yet implemented.

    This test documents the desired future behavior.
    It will fail until theme switching is implemented.
    """
    from clitic import App

    # This is aspirational - will fail
    app_dark = App(theme_name="dark")
    app_light = App(theme_name="light")

    # Currently fails - both use base.tcss
    # Future: Should use theme-specific CSS
    assert app_dark.CSS_PATH != app_light.CSS_PATH
