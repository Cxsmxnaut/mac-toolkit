"""Console utilities for Rich terminal UI."""

from rich.console import Console
from rich.theme import Theme
from typing import Optional


# Custom theme for Mac Toolkit
THEME = Theme({
    "pass": "green",
    "warning": "yellow",
    "fail": "red",
    "info": "cyan",
    "title": "bold blue",
    "header": "bold white",
    "key": "bold cyan",
    "value": "white"
})


class ToolkitConsole:
    """Enhanced console with pre-configured Rich settings."""
    
    def __init__(self, theme: Optional[Theme] = None):
        """Initialize the console with custom theme.
        
        Args:
            theme: Optional custom Rich theme
        """
        self.console = Console(theme=theme or THEME)
    
    def print(self, *args, **kwargs) -> None:
        """Print to console."""
        self.console.print(*args, **kwargs)
    
    def print_success(self, message: str) -> None:
        """Print success message in green."""
        self.console.print(f"[pass]✓[/pass] {message}")
    
    def print_warning(self, message: str) -> None:
        """Print warning message in yellow."""
        self.console.print(f"[warning]⚠[/warning] {message}")
    
    def print_error(self, message: str) -> None:
        """Print error message in red."""
        self.console.print(f"[fail]✗[/fail] {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message in cyan."""
        self.console.print(f"[info]ℹ[/info] {message}")
    
    def print_header(self, message: str) -> None:
        """Print header message."""
        self.console.print(f"[header]{message}[/header]")
    
    def print_title(self, message: str) -> None:
        """Print title message."""
        self.console.print(f"[title]{message}[/title]")
    
    def print_key_value(self, key: str, value: str) -> None:
        """Print key-value pair."""
        self.console.print(f"[key]{key}:[/key] {value}")
    
    def clear(self) -> None:
        """Clear the console screen."""
        self.console.clear()


# Global console instance
_console_instance: Optional[ToolkitConsole] = None


def get_console() -> ToolkitConsole:
    """Get or create the global console instance.
    
    Returns:
        ToolkitConsole instance
    """
    global _console_instance
    if _console_instance is None:
        _console_instance = ToolkitConsole()
    return _console_instance


# Backward compatibility - expose console directly
console = get_console().console
