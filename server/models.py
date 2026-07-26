"""ORM models for the server database."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from server.profile_types import (
    AvailabilityRequirement,
    OpsPreference,
    ProcessingStyle,
    ProfileValues,
    Scale,
    TrafficPattern,
)


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for new records."""
    return datetime.now(UTC)


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
        CheckConstraint("ops_preference IN ('managed_services', 'balanced', 'self_managed_ok')"),
        CheckConstraint("budget_sensitivity_score BETWEEN 0 AND 1"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    inserted_at: Mapped[datetime] = mapped_column(
        default=utc_now,
        nullable=False,
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

    def profile_values(self) -> ProfileValues:
        """Return persisted profile columns as a typed value object."""
        return {
            "scale": cast(Scale, self.scale),
            "traffic_pattern": cast(TrafficPattern, self.traffic_pattern),
            "latency_sensitivity_score": self.latency_sensitivity_score,
            "processing_style": cast(ProcessingStyle, self.processing_style),
            "data_intensity_score": self.data_intensity_score,
            "availability_requirement": cast(
                AvailabilityRequirement,
                self.availability_requirement,
            ),
            "ops_preference": cast(OpsPreference, self.ops_preference),
            "budget_sensitivity_score": self.budget_sensitivity_score,
        }
