"""One-line formatting for backlog pick lists inside box menus."""

from __future__ import annotations

from . import box
from ..backlog.model import Backlog


def format_pick_line(item_no: int, b: Backlog, *, session_text: str) -> str:
    """Single box row: ``[n] [id] title  session`` with title truncated to fit INNER_WIDTH."""
    prefix = f'  [{item_no}]  [{b.id}] '
    spacer = '  '
    tail = f'{spacer}{session_text}'
    budget = box.INNER_WIDTH - box.display_width(prefix) - box.display_width(tail)
    title = b.title
    if budget < 1:
        budget = 1
    if box.display_width(title) > budget:
        title = box.truncate_to_width(title, budget)
    return f'{prefix}{title}{tail}'
