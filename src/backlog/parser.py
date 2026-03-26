"""Parse backlog markdown files."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .model import Backlog, Status


def parse_file(path: Path, status: Status) -> Backlog | None:
    try:
        text = path.read_text(encoding='utf-8')
    except OSError:
        return None

    backlog_id = path.stem.replace('_backlog', '')
    title = _extract_section_first_line(text, 'Title') or '(no title)'
    session_start = _extract_session_field(text, 'Start') or ''
    session_end = _extract_session_field(text, 'End') or ''
    end_date = _parse_date(session_end)

    return Backlog(
        id=backlog_id,
        title=title,
        session_start=session_start,
        session_end=session_end,
        end_date=end_date,
        status=status,
        path=path,
    )


def _extract_section_first_line(text: str, section: str) -> str | None:
    pattern = re.compile(rf'^#\s+{re.escape(section)}\s*$', re.IGNORECASE)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if pattern.match(line):
            for j in range(i + 1, len(lines)):
                stripped = lines[j].strip()
                if stripped and not stripped.startswith('#'):
                    return stripped
    return None


def _extract_session_field(text: str, field: str) -> str | None:
    pattern = re.compile(rf'^\s*-\s*{re.escape(field)}\s*:?\s*(.*)', re.IGNORECASE)
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            value = m.group(1).strip()
            return value if value else None
    return None


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(value[:10], fmt).date()
        except ValueError:
            continue
    return None
