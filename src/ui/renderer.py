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

    print(box.row(box.pad_between('[N] New Project', '[Q] Quit')))
    print(box.bottom())

    if message:
        print(f'     {message}')

    print()


def render_prompt() -> str:
    try:
        return input('❯ ').strip()
    except (EOFError, KeyboardInterrupt):
        return 'q'


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


