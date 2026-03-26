"""CLI flow for viewing a backlog in detail."""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum, auto

from . import backlog_list_line, box
from . import external_tools
from .terminal import clear_screen
from ..backlog.model import Status, Backlog
from ..backlog.parser import parse_file
from ..project.model import Project

STATUS_LIST = [Status.TODO, Status.INPROGRESS, Status.REVIEW, Status.DONE]
STATUS_LABEL = ['Todo', 'Inprogress', 'Review', 'Done']

_STATUS_GRID = [
    '  [0] Todo         [1] Inprogress',
    '  [2] Review       [3] Done',
]
RED = '\033[38;2;234;84;85m'
RESET = '\033[0m'


class ViewFlowResult(Enum):
    """Returned when the user finishes viewing and should return to the Options menu."""

    BACK_TO_OPT_MENU = auto()


def run_view_flow(project: Project) -> str | None | ViewFlowResult:
    """Show one backlog. After content, user presses B to refresh and return to Options."""
    clear_screen()
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

    _render_detail(backlog, STATUS_LABEL[status_idx])
    _wait_back_to_options()
    return ViewFlowResult.BACK_TO_OPT_MENU


def _render_detail(backlog: Backlog, status_label: str) -> None:
    glow = external_tools.glow_binary()
    meta = [
        f'  Status:  {status_label}',
        f'  File:    {backlog.path.name}',
        '',
        f'  Title:   {backlog.title}',
        (
            f'  Session: {_fmt_session(backlog.session_start, backlog.session_end)}'
            f'{_fmt_dday_tag(backlog.session_end)}'
        ),
        '',
    ]
    meta.append(
        '  (markdown below via glow)' if glow else '  ── Document ──────────────────────'
    )

    _render_box(f'Backlog [{backlog.id}]', meta)

    if glow and external_tools.run_glow_markdown(backlog.path, executable=glow):
        print()
    else:
        try:
            body = backlog.path.read_text(encoding='utf-8')
        except OSError:
            body = '  (could not read file)'

        for line in body.splitlines():
            print(f'  {line}')
        print()


def _wait_back_to_options() -> None:
    print('  [B] Back to Options')
    while True:
        try:
            raw = input('❯ ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if raw in ('b', 'back'):
            return
        print('  Press B to return.\n')


def _prompt_status() -> int | None:
    while True:
        _render_box('View Backlog — Select Status', [
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
                    i,
                    b,
                    session_text=_fmt_session(b.session_start, b.session_end),
                    dday_text=_fmt_dday(b.session_end),
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


def _fmt_session(start: str, end: str) -> str:
    if not start and not end:
        return '(no session)'
    return f'{_short_date(start)} ~ {_short_date(end)}'


def _fmt_dday(end: str) -> str:
    target = _parse_date(end)
    if target is None:
        return ''
    delta = (target - date.today()).days
    if delta >= 0:
        return f'D-{delta}'
    return f'D+{abs(delta)}'


def _fmt_dday_tag(end: str) -> str:
    dday = _fmt_dday(end)
    if not dday:
        return ''
    return f' | {RED}{dday}{RESET}'


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(value[:10], fmt).date()
        except ValueError:
            continue
    return None


def _short_date(value: str) -> str:
    m = re.match(r'\d{4}[-/](\d{2})[-/](\d{2})', value)
    return f'{m.group(1)}/{m.group(2)}' if m else (value[:10] if value else '')
