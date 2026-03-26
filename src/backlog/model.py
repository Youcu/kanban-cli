from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path


class Status(Enum):
    TODO = 'Todo'
    INPROGRESS = 'Inprogress'
    REVIEW = 'Review'
    DONE = 'Done'


@dataclass
class Backlog:
    id: str
    title: str
    session_start: str
    session_end: str
    end_date: date | None
    status: Status
    path: Path
