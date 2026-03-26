"""CLI flow for editing a backlog in vi."""

from __future__ import annotations

import re

from . import backlog_list_line, box
from ..backlog import validator
from ..backlog.model import Status, Backlog
from ..backlog.parser import parse_file
from ..project.model import Project
from . import external_tools

STATUS_LIST = [Status.TODO, Status.INPROGRESS, Status.REVIEW, Status.DONE]
STATUS_LABEL = ['Todo', 'Inprogress', 'Review', 'Done']

_STATUS_GRID = [
    '  [0] Todo         [1] Inprogress',
    '  [2] Review       [3] Done',
]


def run_edit_flow(project: Project) -> str | None:
    """Open the backlog in vi until Title and Session validate."""
    print()

    if not external_tools.vi_binary():
        print('  ✗ vi not found in PATH. Install a vi-compatible editor (e.g. vim).')
        print()
        return None

    status_idx = _prompt_status()
    if status_idx is None:
        return None
    status = STATUS_LIST[status_idx]

    backlogs = _load_all(project, status)
    if not backlogs:
        return f'No backlogs in {STATUS_LABEL[status_idx]}.'

    backlog = _prompt_backlog(backlogs, STATUS_LABEL[status_idx])
    if backlog is None:
        return None

    path = backlog.path
    if not path.exists():
        return f'File not found: {path.name}'

    print()
    print('  Edit in vi — save & quit when done. (Title and Session Start/End are required.)')
    print()

    while True:
        if not external_tools.run_vi(path):
            return None

        refreshed = parse_file(path, status)
        if refreshed is None:
            print('  ✗ Could not read the file after editing.')
            print()
            if not _offer_vi_again():
                return 'Edit finished — file could not be validated.'
            continue

        title = '' if refreshed.title == '(no title)' else refreshed.title
        errs = validator.validate_mandatory(title, refreshed.session_start, refreshed.session_end)
        if not errs:
            return f'[{refreshed.id}] "{_trunc(title, 40)}" updated.'

        print()
        for e in errs:
            print(f'  ✗ {e.message}')
        print()
        if not _offer_vi_again():
            return 'File saved, but Title/Session still invalid — fix later in vi.'


def _offer_vi_again() -> bool:
    while True:
        try:
            raw = input('  [Enter] vi again   [Q] stop > ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        if raw in ('q', 'quit'):
            return False
        if raw == '':
            return True
        print('  Press Enter or Q.\n')


def _prompt_status() -> int | None:
    while True:
        _render_box('Edit Backlog — Select Status', [
            '  Select status:',
            '',
            *_STATUS_GRID,
            '',
            '  Ctrl+C to cancel',
        ])
        raw = _input()
        if raw is None:
            return None
        if not raw.isdigit() or int(raw) not in range(4):
            _error('Enter 0, 1, 2, or 3.')
            continue
        return int(raw)


def _prompt_backlog(backlogs: list[Backlog], status_label: str) -> Backlog | None:
    while True:
        lines: list[str] = ['']
        for i, b in enumerate(backlogs, start=1):
            lines.append(
                backlog_list_line.format_pick_line(
                    i, b, session_text=_fmt_session(b.session_start, b.session_end)
                )
            )
            lines.append('')
        lines.append('  Ctrl+C to cancel')

        _render_box(f'Backlogs in {status_label}', lines)

        raw = _input()
        if raw is None:
            return None
        if not raw.isdigit():
            _error(f'Enter a number between 1 and {len(backlogs)}.')
            continue
        idx = int(raw) - 1
        if not (0 <= idx < len(backlogs)):
            _error(f'Enter a number between 1 and {len(backlogs)}.')
            continue
        return backlogs[idx]


def _load_all(project: Project, status: Status) -> list[Backlog]:
    dir_path = project.path / status.value
    if not dir_path.exists():
        return []
    files = sorted(dir_path.glob('*_backlog.md'))
    return [b for f in files if (b := parse_file(f, status)) is not None]


def _render_box(title: str, lines: list[str]) -> None:
    print(box.top(title))
    if not lines or lines[0] != '':
        print(box.empty_row())
    for line in lines:
        print(box.row(line))
    if not lines or lines[-1] != '':
        print(box.empty_row())
    print(box.bottom())
    print()


def _input() -> str | None:
    try:
        return input('❯ ').strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def _error(msg: str) -> None:
    print(f'  ✗ {msg}')
    print()


def _trunc(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[:max_len - 1] + '…'


def _fmt_session(start: str, end: str) -> str:
    if not start and not end:
        return '(no session)'
    return f'{_short_date(start)} ~ {_short_date(end)}'


def _short_date(value: str) -> str:
    m = re.match(r'\d{4}[-/](\d{2})[-/](\d{2})', value)
    return f'{m.group(1)}/{m.group(2)}' if m else (value[:10] if value else '')
