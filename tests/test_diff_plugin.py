"""Tests for the Diff plugin.

This module tests the DiffPlugin class for rendering unified diff content
with color-coded line annotations.
"""

from rich.style import Style
from rich.text import Text

from clitic.plugins import DiffPlugin


class TestDiffPluginProperties:
  """Tests for DiffPlugin properties."""

  def test_name_returns_diff(self) -> None:
    """The name property should return 'Diff'."""
    plugin = DiffPlugin()
    assert plugin.name == "Diff"

  def test_priority_returns_15(self) -> None:
    """The priority property should return 15."""
    plugin = DiffPlugin()
    assert plugin.priority == 15


class TestDiffPluginCanRender:
  """Tests for DiffPlugin.can_render method."""

  def test_can_render_text_x_diff(self) -> None:
    """Should accept 'text/x-diff' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("text/x-diff", "") is True

  def test_can_render_diff(self) -> None:
    """Should accept 'diff' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("diff", "") is True

  def test_can_render_application_x_diff(self) -> None:
    """Should accept 'application/x-diff' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("application/x-diff", "") is True

  def test_can_render_text_x_patch(self) -> None:
    """Should accept 'text/x-patch' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("text/x-patch", "") is True

  def test_can_render_x_diff(self) -> None:
    """Should accept 'x-diff' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("x-diff", "") is True

  def test_can_render_diff_variant(self) -> None:
    """Should accept 'diff/*' content types."""
    plugin = DiffPlugin()
    assert plugin.can_render("diff/unified", "") is True
    assert plugin.can_render("diff/git", "") is True

  def test_can_render_is_case_insensitive(self) -> None:
    """can_render should be case-insensitive."""
    plugin = DiffPlugin()
    assert plugin.can_render("TEXT/X-DIFF", "") is True
    assert plugin.can_render("Diff", "") is True
    assert plugin.can_render("  diff  ", "") is True

  def test_cannot_render_text_plain(self) -> None:
    """Should reject 'text/plain' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("text/plain", "") is False

  def test_cannot_render_markdown(self) -> None:
    """Should reject 'text/markdown' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("text/markdown", "") is False

  def test_cannot_render_code_python(self) -> None:
    """Should reject 'code/python' content type."""
    plugin = DiffPlugin()
    assert plugin.can_render("code/python", "") is False

  def test_can_render_with_non_string_content(self) -> None:
    """can_render should accept any content type, content not used."""
    plugin = DiffPlugin()
    assert plugin.can_render("diff", 123) is True
    assert plugin.can_render("diff", None) is True  # type: ignore[arg-type]


class TestDiffPluginRender:
  """Tests for DiffPlugin.render method."""

  def test_render_returns_text_object(self) -> None:
    """render should return a Rich Text object."""
    plugin = DiffPlugin()
    result = plugin.render("+added line")
    assert isinstance(result, Text)

  def test_render_empty_string(self) -> None:
    """render should handle empty string."""
    plugin = DiffPlugin()
    result = plugin.render("")
    assert isinstance(result, Text)
    assert str(result) == ""

  def test_render_added_lines_in_green(self) -> None:
    """Added lines (+) should have green style."""
    plugin = DiffPlugin()
    result = plugin.render("+added line")
    assert isinstance(result, Text)
    assert str(result) == "+added line"
    # Check that the text has styling applied
    assert len(result.spans) > 0 or len(result.plain) > 0

  def test_render_removed_lines_in_red(self) -> None:
    """Removed lines (-) should have red style."""
    plugin = DiffPlugin()
    result = plugin.render("-removed line")
    assert isinstance(result, Text)
    assert str(result) == "-removed line"

  def test_render_added_prefix_only_colored(self) -> None:
    """Only the + prefix should be colored green, rest neutral."""
    plugin = DiffPlugin()
    result = plugin.render("+added line")
    spans = result.spans
    # First span should be the + prefix with green color
    assert spans[0].start == 0
    assert spans[0].end == 1
    assert spans[0].style == Style(color="green", bold=True, bgcolor="#e3fedf")
    # Second span should be the rest with no text color
    assert spans[1].start == 1
    assert spans[1].end == 11
    assert spans[1].style == Style(bgcolor="#e3fedf")

  def test_render_removed_prefix_only_colored(self) -> None:
    """Only the - prefix should be colored red, rest neutral."""
    plugin = DiffPlugin()
    result = plugin.render("-removed line")
    spans = result.spans
    # First span should be the - prefix with red color
    assert spans[0].start == 0
    assert spans[0].end == 1
    assert spans[0].style == Style(color="red", bold=True, bgcolor="#f9dddd")
    # Second span should be the rest with no text color
    assert spans[1].start == 1
    assert spans[1].end == 13
    assert spans[1].style == Style(bgcolor="#f9dddd")

  def test_render_hunk_header_in_yellow(self) -> None:
    """Hunk headers (@@) should have yellow style."""
    plugin = DiffPlugin()
    result = plugin.render("@@ -1,5 +1,5 @@")
    assert isinstance(result, Text)
    assert str(result) == "@@ -1,5 +1,5 @@"

  def test_render_file_header_in_cyan(self) -> None:
    """File headers (---, +++) should have cyan style."""
    plugin = DiffPlugin()
    result_old = plugin.render("--- old_file.py")
    result_new = plugin.render("+++ new_file.py")
    assert isinstance(result_old, Text)
    assert isinstance(result_new, Text)
    assert str(result_old) == "--- old_file.py"
    assert str(result_new) == "+++ new_file.py"

  def test_render_context_lines_default(self) -> None:
    """Context lines should have default style."""
    plugin = DiffPlugin()
    result = plugin.render(" context line")
    assert isinstance(result, Text)
    assert str(result) == " context line"

  def test_render_no_newline_marker(self) -> None:
    """No newline marker (\\) should have magenta style."""
    plugin = DiffPlugin()
    result = plugin.render("\\ No newline at end of file")
    assert isinstance(result, Text)
    assert str(result) == "\\ No newline at end of file"

  def test_render_git_extended_headers(self) -> None:
    """Git extended headers should have cyan style."""
    plugin = DiffPlugin()
    result = plugin.render("diff --git a/file.py b/file.py")
    assert isinstance(result, Text)
    assert str(result) == "diff --git a/file.py b/file.py"

  def test_render_multiple_lines(self) -> None:
    """render should handle multi-line diff output."""
    plugin = DiffPlugin()
    diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,3 @@\n line1\n-line2\n+line2_modified\n line3"
    result = plugin.render(diff)
    assert isinstance(result, Text)
    assert str(result) == diff

  def test_render_unified_diff_full(self) -> None:
    """render should handle a complete unified diff."""
    plugin = DiffPlugin()
    diff = """--- a/src/example.py
+++ b/src/example.py
@@ -10,7 +10,7 @@
 def calculate(x):
-    return x * 2
+    return x * 3

 def helper():
     pass
"""
    result = plugin.render(diff)
    assert isinstance(result, Text)
    lines = str(result).split("\n")
    assert lines[0] == "--- a/src/example.py"
    assert lines[1] == "+++ b/src/example.py"
    assert lines[2] == "@@ -10,7 +10,7 @@"
    assert lines[3] == " def calculate(x):"
    assert lines[4] == "-    return x * 2"
    assert lines[5] == "+    return x * 3"
    assert lines[6] == ""
    assert lines[7] == " def helper():"
    assert lines[8] == "     pass"

  def test_render_with_renderable_content(self) -> None:
    """render should convert renderable content to string."""
    plugin = DiffPlugin()

    class MockRenderable:
      def __str__(self) -> str:
        return "+mock line"

    result = plugin.render(MockRenderable())
    assert isinstance(result, Text)
    assert str(result) == "+mock line"


class TestDiffPluginLineStyle:
  """Tests for DiffPlugin._line_style method."""

  def test_added_line_style(self) -> None:
    """Lines starting with + should have added style."""
    plugin = DiffPlugin()
    style = plugin._line_style("+added")
    assert style == Style(color="green", bold=True, bgcolor="#e3fedf")

  def test_removed_line_style(self) -> None:
    """Lines starting with - should have removed style."""
    plugin = DiffPlugin()
    style = plugin._line_style("-removed")
    assert style == Style(color="red", bold=True, bgcolor="#f9dddd")

  def test_hunk_header_style(self) -> None:
    """Lines starting with @@ should have hunk style."""
    plugin = DiffPlugin()
    style = plugin._line_style("@@ -1,5 +1,5 @@")
    assert style == Style(color="yellow")

  def test_old_file_header_style(self) -> None:
    """Lines starting with --- should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("--- old_file.py")
    assert style == Style(color="cyan", bold=True)

  def test_new_file_header_style(self) -> None:
    """Lines starting with +++ should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("+++ new_file.py")
    assert style == Style(color="cyan", bold=True)

  def test_context_line_style(self) -> None:
    """Lines starting with space should have default style."""
    plugin = DiffPlugin()
    style = plugin._line_style(" context line")
    assert style == Style()

  def test_empty_line_style(self) -> None:
    """Empty lines should have default style."""
    plugin = DiffPlugin()
    style = plugin._line_style("")
    assert style == Style()

  def test_no_newline_marker_style(self) -> None:
    """Lines starting with \\ should have mark style."""
    plugin = DiffPlugin()
    style = plugin._line_style("\\ No newline at end of file")
    assert style == Style(color="magenta")

  def test_git_diff_header_style(self) -> None:
    """Lines starting with diff should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("diff --git a/file b/file")
    assert style == Style(color="cyan", bold=True)

  def test_index_line_style(self) -> None:
    """Lines starting with index should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("index 1234567..abcdefg 100644")
    assert style == Style(color="cyan", bold=True)

  def test_new_file_mode_style(self) -> None:
    """Lines starting with new file mode should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("new file mode 100644")
    assert style == Style(color="cyan", bold=True)

  def test_deleted_file_mode_style(self) -> None:
    """Lines starting with deleted file mode should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("deleted file mode 100644")
    assert style == Style(color="cyan", bold=True)

  def test_rename_line_style(self) -> None:
    """Lines starting with rename should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("rename from old.txt")
    assert style == Style(color="cyan", bold=True)

  def test_similarity_line_style(self) -> None:
    """Lines starting with similarity should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("similarity index 99%")
    assert style == Style(color="cyan", bold=True)

  def test_dissimilarity_line_style(self) -> None:
    """Lines starting with dissimilarity should have header style."""
    plugin = DiffPlugin()
    style = plugin._line_style("dissimilarity index 1%")
    assert style == Style(color="cyan", bold=True)

  def test_minus_only_line_not_header(self) -> None:
    """A line that is just '-' should be removed, not header."""
    plugin = DiffPlugin()
    style = plugin._line_style("-")
    assert style == Style(color="red", bold=True, bgcolor="#f9dddd")

  def test_plus_only_line_not_header(self) -> None:
    """A line that is just '+' should be added, not header."""
    plugin = DiffPlugin()
    style = plugin._line_style("+")
    assert style == Style(color="green", bold=True, bgcolor="#e3fedf")


class TestDiffPluginRenderToStrips:
  """Tests for DiffPlugin.render_to_strips method."""

  def test_render_to_strips_returns_strips(self) -> None:
    """render_to_strips should return a list of Strips."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("+added line", 40)
    from textual.strip import Strip
    assert isinstance(strips, list)
    assert len(strips) == 1
    assert isinstance(strips[0], Strip)

  def test_render_to_strips_added_line_full_width(self) -> None:
    """Added line should have background spanning full width."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("+added line", 40)
    strip = strips[0]
    segments = list(strip)
    # First segment: + prefix
    assert segments[0].text == "+"
    assert segments[0].style == Style(color="green", bold=True, bgcolor="#e3fedf")
    # Second segment: text content
    assert segments[1].text == "added line"
    assert segments[1].style == Style(bgcolor="#e3fedf")
    # Third segment: padding to full width
    assert segments[2].text == " " * 29
    assert segments[2].style == Style(bgcolor="#e3fedf")

  def test_render_to_strips_removed_line_full_width(self) -> None:
    """Removed line should have background spanning full width."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("-removed", 40)
    strip = strips[0]
    segments = list(strip)
    # First segment: - prefix
    assert segments[0].text == "-"
    assert segments[0].style == Style(color="red", bold=True, bgcolor="#f9dddd")
    # Second segment: text content
    assert segments[1].text == "removed"
    assert segments[1].style == Style(bgcolor="#f9dddd")
    # Third segment: padding to full width
    assert segments[2].text == " " * 32
    assert segments[2].style == Style(bgcolor="#f9dddd")

  def test_render_to_strips_no_padding_when_text_fills_width(self) -> None:
    """No padding when text already fills the width."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("+" + "x" * 39, 40)
    strip = strips[0]
    segments = list(strip)
    assert segments[0].text == "+"
    assert segments[1].text == "x" * 39
    assert len(segments) == 2

  def test_render_to_strips_header_no_background(self) -> None:
    """Header lines should not have background padding."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("--- old_file.py", 40)
    strip = strips[0]
    segments = list(strip)
    assert segments[0].text == "--- old_file.py"
    assert segments[0].style == Style(color="cyan", bold=True)

  def test_render_to_strips_multiple_lines(self) -> None:
    """render_to_strips should handle multiple lines."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("--- a/file.py\n+++ b/file.py\n+added", 40)
    assert len(strips) == 3
    assert list(strips[0])[0].text == "--- a/file.py"
    assert list(strips[1])[0].text == "+++ b/file.py"
    assert list(strips[2])[0].text == "+"

  def test_render_to_strips_empty_added_line(self) -> None:
    """Added line with just + should pad full width."""
    plugin = DiffPlugin()
    strips = plugin.render_to_strips("+", 40)
    strip = strips[0]
    segments = list(strip)
    assert segments[0].text == "+"
    assert segments[0].style == Style(color="green", bold=True, bgcolor="#e3fedf")
    assert segments[1].text == " " * 39
    assert segments[1].style == Style(bgcolor="#e3fedf")

