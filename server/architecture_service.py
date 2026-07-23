"""Database operations for architecture records."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, delete, inspect, select, text, update
from sqlalchemy.orm import sessionmaker

from server.models import ArchitectureRecord, Base


DATABASE_PATH = Path(__file__).with_name("architectures.sqlite")


class ArchitectureService:
    """Own the SQLite connection and CRUD operations for architectures."""

    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.engine = create_engine(f"sqlite:///{database_path}")
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)
        columns = {column["name"] for column in inspect(self.engine).get_columns("architectures")}
        if "inserted_at" not in columns:
            with self.engine.begin() as connection:
                connection.execute(text("ALTER TABLE architectures ADD COLUMN inserted_at DATETIME"))
            with self._sessions.begin() as session:
                session.execute(
                    update(ArchitectureRecord)
                    .where(ArchitectureRecord.inserted_at.is_(None))
                    .values(inserted_at=datetime.now(UTC))
                )

    def get(self, architecture_id: str) -> ArchitectureRecord | None:
        self.create_schema()
        with self._sessions() as session:
            return session.get(ArchitectureRecord, architecture_id)

    def list(self) -> list[ArchitectureRecord]:
        self.create_schema()
        with self._sessions() as session:
            return list(session.scalars(select(ArchitectureRecord).order_by(ArchitectureRecord.name)))

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
