"""Tests for architecture ranking and selection."""

from __future__ import annotations

import json

from server.models import ArchitectureRecord
from server.profile_types import (
    AvailabilityRequirement,
    OpsPreference,
    ProcessingStyle,
    Scale,
    TrafficPattern,
)
from server.recommendations import ArchitectureRecommender, RecommendationCriteria


def make_record(
    *,
    record_id: str,
    document_name: str,
    scale: Scale,
    traffic_pattern: TrafficPattern,
    latency_score: float,
    processing_style: ProcessingStyle,
    data_score: float,
    availability: AvailabilityRequirement,
    operations: OpsPreference,
    budget_score: float,
) -> ArchitectureRecord:
    return ArchitectureRecord(
        id=record_id,
        name=document_name,
        architecture_json=json.dumps({"name": document_name, "resources": []}),
        scale=scale,
        traffic_pattern=traffic_pattern,
        latency_sensitivity_score=latency_score,
        processing_style=processing_style,
        data_intensity_score=data_score,
        availability_requirement=availability,
        ops_preference=operations,
        budget_sensitivity_score=budget_score,
    )


def test_use_case_name_contributes_twice_to_the_original_ranking_formula() -> None:
    criteria = RecommendationCriteria(
        use_case="ecommerce",
        scale="large",
        traffic_pattern="bursty",
        latency_sensitivity="high",
        processing_style="request_response",
        data_intensity="high",
        availability_requirement="critical",
        ops_preference="balanced",
        budget_sensitivity="low",
    )
    matching_use_case = make_record(
        record_id="matching",
        document_name="Ecommerce",
        scale="large",
        traffic_pattern="bursty",
        latency_score=0.8,
        processing_style="request_response",
        data_score=0.8,
        availability="critical",
        operations="balanced",
        budget_score=0.2,
    )
    unlabelled = make_record(
        record_id="unlabelled",
        document_name="Unlabelled architecture",
        scale="large",
        traffic_pattern="bursty",
        latency_score=0.8,
        processing_style="request_response",
        data_score=0.8,
        availability="critical",
        operations="balanced",
        budget_score=0.2,
    )

    recommender = ArchitectureRecommender()
    recommendations = recommender.recommend([unlabelled, matching_use_case], criteria)

    assert recommendations[0][0].record.id == "matching"
    assert recommendations[0][0].overall_score == 1.0
    assert recommendations[1][0].overall_score == 0.8
