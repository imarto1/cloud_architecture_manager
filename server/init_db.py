"""Seed a local SQLite database from the bundled mock architectures.

Run with ``python -m server.init_db``. It starts/parses the LocalStack mock
architectures through ``aws_parser.parse_mocks`` and stores one row per
architecture in ``architectures.sqlite``.
"""

from __future__ import annotations

from pathlib import Path

from aws_parser import parse_mocks, teardown_mocks
from server.architecture_service import DATABASE_PATH, ArchitectureService
from server.record_factory import create_architecture_record


def seed_database(
    database_path: Path = DATABASE_PATH,
) -> int:
    """Recreate the seed rows and return how many mock architectures were stored."""
    architectures = parse_mocks()
    records = [
        create_architecture_record(architecture.model_dump(mode="json"))
        for architecture in architectures
    ]
    ArchitectureService(database_path).replace_all(records)
    return len(architectures)


if __name__ == "__main__":
    try:
        count = seed_database()
    finally:
        teardown_mocks()
    print(f"Seeded {count} architecture record(s) in {DATABASE_PATH}")
