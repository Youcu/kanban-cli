"""CLI flow for moving a backlog between status directories."""

from __future__ import annotations

import re
import shutil

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

_TITLE_MAX_HINT = 26   # "  Moving: [id] " in status prompt (legacy char count)


# ── Public entry point ────────────────────────────────────────────────────

def run_move_flow(project: Project) -> str | None:
    """Run backlog move flow. Returns feedback message or None if cancelled."""
    print()

    source_idx = _prompt_status('Move Backlog — Source Status', exclude_idx=None)
    if source_idx is None:
        return None
    source = STATUS_LIST[source_idx]

    backlogs = _load_all(project, source)
    if not backlogs:
        return f'No backlogs in {STATUS_LABEL[source_idx]}.'

    backlog = _prompt_backlog(backlogs, STATUS_LABEL[source_idx])
    if backlog is None:
        return None

    target_idx = _prompt_status(
        'Target Status',
        exclude_idx=source_idx,
        hint=f'  Moving: [{backlog.id}] {_trunc(backlog.title, _TITLE_MAX_HINT)}',
    )
    if target_idx is None:
        return None
    target = STATUS_LIST[target_idx]

    error = _do_move(backlog, target, project)
    if error:
        return f'Move failed: {error}'

    return (
        f'[{backlog.id}] "{_trunc(backlog.title, 30)}" moved: '
        f'{STATUS_LABEL[source_idx]} → {STATUS_LABEL[target_idx]}'
    )


# ── Steps ─────────────────────────────────────────────────────────────────

def _prompt_status(title: str, exclude_idx: int | None, hint: str = '') -> int | None:
    while True:
        lines: list[str] = []
        if hint:
            lines += [hint, '']
        lines += ['  Select status:', ''] + _STATUS_GRID + ['', '  Ctrl+C to cancel']
        _render_box(title, lines)

        raw = _input()
        if raw is None:
            return None
        if not raw.isdigit() or int(raw) not in range(4):
            _error('Enter 0, 1, 2, or 3.')
            continue
        idx = int(raw)
        if idx == exclude_idx:
            _error(f'Target must differ from source ({STATUS_LABEL[exclude_idx]}).')
            continue
        return idx


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


# ── File operation ────────────────────────────────────────────────────────

def _do_move(backlog: Backlog, target: Status, project: Project) -> str | None:
    """Move file to target directory. Returns error string or None on success."""
    if not backlog.path.exists():
        return f'File not found: {backlog.path.name}'

    target_dir = project.path / target.value
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / backlog.path.name

    if dest.exists():
        return f'{backlog.path.name} already exists in {target.value}.'

    shutil.move(str(backlog.path), str(dest))
    return None


# ── Loaders ───────────────────────────────────────────────────────────────

def _load_all(project: Project, status: Status) -> list[Backlog]:
    """Load all backlogs from a status directory without any date filter."""
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
