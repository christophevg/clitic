"""Tests for clitic exception hierarchy."""

import pytest

from clitic.exceptions import (
  CliticError,
  ConfigurationError,
  PluginError,
  RenderError,
)


class TestCliticError:
  """Tests for the base CliticError exception."""

  def test_is_exception(self) -> None:
    """CliticError should be an Exception."""
    assert issubclass(CliticError, Exception)

  def test_can_be_raised(self) -> None:
    """CliticError can be raised."""
    with pytest.raises(CliticError):
      raise CliticError("test error")

  def test_can_be_caught_as_exception(self) -> None:
    """CliticError can be caught as Exception."""
    with pytest.raises(Exception):  # noqa: B017
      raise CliticError("test error")

  def test_message_preserved(self) -> None:
    """CliticError preserves error message."""
    error = CliticError("something went wrong")
    assert "something went wrong" in str(error)


class TestPluginError:
  """Tests for PluginError exception."""

  def test_is_clitic_error(self) -> None:
    """PluginError should inherit from CliticError."""
    assert issubclass(PluginError, CliticError)

  def test_can_be_raised(self) -> None:
    """PluginError can be raised with required attributes."""
    with pytest.raises(PluginError):
      raise PluginError(plugin_name="TestPlugin", operation="load")

  def test_can_be_caught_as_clitic_error(self) -> None:
    """PluginError can be caught as CliticError."""
    with pytest.raises(CliticError):
      raise PluginError(plugin_name="TestPlugin", operation="load")

  def test_attributes_set(self) -> None:
    """PluginError sets attributes correctly."""
    error = PluginError(
      plugin_name="MarkdownRenderer",
      operation="initialize",
      message="Config not found",
    )
    assert error.plugin_name == "MarkdownRenderer"
    assert error.operation == "initialize"

  def test_str_without_message(self) -> None:
    """PluginError formats message without additional context."""
    error = PluginError(plugin_name="TestPlugin", operation="load")
    assert str(error) == "Plugin 'TestPlugin' failed during load."

  def test_str_with_message(self) -> None:
    """PluginError formats message with additional context."""
    error = PluginError(
      plugin_name="TestPlugin",
      operation="load",
      message="module not found",
    )
    assert str(error) == "Plugin 'TestPlugin' failed during load: module not found"

  def test_repr_contains_all_info(self) -> None:
    """PluginError repr contains all relevant information."""
    error = PluginError(
      plugin_name="TestPlugin",
      operation="load",
      message="test",
    )
    repr_str = repr(error)
    assert "PluginError" in repr_str
    assert "TestPlugin" in repr_str
    assert "load" in repr_str

  def test_message_default_none(self) -> None:
    """PluginError message defaults to None."""
    error = PluginError(plugin_name="TestPlugin", operation="load")
    assert error._message is None


class TestConfigurationError:
  """Tests for ConfigurationError exception."""

  def test_is_clitic_error(self) -> None:
    """ConfigurationError should inherit from CliticError."""
    assert issubclass(ConfigurationError, CliticError)

  def test_can_be_raised(self) -> None:
    """ConfigurationError can be raised with required attributes."""
    with pytest.raises(ConfigurationError):
      raise ConfigurationError(setting="theme")

  def test_can_be_caught_as_clitic_error(self) -> None:
    """ConfigurationError can be caught as CliticError."""
    with pytest.raises(CliticError):
      raise ConfigurationError(setting="theme")

  def test_attributes_set(self) -> None:
    """ConfigurationError sets attributes correctly."""
    error = ConfigurationError(
      setting="port",
      expected="integer between 1 and 65535",
      message="got 'abc'",
    )
    assert error.setting == "port"
    assert error.expected == "integer between 1 and 65535"

  def test_str_without_extras(self) -> None:
    """ConfigurationError formats message without extras."""
    error = ConfigurationError(setting="theme")
    assert str(error) == "Configuration error for setting 'theme'."

  def test_str_with_expected(self) -> None:
    """ConfigurationError formats message with expected values."""
    error = ConfigurationError(
      setting="theme",
      expected="one of: 'dark', 'light'",
    )
    assert str(error) == "Configuration error for setting 'theme'. Expected one of: 'dark', 'light'"

  def test_str_with_message(self) -> None:
    """ConfigurationError formats message with additional context."""
    error = ConfigurationError(
      setting="theme",
      message="invalid value 'unknown'",
    )
    assert str(error) == "Configuration error for setting 'theme': invalid value 'unknown'"

  def test_str_with_message_takes_precedence(self) -> None:
    """ConfigurationError message takes precedence over expected."""
    error = ConfigurationError(
      setting="theme",
      expected="one of: 'dark', 'light'",
      message="invalid value",
    )
    # Message should take precedence
    assert "invalid value" in str(error)
    assert "Expected" not in str(error)

  def test_repr_contains_all_info(self) -> None:
    """ConfigurationError repr contains all relevant information."""
    error = ConfigurationError(
      setting="theme",
      expected="'dark' or 'light'",
      message="test",
    )
    repr_str = repr(error)
    assert "ConfigurationError" in repr_str
    assert "theme" in repr_str

  def test_expected_default_none(self) -> None:
    """ConfigurationError expected defaults to None."""
    error = ConfigurationError(setting="theme")
    assert error.expected is None


class TestRenderError:
  """Tests for RenderError exception."""

  def test_is_clitic_error(self) -> None:
    """RenderError should inherit from CliticError."""
    assert issubclass(RenderError, CliticError)

  def test_can_be_raised(self) -> None:
    """RenderError can be raised with required attributes."""
    with pytest.raises(RenderError):
      raise RenderError(content_type="markdown", renderer="MarkdownRenderer")

  def test_can_be_caught_as_clitic_error(self) -> None:
    """RenderError can be caught as CliticError."""
    with pytest.raises(CliticError):
      raise RenderError(content_type="markdown", renderer="MarkdownRenderer")

  def test_attributes_set(self) -> None:
    """RenderError sets attributes correctly."""
    error = RenderError(
      content_type="markdown",
      renderer="MarkdownRenderer",
      message="Failed to parse",
    )
    assert error.content_type == "markdown"
    assert error.renderer == "MarkdownRenderer"

  def test_str_without_message(self) -> None:
    """RenderError formats message without additional context."""
    error = RenderError(
      content_type="markdown",
      renderer="MarkdownRenderer",
    )
    assert str(error) == "Renderer 'MarkdownRenderer' failed for content type 'markdown'."

  def test_str_with_message(self) -> None:
    """RenderError formats message with additional context."""
    error = RenderError(
      content_type="markdown",
      renderer="MarkdownRenderer",
      message="invalid table syntax",
    )
    assert str(error) == (
      "Renderer 'MarkdownRenderer' failed for content type 'markdown': invalid table syntax"
    )

  def test_repr_contains_all_info(self) -> None:
    """RenderError repr contains all relevant information."""
    error = RenderError(
      content_type="markdown",
      renderer="MarkdownRenderer",
      message="test",
    )
    repr_str = repr(error)
    assert "RenderError" in repr_str
    assert "markdown" in repr_str
    assert "MarkdownRenderer" in repr_str

  def test_message_default_none(self) -> None:
    """RenderError message defaults to None."""
    error = RenderError(content_type="markdown", renderer="TestRenderer")
    assert error._message is None


class TestExceptionHierarchy:
  """Tests for exception hierarchy relationships."""

  def test_plugin_error_is_instance_of_clitic_error(self) -> None:
    """PluginError instance should be instance of CliticError."""
    error = PluginError(plugin_name="Test", operation="test")
    assert isinstance(error, CliticError)
    assert isinstance(error, Exception)

  def test_configuration_error_is_instance_of_clitic_error(self) -> None:
    """ConfigurationError instance should be instance of CliticError."""
    error = ConfigurationError(setting="test")
    assert isinstance(error, CliticError)
    assert isinstance(error, Exception)

  def test_render_error_is_instance_of_clitic_error(self) -> None:
    """RenderError instance should be instance of CliticError."""
    error = RenderError(content_type="test", renderer="TestRenderer")
    assert isinstance(error, CliticError)
    assert isinstance(error, Exception)

  def test_catching_clitic_error_catches_all(self) -> None:
    """Catching CliticError should catch all specific errors."""
    errors_to_raise = [
      PluginError(plugin_name="Test", operation="load"),
      ConfigurationError(setting="test"),
      RenderError(content_type="test", renderer="Test"),
    ]

    for error in errors_to_raise:
      with pytest.raises(CliticError):
        raise error


class TestExceptionScenarios:
  """Tests for realistic error scenarios."""

  def test_plugin_not_found_scenario(self) -> None:
    """Simulate a plugin not found error."""
    with pytest.raises(PluginError) as exc_info:
      raise PluginError(
        plugin_name="CustomRenderer",
        operation="import",
        message="No module named 'custom_renderer'",
      )

    error = exc_info.value
    assert "CustomRenderer" in str(error)
    assert "import" in str(error)
    assert "No module named" in str(error)

  def test_invalid_config_scenario(self) -> None:
    """Simulate an invalid configuration error."""
    with pytest.raises(ConfigurationError) as exc_info:
      raise ConfigurationError(
        setting="max_history",
        expected="positive integer",
        message="got -5",
      )

    error = exc_info.value
    assert "max_history" in str(error)
    assert "-5" in str(error)

  def test_rendering_failure_scenario(self) -> None:
    """Simulate a rendering failure error."""
    with pytest.raises(RenderError) as exc_info:
      raise RenderError(
        content_type="diff",
        renderer="DiffRenderer",
        message="Binary files cannot be rendered",
      )

    error = exc_info.value
    assert "diff" in str(error)
    assert "DiffRenderer" in str(error)
    assert "Binary files" in str(error)

  def test_catching_specific_vs_base_error(self) -> None:
    """Test catching specific vs base error types."""
    # Can catch specific error
    with pytest.raises(PluginError):
      raise PluginError(plugin_name="Test", operation="test")

    # Can catch as base error
    with pytest.raises(CliticError):
      raise PluginError(plugin_name="Test", operation="test")

  def test_error_not_caught_by_wrong_type(self) -> None:
    """Specific errors are not caught by wrong exception type."""
    with pytest.raises(PluginError):
      try:
        raise PluginError(plugin_name="Test", operation="test")
      except ConfigurationError:
        pytest.fail("PluginError should not be caught as ConfigurationError")
      except RenderError:
        pytest.fail("PluginError should not be caught as RenderError")
