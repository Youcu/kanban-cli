"""Backlog field validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationError:
    field: str
    message: str


def validate_mandatory(title: str, start: str, end: str) -> list[ValidationError]:
    errors: list[ValidationError] = []

    if not title.strip():
        errors.append(ValidationError('Title', 'Title cannot be empty.'))

    start_date = _parse_date(start)
    if not start.strip():
        errors.append(ValidationError('Start', 'Session Start is required.'))
    elif start_date is None:
        errors.append(ValidationError('Start', 'Session Start must be YYYY-MM-DD.'))

    end_date = _parse_date(end)
    if not end.strip():
        errors.append(ValidationError('End', 'Session End is required.'))
    elif end_date is None:
        errors.append(ValidationError('End', 'Session End must be YYYY-MM-DD.'))

    if start_date and end_date and end_date < start_date:
        errors.append(ValidationError('End', 'Session End cannot be before Start.'))

    return errors


def _parse_date(value: str):
    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(value.strip()[:10], fmt).date()
        except ValueError:
            continue
    return None
