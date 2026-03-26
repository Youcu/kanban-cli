"""Terminal screen control."""

from __future__ import annotations

import os


def clear_screen() -> None:
    """Clear the terminal (best-effort for common macOS / Linux / Windows shells)."""
    if os.name == 'nt':
        os.system('cls')
    else:
        print('\033[2J\033[H', end='', flush=True)
