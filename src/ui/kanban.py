"""Kanban board renderer."""

from __future__ import annotations

import re

from . import box
from ..backlog.model import Status, Backlog
from ..project.model import Project

STATUSES = [Status.TODO, Status.INPROGRESS, Status.REVIEW, Status.DONE]
LABELS   = ['TODO', 'INPROGRESS', 'REVIEW', 'DONE']
BOLD = '\033[1m'
RESET = '\033[0m'
ID_COLOR = '\033[38;2;108;123;202m'
SESSION_COLOR = '\033[38;2;241;205;97m'

# Per column: at most this many cards on the board; remainder shown as "+N more".
K_MAX_VISIBLE_CARDS = 10

# K_BOARD_TOTAL: total character width of the kanban board (= k_top() length)
# = 2 corners + K_NC * K_COL_TOTAL dashes + (K_NC-1) junctions
_K_BOARD_TOTAL  = 2 + box.K_COL_TOTAL * box.K_NC + (box.K_NC - 1)  # 93
_CMD_H_INNER    = _K_BOARD_TOTAL - 2   # dashes between corners = 91
_CMD_CONTENT    = _CMD_H_INNER - 2     # content between '│ ' and ' │' = 89


def render_kanban(
    project: Project,
    board: dict[Status, list[Backlog]],
) -> None:
    _render_project_label(project)
    _render_board(board)
    _render_command_bar()
    print()


def render_kanban_prompt() -> str:
    try:
        return input('❯ ').strip()
    except (EOFError, KeyboardInterrupt):
        return 'b'


def _render_project_label(project: Project) -> None:
    print(f'[ Project: {project.name} ]')


def _render_board(board: dict[Status, list[Backlog]]) -> None:
    print(box.k_top())
    print(box.k_row([f'{BOLD}{label}{RESET}' for label in LABELS]))
    print(box.k_header_divider())

    col_lengths = [len(board[s]) for s in STATUSES]
    max_slots = max(col_lengths, default=0)
    visible_rows = min(max_slots, K_MAX_VISIBLE_CARDS) if max_slots else 0

    print(box.k_row([''] * box.K_NC))  # top padding

    if max_slots == 0:
        print(box.k_row(['  (no backlogs)'] + [''] * (box.K_NC - 1)))
        print(box.k_row([''] * box.K_NC))
    else:
        for i in range(visible_rows):
            title_cells: list[str] = []
            session_cells: list[str] = []
            for status in STATUSES:
                items = board[status]
                if i < len(items):
                    b = items[i]
                    colored_id = f'[{ID_COLOR}{b.id}{RESET}]'
                    styled_title = f'{BOLD}{b.title}{RESET}'
                    title_cells.append(f'{colored_id} {styled_title}')
                    session_text = _format_session(b.session_start, b.session_end)
                    colored_session = f'{SESSION_COLOR}{session_text}{RESET}' if session_text else ''
                    session_cells.append(colored_session)
                else:
                    title_cells.append('')
                    session_cells.append('')
            print(box.k_row(title_cells))
            print(box.k_row(session_cells))
            if i < visible_rows - 1:
                print(box.k_row([''] * box.K_NC))

        if max_slots > K_MAX_VISIBLE_CARDS:
            more_cells: list[str] = []
            for status in STATUSES:
                n = len(board[status])
                extra = n - K_MAX_VISIBLE_CARDS
                more_cells.append(f'+{extra} more' if extra > 0 else '')
            print(box.k_row([''] * box.K_NC))
            print(box.k_row(more_cells))

        print(box.k_row([''] * box.K_NC))  # bottom padding

    print(box.k_bottom())


def _render_command_bar() -> None:
    title = ' Commands '
    top_line = box.TL + box.H * 4 + title + box.H * (_CMD_H_INNER - 4 - len(title)) + box.TR

    left = '[opt] Options     [sort] Todo order'
    right = '[B] Back'
    gap = _CMD_CONTENT - box.display_width(left) - box.display_width(right)
    row = left + ' ' * max(1, gap) + right

    print(top_line)
    print(box.V + ' ' + ' ' * _CMD_CONTENT + ' ' + box.V)
    print(box.V + ' ' + row + ' ' + box.V)
    print(box.V + ' ' + ' ' * _CMD_CONTENT + ' ' + box.V)
    print(box.BL + box.H * _CMD_H_INNER + box.BR)


def _format_session(start: str, end: str) -> str:
    if not start and not end:
        return ''
    return f'{_shorten_date(start)} ~ {_shorten_date(end)}'


def _shorten_date(value: str) -> str:
    """Convert YYYY-MM-DD(...) to MM/DD, otherwise return as-is (truncated)."""
    m = re.match(r'\d{4}[-/](\d{2})[-/](\d{2})', value)
    if m:
        return f'{m.group(1)}/{m.group(2)}'
    return value[:5] if len(value) > 5 else value
