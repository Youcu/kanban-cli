"""One-line formatting for backlog pick lists inside box menus."""

from __future__ import annotations

from . import box
from ..backlog.model import Backlog

BOLD = '\033[1m'
RESET = '\033[0m'
ID_COLOR = '\033[38;2;108;123;202m'
SESSION_COLOR = '\033[38;2;241;205;97m'


def format_pick_line(item_no: int, b: Backlog, *, session_text: str) -> str:
    """Single box row: ``[n] [id] title  session`` with title truncated to fit INNER_WIDTH."""
    colored_id = f'[{ID_COLOR}{b.id}{RESET}]'
    prefix = f'  [{item_no}]  {colored_id} '
    spacer = '  '
    tail = f'{spacer}{SESSION_COLOR}{session_text}{RESET}' if session_text else ''
    budget = box.INNER_WIDTH - box.display_width(prefix) - box.display_width(tail)
    title = f'{BOLD}{b.title}{RESET}'
    if budget < 1:
        budget = 1
    if box.display_width(title) > budget:
        title = box.truncate_to_width(title, budget)
    return f'{prefix}{title}{tail}'
