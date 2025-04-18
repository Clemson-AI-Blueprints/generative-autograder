
# ========================= file_manager.py ===================
from pathlib import Path
from typing import List, Tuple, Dict
from .constants import ROOT
from .models import FileRecord
from .config_io import read_yaml, write_yaml

CONFIG_FILENAME = "config.yaml"


def _project_folder(project_id: str) -> Path:
    return ROOT / project_id


def load_project(project_id: str) -> Dict:
    cfg_path = _project_folder(project_id) / CONFIG_FILENAME
    cfg = read_yaml(cfg_path)
    return cfg


def save_project(
    project_id: str,
    config_option: str,
    new_files: List[FileRecord],
    visibility: List[str],
) -> None:
    folder = _project_folder(project_id)
    cfg_path = folder / CONFIG_FILENAME

    # Merge with existing data to preserve visibility flags when untouched
    files = load_project(project_id).get("files", [])
    for f in new_files:
        files.append(f.to_dict())

    for f in files:
        f['visible_to_students'] = f['name'] in visibility

    cfg = {
        "project_id": project_id,
        "config_option": config_option,
        "files": files,
    }

    print("Wrote YAML config to", cfg_path)
    write_yaml(cfg_path, cfg)
