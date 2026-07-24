"""Seed a local SQLite database from the bundled mock architectures.

Run with ``python server/init_db.py``. It starts/parses the LocalStack mock
architectures through ``aws_parser.parse_mocks`` and stores one row per
architecture in ``architectures.sqlite``.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aws_parser import parse_mocks
from server.architecture_service import ArchitectureService, DATABASE_PATH
from server.models import ArchitectureRecord
from server.profiling import calculate_profile


def seed_database(database_path: Path = DATABASE_PATH) -> int:
    """Recreate the seed rows and return how many mock architectures were stored."""
    architectures = parse_mocks()

    records = []
    for architecture in architectures:
        document = architecture.model_dump(mode="json")
        profile = calculate_profile(document)
        records.append(
            ArchitectureRecord(
                id=str(uuid.uuid4()),
                name=document["name"],
                architecture_json=json.dumps(document),
                profile_metadata=json.dumps(profile.metadata),
                **profile.values,
            )
        )
    ArchitectureService(database_path).replace_all(records)
    return len(architectures)


if __name__ == "__main__":
    count = seed_database()
    print(f"Seeded {count} architecture record(s) in {DATABASE_PATH}")
