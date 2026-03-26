"""Load backlogs from project storage."""

from __future__ import annotations

from datetime import date, timedelta
from enum import Enum, auto
from pathlib import Path

from .model import Backlog, Status
from .parser import parse_file
from ..project.model import Project

DONE_HIDE_DAYS = 7


class TodoSortMode(Enum):
    """Todo column only — applied when building the kanban board."""

    CREATION = auto()
    DDAY = auto()


def load_board(
    project: Project,
    *,
    todo_sort: TodoSortMode = TodoSortMode.CREATION,
) -> dict[Status, list[Backlog]]:
    board: dict[Status, list[Backlog]] = {}
    for status in Status:
        dir_path = project.path / status.value
        backlogs = _load_from_dir(dir_path, status)
        if status == Status.TODO:
            backlogs = _sort_todo(backlogs, todo_sort)
        if status == Status.DONE:
            backlogs = _filter_done(backlogs)
        board[status] = backlogs
    return board


def _load_from_dir(dir_path: Path, status: Status) -> list[Backlog]:
    if not dir_path.exists():
        return []
    files = sorted(dir_path.glob('*_backlog.md'))
    return [b for f in files if (b := parse_file(f, status)) is not None]


def _file_created_timestamp(path: Path) -> float:
    try:
        st = path.stat()
    except OSError:
        return 0.0
    return float(getattr(st, 'st_birthtime', st.st_mtime))


def _sort_todo(backlogs: list[Backlog], mode: TodoSortMode) -> list[Backlog]:
    if mode == TodoSortMode.CREATION:
        return sorted(backlogs, key=lambda b: (_file_created_timestamp(b.path), b.id))

    today = date.today()

    def dday_key(b: Backlog) -> tuple:
        if b.end_date is None:
            return (1, 999999, b.id)
        delta = (b.end_date - today).days
        return (0, delta, b.id)

    return sorted(backlogs, key=dday_key)


def _filter_done(backlogs: list[Backlog]) -> list[Backlog]:
    cutoff = date.today() - timedelta(days=DONE_HIDE_DAYS)
    return [
        b for b in backlogs
        if b.end_date is None or b.end_date >= cutoff
    ]
