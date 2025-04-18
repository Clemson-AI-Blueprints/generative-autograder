
# ========================= constants.py ======================
from pathlib import Path
import os

# Root directory where all project folders live.  Overridable via env‑var
ROOT: Path = Path(os.getenv("AUTOHINT_CONFIG_ROOT", "/mounted_autohint_configs"))