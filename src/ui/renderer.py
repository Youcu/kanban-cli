"""Screen renderer for project list view."""

from typing import Optional
from . import box
from ..project.model import Project


TITLE = 'Schedule Manager CLI'
VERSION = 'v0.1'


def render_header() -> None:
    print(box.top())
    title_line = f'{TITLE}  {VERSION}'
    print(box.row(title_line))
    print(box.bottom())
    print()


def render_project_list(projects: list[Project], message: Optional[str] = None) -> None:
    print(box.top('Projects'))

    if not projects:
        print(box.empty_row())
        print(box.row('  No projects yet.'))
        print(box.empty_row())
    else:
        print(box.empty_row())
        for i, project in enumerate(projects, start=1):
            print(box.row(f'  [{i}]  {project.name}'))
        print(box.empty_row())

    print(box.divider())

    print(box.row('  [N] New project   [A] All boards   [Q] Quit'))
    print(box.bottom())

    if message:
        print(f'     {message}')

    print()


def render_prompt() -> str:
    try:
        return input('❯ ').strip()
    except (EOFError, KeyboardInterrupt):
        return 'q'


def prompt_project_choice(projects: list[Project], *, title: str) -> Project | None:
    """Pick a project by number, or cancel with B. Sorted by name for stable labels."""
    ordered = sorted(projects, key=lambda p: p.name.casefold())
    print(box.top(title))
    print(box.empty_row())
    for i, p in enumerate(ordered, start=1):
        print(box.row(f'  [{i}]  {p.name}'))
    print(box.empty_row())
    print(box.row('  [B] Cancel'))
    print(box.bottom())
    print()
    while True:
        try:
            raw = input('❯ ').strip()
        except (EOFError, KeyboardInterrupt):
            return None
        cmd = raw.lower()
        if cmd in ('b', 'back', ''):
            return None
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(ordered):
                return ordered[idx]
        print(f'  Invalid: "{raw}"  (number or B)')
        print()


def render_project_name_prompt() -> str:
    print()
    try:
        name = input('  Project name: ').strip()
    except (EOFError, KeyboardInterrupt):
        name = ''
    print()
    return name


def render_selected(project: Project) -> None:
    print()
    print(f'  ✓ Project "{project.name}" selected.')
    print()


