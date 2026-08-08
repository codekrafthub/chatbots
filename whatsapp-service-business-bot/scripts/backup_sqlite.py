from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def backup_sqlite(db_path: str = "instance/servicebot.sqlite3", backup_dir: str = "backups") -> Path:
    source = Path(db_path)
    if not source.exists():
        raise FileNotFoundError(source)
    target_dir = Path(backup_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"servicebot-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.sqlite3"
    shutil.copy2(source, target)
    return target


if __name__ == "__main__":
    print(backup_sqlite())
