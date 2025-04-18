
# ========================= config_io.py ======================
import yaml
from pathlib import Path
from typing import Dict, Any


def read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf‑8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf‑8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

