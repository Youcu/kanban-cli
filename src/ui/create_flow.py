"""CLI flow for backlog creation — edit new file in vi only."""

from __future__ import annotations

from ..backlog import creator, validator
from ..backlog.model import Status
from ..backlog.parser import parse_file
from ..project.model import Project
from . import external_tools


def run_create_flow(project: Project) -> str | None:
    """Create an empty General backlog and complete it in vi."""
    print()

    if not external_tools.vi_binary():
        print('  ✗ vi not found in PATH. Install a vi-compatible editor (e.g. vim).')
        print()
        return 'Backlog not created.'

    path = creator.create_backlog(project, 'G', '', '', '', {})
    bid = path.stem.replace('_backlog', '')

    print('  New backlog opened in vi — set # Title, # Session (Start / End), then save & quit.')
    print()

    while True:
        if not external_tools.run_vi(path):
            path.unlink(missing_ok=True)
            return 'Backlog not created.'

        backlog = parse_file(path, Status.TODO)
        if backlog is None:
            print('  ✗ Could not read the file after editing.')
            print()
            if not _offer_vi_again(path, delete_on_quit=True):
                return 'Backlog not created.'
            continue

        title = '' if backlog.title == '(no title)' else backlog.title
        errs = validator.validate_mandatory(title, backlog.session_start, backlog.session_end)
        if not errs:
            return f'Backlog [{bid}] "{title}" created in Todo.'

        print()
        for e in errs:
            print(f'  ✗ {e.message}')
        print()
        if not _offer_vi_again(path, delete_on_quit=True):
            return 'Backlog not created.'


def _offer_vi_again(path, *, delete_on_quit: bool) -> bool:
    """True = run vi again; False = stop (and delete file if delete_on_quit)."""
    while True:
        try:
            raw = input('  [Enter] vi again   [Q] quit > ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            if delete_on_quit:
                path.unlink(missing_ok=True)
            return False
        if raw in ('q', 'quit'):
            if delete_on_quit:
                path.unlink(missing_ok=True)
            return False
        if raw == '':
            return True
        print('  Press Enter or Q.\n')
