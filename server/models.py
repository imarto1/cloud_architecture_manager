"""ORM models for the server database."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all server database models."""


class ArchitectureRecord(Base):
    """A parsed architecture and its provisional workload profile."""

    __tablename__ = "architectures"
    __table_args__ = (
        CheckConstraint("scale IN ('small', 'medium', 'large')"),
        CheckConstraint(
            "traffic_pattern IN ('steady', 'bursty', 'spiky', 'scheduled', 'unpredictable')"
        ),
        CheckConstraint("latency_sensitivity_score BETWEEN 0 AND 1"),
        CheckConstraint(
            "processing_style IN ('request_response', 'event_driven', 'batch', 'streaming')"
        ),
        CheckConstraint("data_intensity_score BETWEEN 0 AND 1"),
        CheckConstraint("availability_requirement IN ('standard', 'high', 'critical')"),
        CheckConstraint(
            "ops_preference IN ('managed_services', 'balanced', 'self_managed_ok')"
        ),
        CheckConstraint("budget_sensitivity_score BETWEEN 0 AND 1"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    inserted_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), nullable=False
    )
    architecture_json: Mapped[str] = mapped_column(Text, nullable=False)
    profile_metadata: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    scale: Mapped[str] = mapped_column(String, nullable=False)
    traffic_pattern: Mapped[str] = mapped_column(String, nullable=False)
    latency_sensitivity_score: Mapped[float] = mapped_column(nullable=False)
    processing_style: Mapped[str] = mapped_column(String, nullable=False)
    data_intensity_score: Mapped[float] = mapped_column(nullable=False)
    availability_requirement: Mapped[str] = mapped_column(String, nullable=False)
    ops_preference: Mapped[str] = mapped_column(String, nullable=False)
    budget_sensitivity_score: Mapped[float] = mapped_column(nullable=False)
