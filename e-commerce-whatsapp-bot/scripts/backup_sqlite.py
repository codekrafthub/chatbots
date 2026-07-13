"""
scripts/backup_sqlite.py — SQLite Database Backup Utility
===========================================================
Creates a timestamped copy of the SQLite database file.
Run manually or schedule with cron for automatic backups.

Usage:
    python scripts/backup_sqlite.py
    python scripts/backup_sqlite.py --db instance/ecommerce_bot.db --out backups/

Cron example (daily at 2 AM):
    0 2 * * * cd /app && python scripts/backup_sqlite.py >> logs/backup.log 2>&1

The script keeps the last N backups and deletes older ones automatically
(controlled by MAX_BACKUPS constant below).
"""

import os
import sys
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

# Default path to the SQLite database (relative to project root)
DEFAULT_DB_PATH  = "instance/ecommerce_bot.db"

# Default backup output directory
DEFAULT_BACKUP_DIR = "backups"

# Maximum number of backup files to retain (oldest are deleted first)
MAX_BACKUPS = 10

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Core functions ────────────────────────────────────────────────────────────

def backup(db_path: str, backup_dir: str) -> str:
    """
    Copy the SQLite database file to the backup directory with a timestamp.

    Args:
        db_path:    Path to the source .db file
        backup_dir: Directory where backup files will be stored

    Returns:
        Full path of the created backup file

    Raises:
        FileNotFoundError: if db_path does not exist
        OSError:           on any file system error
    """
    db_path    = Path(db_path)
    backup_dir = Path(backup_dir)

    # Validate source
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    # Ensure backup directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Build timestamped filename: ecommerce_bot_2026-06-23_14-30-00.db
    timestamp   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stem        = db_path.stem          # e.g. 'ecommerce_bot'
    dest        = backup_dir / f"{stem}_{timestamp}.db"

    # Copy the file (preserves metadata)
    shutil.copy2(str(db_path), str(dest))
    size_kb = dest.stat().st_size / 1024

    logger.info(f"✅ Backup created: {dest}  ({size_kb:.1f} KB)")
    return str(dest)


def prune_old_backups(backup_dir: str, stem: str, max_keep: int = MAX_BACKUPS):
    """
    Delete the oldest backup files, keeping only `max_keep` most recent.

    Args:
        backup_dir: Directory containing backup files
        stem:       Base filename stem (e.g. 'ecommerce_bot')
        max_keep:   Number of files to keep
    """
    backup_dir = Path(backup_dir)
    pattern    = f"{stem}_*.db"
    backups    = sorted(backup_dir.glob(pattern))   # alphabetical = chronological

    if len(backups) <= max_keep:
        return

    to_delete = backups[:len(backups) - max_keep]
    for old in to_delete:
        old.unlink()
        logger.info(f"🗑️  Removed old backup: {old.name}")


def get_db_stats(db_path: str) -> dict:
    """Return basic statistics about the database for the log."""
    try:
        import sqlite3
        conn   = sqlite3.connect(db_path)
        cursor = conn.cursor()

        stats = {}
        for table in ("leads", "conversations", "messages", "orders", "products", "faqs"):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats[table] = "N/A"

        conn.close()
        return stats
    except Exception as exc:
        return {"error": str(exc)}


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Create a timestamped backup of the SQLite database."
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=f"Path to the .db file (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_BACKUP_DIR,
        help=f"Backup directory (default: {DEFAULT_BACKUP_DIR})",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=MAX_BACKUPS,
        help=f"Max backups to retain (default: {MAX_BACKUPS})",
    )
    args = parser.parse_args()

    # Print DB stats before backup
    logger.info(f"📊 Database stats before backup:")
    stats = get_db_stats(args.db)
    for table, count in stats.items():
        logger.info(f"    {table}: {count} rows")

    # Run backup
    try:
        dest = backup(args.db, args.out)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        sys.exit(1)

    # Prune old backups
    stem = Path(args.db).stem
    prune_old_backups(args.out, stem, max_keep=args.keep)

    logger.info(f"✅ Done. Keeping last {args.keep} backups in '{args.out}/'")


if __name__ == "__main__":
    main()