"""External CLI helpers: vi (required for edit flows), glow (optional for markdown)."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path


VI_COMMAND = 'vi'


def vi_binary() -> str | None:
    return shutil.which(VI_COMMAND)


def run_vi(path: Path) -> bool:
    """Open path in vi. Returns False if vi is not available."""
    vi = vi_binary()
    if not vi:
        print('  ✗ vi not found in PATH. Install a vi-compatible editor (e.g. vim).')
        print()
        return False
    try:
        subprocess.run([vi, str(path)], check=False)
    except (OSError, FileNotFoundError):
        print(f'  ✗ Could not run {VI_COMMAND}.')
        print()
        return False
    return True


def glow_binary() -> str | None:
    """Resolve glow: GLOW_PATH, PATH, then common macOS / Windows install dirs."""
    override = os.environ.get('GLOW_PATH', '').strip()
    if override and os.path.isfile(override):
        return override

    found = shutil.which('glow')
    if found:
        return found

    if platform.system() == 'Darwin':
        for candidate in ('/opt/homebrew/bin/glow', '/usr/local/bin/glow'):
            if os.path.isfile(candidate):
                return candidate

    if platform.system() == 'Windows':
        profile = os.environ.get('USERPROFILE', '')
        local = os.environ.get('LOCALAPPDATA', '')
        pf = os.environ.get('ProgramFiles', '')
        candidates = [
            Path(profile) / 'scoop' / 'shims' / 'glow.exe' if profile else None,
            Path(local) / 'Microsoft' / 'WinGet' / 'Links' / 'glow.exe' if local else None,
            Path(pf) / 'glow' / 'glow.exe' if pf else None,
        ]
        for p in candidates:
            if p is not None and p.is_file():
                return str(p)

    return None


def run_glow_markdown(md_path: Path, *, executable: str | None = None) -> bool:
    """Render markdown with glow. Returns False if glow cannot be run."""
    glow = executable or glow_binary()
    if not glow:
        return False
    try:
        subprocess.run([glow, str(md_path)], check=False)
    except (OSError, FileNotFoundError):
        return False
    return True
