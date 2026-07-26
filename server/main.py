"""FastAPI application for saved architecture records."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from requests import RequestException

from aws_parser import parse, teardown_mocks
from server.api_models import (
    ArchitectureDetailResponse,
    ArchitectureRecommendationRequest,
    ArchitectureRecommendationResponse,
    ArchitectureResponse,
    ParseArchitectureRequest,
)
from server.architecture_service import DATABASE_PATH, ArchitectureService
from server.init_db import seed_database
from server.recommendations import ArchitectureRecommender, RecommendationCriteria
from server.record_factory import create_architecture_record

logger = logging.getLogger(__name__)
architecture_service = ArchitectureService()
recommender = ArchitectureRecommender()


def ensure_database() -> None:
    """Seed a missing local database during application initialization."""
    if DATABASE_PATH.exists():
        return

    try:
        seed_database()
    finally:
        teardown_mocks()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize external resources before the API accepts requests."""
    ensure_database()
    yield


app = FastAPI(
    title="Cloud Architecture Manager API",
    lifespan=lifespan,
)


@app.get("/architectures", response_model=list[ArchitectureResponse])
def get_architectures() -> list[ArchitectureResponse]:
    """Return every architecture stored in the local database."""
    return [ArchitectureResponse.from_record(record) for record in architecture_service.list()]


@app.post(
    "/architectures/recommendations",
    response_model=list[ArchitectureRecommendationResponse],
)
def recommend_architectures(
    request: ArchitectureRecommendationRequest,
) -> list[ArchitectureRecommendationResponse]:
    """Return up to three saved architectures ranked for the requested profile."""
    criteria = RecommendationCriteria(**request.model_dump())
    recommendations = recommender.recommend(
        architecture_service.list(),
        criteria,
    )
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
    record = architecture_service.get(architecture_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Architecture not found.",
        )
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
def parse_architecture(
    request: ParseArchitectureRequest,
) -> ArchitectureResponse:
    """Parse an AWS-compatible endpoint and save the resulting architecture."""
    try:
        architecture = parse(
            request.endpoint,
            request.name,
            request.region,
            request.services,
        )
    except RequestException as error:
        logger.warning(
            "Could not reach architecture endpoint %s: %s",
            request.endpoint,
            error,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the architecture endpoint.",
        ) from error

    record = architecture_service.create(
        create_architecture_record(architecture.model_dump(mode="json"))
    )
    return ArchitectureResponse.from_record(record)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=os.getenv("SERVER_HOST", "127.0.0.1"),
        port=int(os.getenv("SERVER_PORT", "8000")),
    )
