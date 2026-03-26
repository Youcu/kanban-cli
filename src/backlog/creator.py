"""Backlog file creation and template rendering."""

from __future__ import annotations

from pathlib import Path

from .model import Status
from ..project.model import Project


def next_id(project: Project) -> str:
    """Return next sequential 3-digit zero-padded ID across all status dirs."""
    existing: set[int] = set()
    for status in Status:
        d = project.path / status.value
        if d.exists():
            for f in d.glob('*_backlog.md'):
                id_part = f.stem.replace('_backlog', '')
                if id_part.isdigit():
                    existing.add(int(id_part))
    return f'{max(existing, default=0) + 1:03d}'


def create_backlog(
    project: Project,
    template: str,
    title: str,
    start: str,
    end: str,
    fields: dict[str, str],
) -> Path:
    """Create backlog markdown in {project}/Todo/ and return the file path."""
    bid = next_id(project)
    todo_dir = project.path / Status.TODO.value
    todo_dir.mkdir(parents=True, exist_ok=True)

    render = _render_general if template == 'G' else _render_developer
    content = render(title, start, end, fields)

    path = todo_dir / f'{bid}_backlog.md'
    path.write_text(content, encoding='utf-8')
    return path


# ── Template renderers ────────────────────────────────────────────────────

def _body(fields: dict[str, str], key: str) -> str:
    """Return field content with trailing newline, or empty string."""
    content = fields.get(key, '').strip()
    return content + '\n' if content else ''


def _render_general(title: str, start: str, end: str, fields: dict[str, str]) -> str:
    b = lambda k: _body(fields, k)
    return (
        f'# Title\n{title}\n'
        f'\n# What to do\n{b("what_to_do")}'
        f'\n# Why to do\n{b("why_to_do")}'
        f'\n# Session\n- Start: {start}\n- End: {end}\n'
        f'\n# Note\n{b("note")}'
    )


def _render_developer(title: str, start: str, end: str, fields: dict[str, str]) -> str:
    b = lambda k: _body(fields, k)
    return (
        f'# Title\n{title}\n'
        f'\n# What to do\n## Description\n{b("description")}'
        f'\n## User Story\n{b("user_story")}'
        f'\n# Why to do\n{b("why_to_do")}'
        f'\n# Requirement\n{b("requirement")}'
        f'\n# Tasks\n{b("tasks")}'
        f'\n# Estimated Story Point\n'
        f'\n# Complete Condition\n{b("complete_condition")}'
        f'\n# (Optional) Request/Response\n'
        f'\n# Session\n- Start: {start}\n- End: {end}\n'
        f'\n# Worker\n'
        f'\n# Note\n{b("note")}'
    )
