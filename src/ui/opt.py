"""Opt command session: context-aware option menu and dispatch."""

from __future__ import annotations

from . import box, create_flow, view_flow, edit_flow, move_flow, delete_flow, renderer
from .terminal import clear_screen
from ..backlog.model import Status
from ..project.model import Project

_UNAVAILABLE = '  (no backlogs)'


def _pick_project(projects: list[Project], *, title: str) -> Project | None:
    if len(projects) == 1:
        return projects[0]
    return renderer.prompt_project_choice(projects, title=title)


def run_aggregate_opt_session(projects: list[Project]) -> str | None:
    """Options menu for the all-projects kanban; asks which project when needed."""
    has_backlogs = any(_any_backlogs(p) for p in projects)

    clear_screen()
    print()
    _render_opt_menu(has_backlogs)

    while True:
        try:
            raw = input('❯ ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == '1':
            # All Boards: always pick target project (even if only one exists).
            target = renderer.prompt_project_choice(
                projects,
                title='Create backlog — project',
            )
            if target is None:
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return create_flow.run_create_flow(target)

        if raw == '2':
            if not has_backlogs:
                print('  No backlogs to view.')
                print()
                continue
            target = _pick_project(projects, title='View backlog — project')
            if target is None:
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            result = view_flow.run_view_flow(target)
            if result is view_flow.ViewFlowResult.BACK_TO_OPT_MENU:
                has_backlogs = any(_any_backlogs(p) for p in projects)
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return result

        if raw == '3':
            if not has_backlogs:
                print('  No backlogs to edit.')
                print()
                continue
            target = _pick_project(projects, title='Edit backlog — project')
            if target is None:
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return edit_flow.run_edit_flow(target)

        if raw == '4':
            if not has_backlogs:
                print('  No backlogs to move.')
                print()
                continue
            target = _pick_project(projects, title='Move backlog — project')
            if target is None:
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return move_flow.run_move_flow(target)

        if raw == '5':
            if not has_backlogs:
                print('  No backlogs to delete.')
                print()
                continue
            target = _pick_project(projects, title='Delete backlog — project')
            if target is None:
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return delete_flow.run_delete_flow(target)

        if raw in ('b', 'back', ''):
            return None

        print(f'  Unknown: "{raw}"  (1–5, B to back)')
        print()


def run_opt_session(project: Project) -> str | None:
    """Render context-aware opt menu and dispatch. Returns feedback message or None."""
    has_backlogs = _any_backlogs(project)

    clear_screen()
    print()
    _render_opt_menu(has_backlogs)

    while True:
        try:
            raw = input('❯ ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == '1':
            return create_flow.run_create_flow(project)

        if raw == '2':
            if not has_backlogs:
                print('  No backlogs to view.')
                print()
                continue
            result = view_flow.run_view_flow(project)
            if result is view_flow.ViewFlowResult.BACK_TO_OPT_MENU:
                has_backlogs = _any_backlogs(project)
                clear_screen()
                print()
                _render_opt_menu(has_backlogs)
                continue
            return result

        if raw == '3':
            if not has_backlogs:
                print('  No backlogs to edit.')
                print()
                continue
            return edit_flow.run_edit_flow(project)

        if raw == '4':
            if not has_backlogs:
                print('  No backlogs to move.')
                print()
                continue
            return move_flow.run_move_flow(project)

        if raw == '5':
            if not has_backlogs:
                print('  No backlogs to delete.')
                print()
                continue
            return delete_flow.run_delete_flow(project)

        if raw in ('b', 'back', ''):
            return None

        print(f'  Unknown: "{raw}"  (1–5, B to back)')
        print()


# ── Menu renderer ─────────────────────────────────────────────────────────

def _render_opt_menu(has_backlogs: bool) -> None:
    def opt_row(num: str, label: str, active: bool) -> str:
        suffix = '' if active else _UNAVAILABLE
        return f'  [{num}] {label}{suffix}'

    print(box.top('Options'))
    print(box.empty_row())
    print(box.row(opt_row('1', 'Create Backlog ', active=True)))
    print(box.empty_row())
    print(box.row(opt_row('2', 'View Backlog   ', active=has_backlogs)))
    print(box.empty_row())
    print(box.row(opt_row('3', 'Edit Backlog   ', active=has_backlogs)))
    print(box.empty_row())
    print(box.row(opt_row('4', 'Move Backlog   ', active=has_backlogs)))
    print(box.empty_row())
    print(box.row(opt_row('5', 'Delete Backlog ', active=has_backlogs)))
    print(box.empty_row())
    print(box.divider())
    print(box.row('  [B] Back'))
    print(box.bottom())
    print()


# ── Context check ─────────────────────────────────────────────────────────

def _any_backlogs(project: Project) -> bool:
    for status in Status:
        d = project.path / status.value
        if d.exists() and any(d.glob('*_backlog.md')):
            return True
    return False
