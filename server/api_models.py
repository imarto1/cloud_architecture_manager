"""Validated request and response models for the FastAPI application."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from server.models import ArchitectureRecord
from server.profile_types import (
    AvailabilityRequirement,
    Level,
    OpsPreference,
    ProcessingStyle,
    Scale,
    TrafficPattern,
    UseCase,
)


class ArchitectureResponse(BaseModel):
    id: str
    name: str
    inserted_at: datetime
    architecture: dict[str, Any]
    profile_metadata: dict[str, Any]
    scale: Scale
    traffic_pattern: TrafficPattern
    latency_sensitivity_score: float
    processing_style: ProcessingStyle
    data_intensity_score: float
    availability_requirement: AvailabilityRequirement
    ops_preference: OpsPreference
    budget_sensitivity_score: float

    @classmethod
    def from_record(cls, record: ArchitectureRecord) -> ArchitectureResponse:
        return cls.model_validate(
            {
                **record.profile_values(),
                "id": record.id,
                "name": record.name,
                "inserted_at": record.inserted_at,
                "architecture": json.loads(record.architecture_json),
                "profile_metadata": json.loads(record.profile_metadata),
            }
        )


class ArchitectureDetailResponse(ArchitectureResponse):
    architecture: dict[str, Any] | None = None
    profile_metadata: dict[str, Any] | None = None

    @classmethod
    def from_record(
        cls,
        record: ArchitectureRecord,
        include_profile_metadata: bool,
        include_architecture_data: bool,
    ) -> ArchitectureDetailResponse:
        response = ArchitectureResponse.from_record(record).model_dump()
        if not include_profile_metadata:
            response["profile_metadata"] = None
        if not include_architecture_data:
            response["architecture"] = None
        return cls.model_validate(response)


class ParseArchitectureRequest(BaseModel):
    endpoint: str
    name: str
    region: str = "us-east-1"
    services: set[str] | None = None


class ArchitectureRecommendationRequest(BaseModel):
    use_case: UseCase
    scale: Scale
    traffic_pattern: TrafficPattern
    latency_sensitivity: Level
    processing_style: ProcessingStyle
    data_intensity: Level
    availability_requirement: AvailabilityRequirement
    ops_preference: OpsPreference
    budget_sensitivity: Level


class ArchitectureRecommendationResponse(BaseModel):
    architecture_id: str
    name: str
    endpoint: str | None
    match_score: float
    recommendation_type: str
    reason: str
