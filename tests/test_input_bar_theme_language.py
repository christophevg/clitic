"""Tests for InputBar theme and language parameters."""

from textual.app import App, ComposeResult

from clitic import InputBar


class TestInputBarThemeParameter:
  """Tests for InputBar theme parameter."""

  def test_default_theme_is_monokai(self, input_bar: InputBar) -> None:
    """InputBar should default to monokai theme."""
    assert input_bar.theme == "monokai"

  def test_custom_theme_in_constructor(self) -> None:
    """InputBar should accept custom theme parameter."""
    input_bar = InputBar(theme="github_light")
    assert input_bar.theme == "github_light"

  def test_theme_vscode_dark(self) -> None:
    """InputBar should accept vscode_dark theme."""
    input_bar = InputBar(theme="vscode_dark")
    assert input_bar.theme == "vscode_dark"

  def test_theme_dracula(self) -> None:
    """InputBar should accept dracula theme."""
    input_bar = InputBar(theme="dracula")
    assert input_bar.theme == "dracula"

  def test_theme_css(self) -> None:
    """InputBar should accept css theme."""
    input_bar = InputBar(theme="css")
    assert input_bar.theme == "css"

  def test_theme_can_be_changed(self) -> None:
    """InputBar theme should be changeable after creation."""
    input_bar = InputBar(theme="monokai")
    assert input_bar.theme == "monokai"

    # TextArea allows theme to be changed
    input_bar.theme = "github_light"
    assert input_bar.theme == "github_light"

  def test_theme_property_access_via_text_area(self) -> None:
    """Theme should be accessible via TextArea's theme property."""
    input_bar = InputBar(theme="vscode_dark")
    # InputBar extends TextArea, so theme property should work
    assert input_bar.theme == "vscode_dark"


class TestInputBarLanguageParameter:
  """Tests for InputBar language parameter."""

  def test_default_language_is_none(self, input_bar: InputBar) -> None:
    """InputBar should default to None language (no highlighting)."""
    assert input_bar.language is None

  def test_custom_language_in_constructor(self) -> None:
    """InputBar should accept custom language parameter."""
    input_bar = InputBar(language="python")
    assert input_bar.language == "python"

  def test_language_python(self) -> None:
    """InputBar should accept python language."""
    input_bar = InputBar(language="python")
    assert input_bar.language == "python"

  def test_language_javascript(self) -> None:
    """InputBar should accept javascript language."""
    input_bar = InputBar(language="javascript")
    assert input_bar.language == "javascript"

  def test_language_markdown(self) -> None:
    """InputBar should accept markdown language."""
    input_bar = InputBar(language="markdown")
    assert input_bar.language == "markdown"

  def test_language_json(self) -> None:
    """InputBar should accept json language."""
    input_bar = InputBar(language="json")
    assert input_bar.language == "json"

  def test_language_html(self) -> None:
    """InputBar should accept html language."""
    input_bar = InputBar(language="html")
    assert input_bar.language == "html"

  def test_language_css(self) -> None:
    """InputBar should accept css language."""
    input_bar = InputBar(language="css")
    assert input_bar.language == "css"

  def test_language_sql(self) -> None:
    """InputBar should accept sql language."""
    input_bar = InputBar(language="sql")
    assert input_bar.language == "sql"

  def test_language_bash(self) -> None:
    """InputBar should accept bash language."""
    input_bar = InputBar(language="bash")
    assert input_bar.language == "bash"

  def test_language_can_be_changed(self) -> None:
    """InputBar language should be changeable after creation."""
    input_bar = InputBar(language=None)
    assert input_bar.language is None

    # TextArea allows language to be changed
    input_bar.language = "python"
    assert input_bar.language == "python"

  def test_language_property_access_via_text_area(self) -> None:
    """Language should be accessible via TextArea's language property."""
    input_bar = InputBar(language="python")
    # InputBar extends TextArea, so language property should work
    assert input_bar.language == "python"

  def test_language_with_text_content(self) -> None:
    """InputBar should work with both language and text parameters."""
    input_bar = InputBar(text="def hello(): pass", language="python")
    assert input_bar.text == "def hello(): pass"
    assert input_bar.language == "python"


class TestInputBarLanguageSwitching:
  """Tests for InputBar language switching at runtime."""

  def test_switch_from_none_to_python(self) -> None:
    """Should be able to switch from no highlighting to Python."""
    input_bar = InputBar(language=None)
    assert input_bar.language is None

    input_bar.language = "python"
    assert input_bar.language == "python"

  def test_switch_from_python_to_javascript(self) -> None:
    """Should be able to switch between languages."""
    input_bar = InputBar(language="python")
    assert input_bar.language == "python"

    input_bar.language = "javascript"
    assert input_bar.language == "javascript"

  def test_switch_from_python_to_none(self) -> None:
    """Should be able to disable highlighting by setting language to None."""
    input_bar = InputBar(language="python")
    assert input_bar.language == "python"

    input_bar.language = None
    assert input_bar.language is None

  def test_language_switch_preserves_text(self) -> None:
    """Switching language should preserve text content."""
    input_bar = InputBar(text="print('hello')", language="python")
    assert input_bar.text == "print('hello')"
    assert input_bar.language == "python"

    input_bar.language = "javascript"
    assert input_bar.text == "print('hello')"
    assert input_bar.language == "javascript"

  def test_language_switch_resets_cursor(self) -> None:
    """Switching language resets cursor to start (TextArea behavior)."""
    input_bar = InputBar(text="hello world", language="python")
    # Set cursor to middle of text
    input_bar.cursor_location = (0, 5)
    assert input_bar.cursor_location == (0, 5)

    # TextArea resets cursor when language changes
    input_bar.language = "javascript"
    assert input_bar.cursor_location == (0, 0)


class TestInputBarThemeLanguageIntegration:
  """Integration tests for theme and language parameters."""

  def test_theme_and_language_together(self) -> None:
    """InputBar should accept both theme and language parameters."""
    input_bar = InputBar(
      text="def hello(): pass",
      theme="vscode_dark",
      language="python",
    )
    assert input_bar.text == "def hello(): pass"
    assert input_bar.theme == "vscode_dark"
    assert input_bar.language == "python"

  def test_theme_and_language_with_other_params(self) -> None:
    """Theme and language should work with other parameters."""
    input_bar = InputBar(
      text="test",
      theme="dracula",
      language="json",
      name="test_input",
      id="input-id",
      classes="custom-class",
    )
    assert input_bar.text == "test"
    assert input_bar.theme == "dracula"
    assert input_bar.language == "json"
    assert input_bar._name == "test_input"
    assert input_bar.id == "input-id"
    assert input_bar.classes == {"custom-class"}

  async def test_language_in_mounted_app(self) -> None:
    """Language should work when InputBar is mounted in an App."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(language="python", text="def test(): pass")

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language == "python"
      assert input_bar.text == "def test(): pass"

  async def test_theme_in_mounted_app(self) -> None:
    """Theme should work when InputBar is mounted in an App."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(theme="github_light")

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.theme == "github_light"

  async def test_language_switch_in_mounted_app(self) -> None:
    """Language switching should work in a mounted App."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(language="python")

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language == "python"

      input_bar.language = "javascript"
      assert input_bar.language == "javascript"


class TestInputBarSyntaxHighlighting:
  """Tests for syntax highlighting behavior."""

  async def test_python_code_highlighting_active(self) -> None:
    """Python code should have syntax highlighting when language is set."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(language="python", text="def hello(): pass")

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      # The TextArea widget should have highlighting enabled
      assert input_bar.language == "python"
      assert input_bar.text == "def hello(): pass"

  async def test_no_highlighting_when_language_none(self) -> None:
    """No highlighting should be active when language is None."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(language=None, text="plain text without highlighting")

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language is None
      assert input_bar.text == "plain text without highlighting"

  async def test_markdown_highlighting(self) -> None:
    """Markdown should have syntax highlighting when language is set."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(
          language="markdown",
          text="# Header\n\n**bold** text",
        )

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language == "markdown"
      assert input_bar.text == "# Header\n\n**bold** text"

  async def test_json_highlighting(self) -> None:
    """JSON should have syntax highlighting when language is set."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(
          language="json",
          text='{"key": "value", "number": 42}',
        )

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language == "json"
      assert input_bar.text == '{"key": "value", "number": 42}'

  async def test_javascript_highlighting(self) -> None:
    """JavaScript should have syntax highlighting when language is set."""

    class TestApp(App[None]):
      def compose(self) -> ComposeResult:
        yield InputBar(
          language="javascript",
          text="const x = () => console.log('hello');",
        )

    async with TestApp().run_test() as pilot:
      input_bar = pilot.app.query_one(InputBar)
      assert input_bar.language == "javascript"
      assert input_bar.text == "const x = () => console.log('hello');"
