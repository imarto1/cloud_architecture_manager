"""FastAPI application for saved architecture records."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from requests import RequestException

from aws_parser import parse
from server.architecture_service import ArchitectureService, DATABASE_PATH
from server.init_db import seed_database
from server.models import ArchitectureRecord
from server.profiling import calculate_profile
from server.recommendations import ArchitectureRecommender, RecommendationCriteria, UseCase


class ArchitectureResponse(BaseModel):
    id: str
    name: str
    inserted_at: datetime
    architecture: dict[str, Any]
    profile_metadata: dict[str, Any]
    scale: str
    traffic_pattern: str
    latency_sensitivity_score: float
    processing_style: str
    data_intensity_score: float
    availability_requirement: str
    ops_preference: str
    budget_sensitivity_score: float

    @classmethod
    def from_record(cls, record: ArchitectureRecord) -> "ArchitectureResponse":
        return cls(
            id=record.id,
            name=record.name,
            inserted_at=record.inserted_at,
            architecture=json.loads(record.architecture_json),
            profile_metadata=json.loads(record.profile_metadata),
            scale=record.scale,
            traffic_pattern=record.traffic_pattern,
            latency_sensitivity_score=record.latency_sensitivity_score,
            processing_style=record.processing_style,
            data_intensity_score=record.data_intensity_score,
            availability_requirement=record.availability_requirement,
            ops_preference=record.ops_preference,
            budget_sensitivity_score=record.budget_sensitivity_score,
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
    ) -> "ArchitectureDetailResponse":
        response = ArchitectureResponse.from_record(record).model_dump()
        if not include_profile_metadata:
            response["profile_metadata"] = None
        if not include_architecture_data:
            response["architecture"] = None
        return cls.model_validate(response)


class ParseArchitectureRequest(BaseModel):
    endpoint: str
    region: str = "us-east-1"
    services: set[str] | None = None


class ArchitectureRecommendationRequest(BaseModel):
    use_case: UseCase
    scale: Literal["small", "medium", "large"]
    traffic_pattern: Literal["steady", "bursty", "spiky", "scheduled", "unpredictable"]
    latency_sensitivity: Literal["low", "medium", "high"]
    processing_style: Literal["request_response", "event_driven", "batch", "streaming"]
    data_intensity: Literal["low", "medium", "high"]
    availability_requirement: Literal["standard", "high", "critical"]
    ops_preference: Literal["managed_services", "balanced", "self_managed_ok"]
    budget_sensitivity: Literal["low", "medium", "high"]


class ArchitectureRecommendationResponse(BaseModel):
    architecture_id: str
    name: str
    endpoint: str | None
    match_score: float
    recommendation_type: str
    reason: str


def ensure_database() -> None:
    """Seed the local database on first use when its file is absent."""
    if not DATABASE_PATH.exists():
        seed_database()


architecture_service = ArchitectureService()
app = FastAPI(title="Cloud Architecture Manager API")
logger = logging.getLogger(__name__)


@app.get("/architectures", response_model=list[ArchitectureResponse])
def get_architectures() -> list[ArchitectureResponse]:
    """Return every architecture stored in the local database."""
    ensure_database()
    return [ArchitectureResponse.from_record(record) for record in architecture_service.list()]


@app.post(
    "/architectures/recommendations",
    response_model=list[ArchitectureRecommendationResponse],
)
def recommend_architectures(
    request: ArchitectureRecommendationRequest,
) -> list[ArchitectureRecommendationResponse]:
    """Return up to three saved architectures ranked for the requested profile."""
    ensure_database()
    criteria = RecommendationCriteria(**request.model_dump())
    recommendations = ArchitectureRecommender().recommend(architecture_service.list(), criteria)
    return [
        ArchitectureRecommendationResponse(
            architecture_id=recommendation.record.id,
            name=recommendation.record.name,
            endpoint=recommendation.endpoint,
            match_score=round(recommendation.overall_score, 3),
            recommendation_type=recommendation_type,
            reason=reason,
        )
        for recommendation, recommendation_type, reason in recommendations
    ]


@app.get(
    "/architectures/{architecture_id}",
    response_model=ArchitectureDetailResponse,
    response_model_exclude_none=True,
)
def get_architecture(
    architecture_id: str,
    include_profile_metadata: bool = False,
    include_architecture_data: bool = False,
) -> ArchitectureDetailResponse:
    """Return one saved architecture, with optional JSON and profile metadata."""
    ensure_database()
    record = architecture_service.get(architecture_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Architecture not found.")
    return ArchitectureDetailResponse.from_record(
        record,
        include_profile_metadata,
        include_architecture_data,
    )


@app.post(
    "/architectures/parse",
    response_model=ArchitectureResponse,
    status_code=status.HTTP_201_CREATED,
)
def parse_architecture(request: ParseArchitectureRequest) -> ArchitectureResponse:
    """Parse an AWS-compatible endpoint and save the resulting architecture."""
    ensure_database()
    try:
        architecture = parse(request.endpoint, request.region, request.services)
    except RequestException as error:
        logger.warning("Could not reach architecture endpoint %s: %s", request.endpoint, error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the architecture endpoint.",
        ) from error
    document = architecture.model_dump(mode="json")
    profile = calculate_profile(document)
    record = architecture_service.create(
        ArchitectureRecord(
            id=str(uuid.uuid4()),
            name=document["name"],
            architecture_json=json.dumps(document),
            profile_metadata=json.dumps(profile.metadata),
            **profile.values,
        )
    )
    return ArchitectureResponse.from_record(record)
