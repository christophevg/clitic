"""
clitic - Executable showcase application.

This module provides a working application that demonstrates all
currently implemented features of the clitic package.

Run with:
    python -m clitic
    # or
    make showcase
"""

from clitic import App, __version__


def main() -> None:
  """Run the clitic showcase application."""
  print("=" * 60)
  print("clitic - Rich CLI Application Framework")
  print("=" * 60)
  print()
  print(f"Version: {__version__}")
  print()
  print("This showcase demonstrates all implemented features.")
  print()
  print("Currently implemented:")
  print("  [✓] Package structure")
  print("  [✓] Version information")
  print("  [✓] Executable module")
  print("  [✓] Core App class with plugin management")
  print("  [✓] on_submit decorator for input handling")
  print()
  print("Demonstrating App class:")
  print("-" * 40)

  # Create a simple app instance
  app = App(title="clitic Showcase", theme_name="dark")
  print(f"  Created App with title: {app.title}")
  print(f"  Theme: {app.theme_name}")

  # Demonstrate on_submit decorator
  messages_received: list[str] = []

  @app.on_submit
  def handle_input(text: str) -> None:
    messages_received.append(text)

  # Trigger submit to demonstrate the handler
  app._trigger_submit("Hello from clitic!")
  print(f"  Submit handler received: {messages_received}")

  print()
  print("Coming soon:")
  print("  [ ] InputBar widget")
  print("  [ ] Conversation container")
  print("  [ ] Markdown/Diff/Terminal plugins")
  print("  [ ] History navigation")
  print("  [ ] Completion system")
  print("  [ ] Theme system")
  print()
  print("=" * 60)
  print("Run 'make showcase' or 'python -m clitic' to see updates.")
  print("=" * 60)


if __name__ == "__main__":
  main()
