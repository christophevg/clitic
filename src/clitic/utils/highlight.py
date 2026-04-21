"""Theme mapping utilities for syntax highlighting.

This module provides functions to map Textual app themes to Pygments themes
for consistent syntax highlighting across different color schemes.
"""

THEME_MAP: dict[str | None, str] = {
  None: "monokai",
  "dark": "monokai",
  "light": "github-light",
}


def get_pygments_theme(app_theme: str | None) -> str:
  """Get the Pygments theme for a given app theme.

  Args:
    app_theme: The Textual app theme name, or None for default.

  Returns:
    The corresponding Pygments theme name.
  """
  if app_theme in THEME_MAP:
    return THEME_MAP[app_theme]
  # Default fallback for unknown themes
  return "monokai"
