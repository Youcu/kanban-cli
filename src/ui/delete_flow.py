"""CLI flow for deleting a backlog."""

from __future__ import annotations

import re

from . import backlog_list_line, box
from ..backlog.model import Status, Backlog
from ..backlog.parser import parse_file
from ..project.model import Project

STATUS_LIST  = [Status.TODO, Status.INPROGRESS, Status.REVIEW, Status.DONE]
STATUS_LABEL = ['Todo', 'Inprogress', 'Review', 'Done']

_STATUS_GRID = [
    '  [0] Todo         [1] Inprogress',
    '  [2] Review       [3] Done',
]

_TITLE_MAX_CONFIRM = 36


# ── Public entry point ────────────────────────────────────────────────────

def run_delete_flow(project: Project) -> str | None:
    """Run backlog delete flow. Returns feedback message or None if cancelled."""
    print()

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

    confirmed = _prompt_confirm(backlog)
    if not confirmed:
        return 'Delete cancelled.'

    if not backlog.path.exists():
        return f'File not found: {backlog.path.name}'

    backlog.path.unlink()
    return f'[{backlog.id}] "{_trunc(backlog.title, 30)}" deleted.'


# ── Steps ─────────────────────────────────────────────────────────────────

def _prompt_status() -> int | None:
    while True:
        _render_box('Delete Backlog — Select Status', [
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


def _prompt_confirm(backlog: Backlog) -> bool:
    title_line = f'  [{backlog.id}] {_trunc(backlog.title, _TITLE_MAX_CONFIRM)}'
    session_line = f'  {_fmt_session(backlog.session_start, backlog.session_end)}'

    _render_box('Confirm Delete', [
        '',
        title_line,
        session_line,
        '',
        '  This cannot be undone.',
        '',
        '    [Y] Confirm         [N] Cancel',
        '',
    ])

    while True:
        raw = _input()
        if raw is None:
            return False
        v = raw.strip().lower()
        if v == 'y':
            return True
        if v in ('n', ''):
            return False
        _error('Enter Y or N.')


# ── File loader ───────────────────────────────────────────────────────────

def _load_all(project: Project, status: Status) -> list[Backlog]:
    dir_path = project.path / status.value
    if not dir_path.exists():
        return []
    files = sorted(dir_path.glob('*_backlog.md'))
    return [b for f in files if (b := parse_file(f, status)) is not None]


# ── UI helpers ────────────────────────────────────────────────────────────

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
    return f'{m.group(1)}/{m.group(2)}' if m else (value[:5] if len(value) > 5 else value)
