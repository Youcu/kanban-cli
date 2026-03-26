"""One-line formatting for backlog pick lists inside box menus."""

from __future__ import annotations

from . import box
from ..backlog.model import Backlog

BOLD = '\033[1m'
RESET = '\033[0m'
ID_COLOR = '\033[38;2;108;123;202m'
SESSION_COLOR = '\033[38;2;241;205;97m'
RED = '\033[38;2;234;84;85m'


def format_pick_line(item_no: int, b: Backlog, *, session_text: str, dday_text: str = '') -> str:
    """Single box row: ``[n] [id] title  session`` with title truncated to fit INNER_WIDTH."""
    colored_id = f'[{ID_COLOR}{b.id}{RESET}]'
    prefix = f'  [{item_no}]  {colored_id} '
    spacer = '  '
    session_part = f'{SESSION_COLOR}{session_text}{RESET}' if session_text else ''
    dday_part = f' | {RED}{dday_text}{RESET}' if dday_text else ''
    tail = f'{spacer}{session_part}{dday_part}' if (session_part or dday_part) else ''
    budget = box.INNER_WIDTH - box.display_width(prefix) - box.display_width(tail)
    title = f'{BOLD}{b.title}{RESET}'
    if budget < 1:
        budget = 1
    if box.display_width(title) > budget:
        title = box.truncate_to_width(title, budget)
    return f'{prefix}{title}{tail}'
