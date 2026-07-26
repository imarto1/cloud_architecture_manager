"""Database operations for architecture records."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from sqlalchemy import URL, create_engine, delete, inspect, select, text, update
from sqlalchemy.orm import sessionmaker

from server.models import ArchitectureRecord, Base

DEFAULT_DATABASE_PATH = Path(__file__).with_name("architectures.sqlite")
DATABASE_PATH = Path(os.getenv("ARCHITECTURES_DATABASE_PATH", DEFAULT_DATABASE_PATH))


class ArchitectureService:
    """Own the SQLite connection and CRUD operations for architectures."""

    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.engine = create_engine(
            URL.create("sqlite", database=str(database_path)),
        )
        self._sessions = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
        self._schema_lock = Lock()
        self._schema_ready = False

    def create_schema(self) -> None:
        """Create the schema once and upgrade records from legacy profiles."""
        if self._schema_ready:
            return

        with self._schema_lock:
            if self._schema_ready:
                return

            Base.metadata.create_all(self.engine)
            columns = {
                column["name"] for column in inspect(self.engine).get_columns("architectures")
            }
            has_inserted_at = "inserted_at" in columns
            has_profile_metadata = "profile_metadata" in columns

            with self.engine.begin() as connection:
                if not has_inserted_at:
                    connection.execute(
                        text("ALTER TABLE architectures ADD COLUMN inserted_at DATETIME")
                    )
                if not has_profile_metadata:
                    connection.execute(
                        text(
                            "ALTER TABLE architectures "
                            "ADD COLUMN profile_metadata TEXT "
                            "NOT NULL DEFAULT '{}'"
                        ),
                    )

            if not has_inserted_at:
                with self._sessions.begin() as session:
                    session.execute(
                        update(ArchitectureRecord)
                        .where(ArchitectureRecord.inserted_at.is_(None))
                        .values(inserted_at=datetime.now(UTC))
                    )

            if not has_profile_metadata:
                self._rescore_existing_records()
            self._schema_ready = True

    def _rescore_existing_records(self) -> None:
        """Replace legacy random profiles after adding profile metadata."""
        from server.profiling import calculate_profile

        with self._sessions.begin() as session:
            for record in session.scalars(select(ArchitectureRecord)):
                profile = calculate_profile(json.loads(record.architecture_json))
                for field, value in profile.values.items():
                    setattr(record, field, value)
                record.profile_metadata = json.dumps(profile.metadata)

    def get(self, architecture_id: str) -> ArchitectureRecord | None:
        self.create_schema()
        with self._sessions() as session:
            return session.get(ArchitectureRecord, architecture_id)

    def list(self) -> list[ArchitectureRecord]:
        self.create_schema()
        with self._sessions() as session:
            return list(
                session.scalars(select(ArchitectureRecord).order_by(ArchitectureRecord.name))
            )

    def replace_all(self, architectures: Sequence[ArchitectureRecord]) -> None:
        """Replace all stored records as one transaction."""
        self.create_schema()
        with self._sessions.begin() as session:
            session.execute(delete(ArchitectureRecord))
            session.add_all(architectures)

    def create(self, architecture: ArchitectureRecord) -> ArchitectureRecord:
        self.create_schema()
        with self._sessions.begin() as session:
            session.add(architecture)
        return architecture
