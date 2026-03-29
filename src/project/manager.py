import shutil

from .model import Project
from . import repository

STATUSES = ['Todo', 'Inprogress', 'Review', 'Done']


def create_project(name: str) -> Project:
    project_path = repository.RESOURCES_PATH / name
    for status in STATUSES:
        (project_path / status).mkdir(parents=True, exist_ok=True)
    return Project(name=name, path=project_path)


def delete_project(project: Project) -> None:
    """Remove the project directory and all backlog data under ~/.kanban/data."""
    root = repository.RESOURCES_PATH.resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = project.path.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError('project path outside data directory') from exc
    if not target.is_dir():
        raise FileNotFoundError(str(target))
    shutil.rmtree(target)
