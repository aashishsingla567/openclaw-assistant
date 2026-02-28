from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def update_command(*, dev: bool = False) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    legacy_script = repo_root / "onboard" / "update.py"
    args = [sys.executable, str(legacy_script)]
    if dev:
        args.append("--dev")
    subprocess.run(args, check=True, cwd=repo_root)
