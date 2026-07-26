"""Initialize the container database before starting the API."""

from __future__ import annotations

import os
import subprocess
import sys

from server.architecture_service import DATABASE_PATH


def start() -> None:
    """Seed a missing database, then replace this process with the API."""
    if not DATABASE_PATH.exists():
        subprocess.run(
            [sys.executable, "-m", "server.init_db"],
            check=True,
        )

    os.execv(
        sys.executable,
        [sys.executable, "-m", "server.main"],
    )


if __name__ == "__main__":
    start()
