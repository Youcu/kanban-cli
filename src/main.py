"""Schedule Manager CLI - Entry Point"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import renderer
from src.ui import kanban as kanban_renderer
from src.ui import opt as opt_session
from src.ui import todo_sort as todo_sort_prompt
from src.ui.terminal import clear_screen
from src.project import repository, manager
from src.backlog import repository as backlog_repo
from src import kanban_git_backup


def run() -> None:
    message: str | None = None

    while True:
        clear_screen()
        print()
        renderer.render_header()
        projects = repository.list_projects()
        renderer.render_project_list(projects, message=message)
        message = None

        raw = renderer.render_prompt()
        cmd = raw.lower()

        if cmd in ('q', 'quit'):
            print('  Goodbye.\n')
            break

        if cmd in ('a', 'all'):
            if not projects:
                message = '  No projects yet.'
                continue
            _run_aggregate_kanban_session(projects)
            continue

        if cmd == 'n':
            name = renderer.render_project_name_prompt()
            if not name:
                message = '  Project name cannot be empty.'
                continue
            if repository.exists(name):
                message = f'  Project "{name}" already exists.'
                continue
            project = manager.create_project(name)
            message = f'  Project "{project.name}" created.'
            continue

        if cmd in ('r', 'remove'):
            if not projects:
                message = '  No projects yet.'
                continue
            chosen = renderer.prompt_remove_project_selection(projects)
            if chosen is None:
                continue
            if not renderer.prompt_remove_project_confirm(chosen):
                message = '  Remove cancelled.'
                continue
            try:
                manager.delete_project(chosen)
            except (ValueError, FileNotFoundError, OSError) as exc:
                message = f'  Could not remove project: {exc}'
                continue
            message = f'  Project "{chosen.name}" removed.'
            continue

        if cmd in ('b', 'backup'):
            message = f'  {kanban_git_backup.run_git_backup()}'
            continue

        if cmd.isdigit():
            index = int(cmd) - 1
            if 0 <= index < len(projects):
                _run_kanban_session(projects[index])
                continue
            else:
                message = f'  Invalid selection: {raw}'
                continue

        message = (
            f'  Unknown command: "{raw}"  '
            '(number, N, A, R, B, or Q)'
        )


def _run_aggregate_kanban_session(projects) -> None:
    message: str | None = None
    todo_sort = backlog_repo.TodoSortMode.CREATION

    while True:
        clear_screen()
        print()
        board = backlog_repo.load_aggregate_board(projects, todo_sort=todo_sort)
        kanban_renderer.render_aggregate_kanban(
            board,
            project_count=len(projects),
        )

        if message:
            print(f'     {message}')
            print()
            message = None

        raw = kanban_renderer.render_kanban_prompt()
        cmd = raw.lower()

        if cmd in ('b', 'back'):
            print()
            break

        if cmd == 'opt':
            message = opt_session.run_aggregate_opt_session(projects)
            continue

        if cmd == 'sort':
            chosen = todo_sort_prompt.prompt_todo_sort(todo_sort)
            if chosen is not None:
                todo_sort = chosen
            continue

        message = (
            f'  Unknown command: "{raw}"  '
            '(B: back, opt: options, sort: Todo order)'
        )


def _run_kanban_session(project) -> None:
    message: str | None = None
    todo_sort = backlog_repo.TodoSortMode.CREATION

    while True:
        clear_screen()
        print()
        board = backlog_repo.load_board(project, todo_sort=todo_sort)
        kanban_renderer.render_kanban(project, board)

        if message:
            print(f'     {message}')
            print()
            message = None

        raw = kanban_renderer.render_kanban_prompt()
        cmd = raw.lower()

        if cmd in ('b', 'back'):
            print()
            break

        if cmd == 'opt':
            message = opt_session.run_opt_session(project)
            continue

        if cmd == 'sort':
            chosen = todo_sort_prompt.prompt_todo_sort(todo_sort)
            if chosen is not None:
                todo_sort = chosen
            continue

        message = (
            f'  Unknown command: "{raw}"  '
            '(B: back, opt: options, sort: Todo order)'
        )


if __name__ == '__main__':
    run()
