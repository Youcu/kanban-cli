from .model import Project
from . import repository

STATUSES = ['Todo', 'Inprogress', 'Review', 'Done']


def create_project(name: str) -> Project:
    project_path = repository.RESOURCES_PATH / name
    for status in STATUSES:
        (project_path / status).mkdir(parents=True, exist_ok=True)
    return Project(name=name, path=project_path)
