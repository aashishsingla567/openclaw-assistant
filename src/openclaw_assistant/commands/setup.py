from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def setup_command() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    legacy_script = repo_root / "onboard" / "setup.py"
    subprocess.run([sys.executable, str(legacy_script)], check=True, cwd=repo_root)
