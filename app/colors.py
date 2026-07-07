"""Color-coded output helpers using colorama (optional feature)."""
from __future__ import annotations

from colorama import Fore, Style, init as colorama_init


colorama_init()


def success(text: str) -> str:
    """Green: successful results."""
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def error(text: str) -> str:
    """Red: errors and failures."""
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def info(text: str) -> str:
    """Cyan: informational output (help, history, status)."""
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"


def warning(text: str) -> str:
    """Yellow: warnings (nothing to undo/redo, unknown commands)."""
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"