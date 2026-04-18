"""Exception hierarchy for clitic package.

This module defines all custom exceptions used throughout the clitic package.
All exceptions inherit from CliticError for easy catching of package-specific
errors.
"""


class CliticError(Exception):
    """Base exception for all clitic errors.

    All custom exceptions in the clitic package inherit from this class,
    allowing users to catch all package-specific errors with a single
    except clause.

    Example:
        try:
            # clitic operations
            pass
        except CliticError as e:
            # Handle any clitic-specific error
            print(f"Clitic error: {e}")
    """

    pass


class PluginError(CliticError):
    """Exception for plugin-related issues.

    Raised when a plugin fails to load, initialize, or execute properly.

    Attributes:
        plugin_name: The name of the plugin that encountered the error.
        operation: The operation that failed (e.g., 'load', 'initialize').

    Example:
        raise PluginError(
            plugin_name="MarkdownRenderer",
            operation="initialize",
            message="Failed to parse configuration"
        )
    """

    def __init__(
        self,
        plugin_name: str,
        operation: str,
        message: str | None = None,
    ) -> None:
        """Initialize PluginError.

        Args:
            plugin_name: Name of the plugin that encountered the error.
            operation: The operation that failed.
            message: Optional additional context for the error.
        """
        self.plugin_name = plugin_name
        self.operation = operation
        self._message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        """Format the error message with plugin context."""
        base = f"Plugin '{self.plugin_name}' failed during {self.operation}"
        if self._message:
            return f"{base}: {self._message}"
        return f"{base}."

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return (
            f"PluginError(plugin_name={self.plugin_name!r}, "
            f"operation={self.operation!r}, message={self._message!r})"
        )


class ConfigurationError(CliticError):
    """Exception for configuration-related issues.

    Raised when a configuration setting is invalid, missing, or malformed.

    Attributes:
        setting: The name of the configuration setting.
        expected: Optional description of expected format or values.

    Example:
        raise ConfigurationError(
            setting="theme",
            expected="one of: 'dark', 'light', 'custom'",
            message="Invalid theme name 'unknown'"
        )
    """

    def __init__(
        self,
        setting: str,
        expected: str | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize ConfigurationError.

        Args:
            setting: Name of the configuration setting with the issue.
            expected: Optional description of expected format or values.
            message: Optional additional context for the error.
        """
        self.setting = setting
        self.expected = expected
        self._message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        """Format the error message with configuration context."""
        parts = [f"Configuration error for setting '{self.setting}'"]
        if self._message:
            parts.append(f": {self._message}")
        elif self.expected:
            parts.append(f". Expected {self.expected}")
        else:
            parts.append(".")
        return "".join(parts)

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return (
            f"ConfigurationError(setting={self.setting!r}, "
            f"expected={self.expected!r}, message={self._message!r})"
        )


class RenderError(CliticError):
    """Exception for content rendering failures.

    Raised when a renderer fails to process or display content.

    Attributes:
        content_type: The type of content being rendered (e.g., 'markdown').
        renderer: The name of the renderer that failed.

    Example:
        raise RenderError(
            content_type="markdown",
            renderer="MarkdownRenderer",
            message="Failed to parse table syntax at line 42"
        )
    """

    def __init__(
        self,
        content_type: str,
        renderer: str,
        message: str | None = None,
    ) -> None:
        """Initialize RenderError.

        Args:
            content_type: Type of content being rendered.
            renderer: Name of the renderer that failed.
            message: Optional additional context for the error.
        """
        self.content_type = content_type
        self.renderer = renderer
        self._message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        """Format the error message with renderer context."""
        base = f"Renderer '{self.renderer}' failed for content type '{self.content_type}'"
        if self._message:
            return f"{base}: {self._message}"
        return f"{base}."

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return (
            f"RenderError(content_type={self.content_type!r}, "
            f"renderer={self.renderer!r}, message={self._message!r})"
        )


class SessionError(CliticError):
    """Exception for session-related issues.

    Raised when a session operation fails (start, save, resume, delete).

    Attributes:
        session_id: The session ID involved in the error (if applicable).
        operation: The operation that failed (e.g., 'start', 'save', 'resume').

    Example:
        raise SessionError(
            session_id="abc-123",
            operation="resume",
            message="Session file not found"
        )
    """

    def __init__(
        self,
        session_id: str | None = None,
        operation: str = "unknown",
        message: str | None = None,
    ) -> None:
        """Initialize SessionError.

        Args:
            session_id: Optional session ID involved in the error.
            operation: The operation that failed.
            message: Optional additional context for the error.
        """
        self.session_id = session_id
        self.operation = operation
        self._message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        """Format the error message with session context."""
        base = f"Session error during {self.operation}"
        if self.session_id:
            base = f"{base} for session '{self.session_id}'"
        if self._message:
            return f"{base}: {self._message}"
        return f"{base}."

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        return (
            f"SessionError(session_id={self.session_id!r}, "
            f"operation={self.operation!r}, message={self._message!r})"
        )
