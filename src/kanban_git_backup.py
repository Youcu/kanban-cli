"""Git backup for ~/.kanban when it is a Git working tree."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

KANBAN_ROOT = Path.home() / '.kanban'


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', '-C', str(root), *args],
        capture_output=True,
        text=True,
    )


def _is_git_managed(root: Path) -> bool:
    if not root.is_dir():
        return False
    p = _git(root, 'rev-parse', '--is-inside-work-tree')
    return p.returncode == 0 and p.stdout.strip() == 'true'


def run_git_backup() -> str:
    """Run git add/commit/push under ~/.kanban. Returns one-line feedback."""
    root = KANBAN_ROOT
    if not _is_git_managed(root):
        return 'Backup skipped: ~/.kanban is not a git repository.'

    try:
        r_add = _git(root, 'add', '.')
    except FileNotFoundError:
        return 'Backup failed: git not found in PATH.'
    if r_add.returncode != 0:
        err = (r_add.stderr or r_add.stdout or '').strip()
        return f'git add failed: {err or r_add.returncode}'

    stamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    try:
        r_commit = _git(root, 'commit', '-m', stamp)
    except FileNotFoundError:
        return 'Backup failed: git not found in PATH.'

    commit_out = ((r_commit.stderr or '') + (r_commit.stdout or '')).lower()
    if r_commit.returncode != 0:
        if 'nothing to commit' in commit_out and 'working tree clean' in commit_out:
            commit_summary = 'no changes to commit'
        else:
            err = (r_commit.stderr or r_commit.stdout or '').strip()
            return f'git commit failed: {err or r_commit.returncode}'
    else:
        commit_summary = f'commit {stamp}'

    try:
        r_push = _git(root, 'push')
    except FileNotFoundError:
        return 'Backup failed: git not found in PATH.'
    if r_push.returncode != 0:
        err = (r_push.stderr or r_push.stdout or '').strip()
        return f'git push failed: {err or r_push.returncode}'

    return f'Backup complete ({commit_summary}, pushed).'
