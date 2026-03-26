"""Todo column sort mode prompt (kanban)."""

from __future__ import annotations

from . import box
from ..backlog.repository import TodoSortMode


def prompt_todo_sort(current: TodoSortMode) -> TodoSortMode | None:
    """Return selected mode, or None to keep the current mode (cancel)."""
    cur = (
        '생성일 · 오래된 항목 먼저'
        if current == TodoSortMode.CREATION
        else 'D-Day · Session End 임박 순'
    )
    print(box.top('Todo column order'))
    print(box.empty_row())
    print(box.row(f'  Current: {cur}'))
    print(box.empty_row())
    print(box.row('    [1] 생성일 순 (파일 생성 시각)'))
    print(box.row('    [2] D-Day 순 (Session End 임박, 없음 맨 뒤)'))
    print(box.empty_row())
    print(box.row('  [B] Cancel'))
    print(box.bottom())
    print()

    while True:
        try:
            raw = input('❯ ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw in ('b', 'back', ''):
            return None
        if raw == '1':
            return TodoSortMode.CREATION
        if raw == '2':
            return TodoSortMode.DDAY
        print('  Enter 1, 2, or B.\n')
