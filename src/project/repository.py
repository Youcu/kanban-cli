from pathlib import Path
from .model import Project

# Default project storage location: ~/.kanban/data
DATA_PATH = Path.home() / '.kanban' / 'data'
# Backward-compatible alias for existing imports/usages.
RESOURCES_PATH = DATA_PATH


def list_projects() -> list[Project]:
    if not RESOURCES_PATH.exists():
        return []
    return [
        Project(name=d.name, path=d)
        for d in sorted(RESOURCES_PATH.iterdir())
        if d.is_dir()
    ]


def exists(name: str) -> bool:
    return (RESOURCES_PATH / name).exists()
