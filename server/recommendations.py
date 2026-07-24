"""Architecture recommendation ranking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from server.models import ArchitectureRecord


UseCase = Literal[
    "web_application",
    "public_api",
    "ecommerce",
    "real_time_analytics",
    "batch_processing",
    "event_processing",
    "media_delivery",
    "internal_tool",
    "iot_ingestion",
    "ml_inference",
]
Level = Literal["low", "medium", "high"]


LEVEL_SCORES = {"low": 0.2, "medium": 0.5, "high": 0.8}
USE_CASES: tuple[UseCase, ...] = (
    "web_application",
    "public_api",
    "ecommerce",
    "real_time_analytics",
    "batch_processing",
    "event_processing",
    "media_delivery",
    "internal_tool",
    "iot_ingestion",
    "ml_inference",
)


@dataclass(frozen=True)
class RecommendationCriteria:
    use_case: UseCase
    scale: Literal["small", "medium", "large"]
    traffic_pattern: Literal["steady", "bursty", "spiky", "scheduled", "unpredictable"]
    latency_sensitivity: Level
    processing_style: Literal["request_response", "event_driven", "batch", "streaming"]
    data_intensity: Level
    availability_requirement: Literal["standard", "high", "critical"]
    ops_preference: Literal["managed_services", "balanced", "self_managed_ok"]
    budget_sensitivity: Level


@dataclass(frozen=True)
class RankedArchitecture:
    record: ArchitectureRecord
    endpoint: str | None
    overall_score: float
    operations_score: float
    budget_score: float


class ArchitectureRecommender:
    """Rank stored architectures against a requested workload profile."""

    def recommend(
        self,
        records: list[ArchitectureRecord],
        criteria: RecommendationCriteria,
    ) -> list[tuple[RankedArchitecture, str, str]]:
        ranked = sorted(
            (self._rank(record, criteria) for record in records),
            key=lambda item: item.overall_score,
            reverse=True,
        )
        if not ranked:
            return []

        recommendations = [
            (
                ranked[0],
                "best_overall_match",
                "Best overall match across the requested workload profile.",
            )
        ]
        remaining = ranked[1:]
        if remaining:
            operations_match = max(remaining, key=lambda item: item.operations_score)
            recommendations.append(
                (
                    operations_match,
                    "operations_alignment",
                    "Alternative selected for the strongest operations-preference alignment.",
                )
            )
            remaining.remove(operations_match)
        if remaining:
            budget_match = max(remaining, key=lambda item: item.budget_score)
            recommendations.append(
                (
                    budget_match,
                    "budget_alignment",
                    "Alternative selected for the strongest budget-sensitivity alignment.",
                )
            )
        return recommendations

    def _rank(
        self,
        record: ArchitectureRecord,
        criteria: RecommendationCriteria,
    ) -> RankedArchitecture:
        use_case_score = float(self._infer_use_case(record) == criteria.use_case)
        categorical_scores = (
            float(record.scale == criteria.scale),
            float(record.traffic_pattern == criteria.traffic_pattern),
            float(record.processing_style == criteria.processing_style),
            float(record.availability_requirement == criteria.availability_requirement),
            float(record.ops_preference == criteria.ops_preference),
        )
        numeric_scores = (
            self._numeric_match(record.latency_sensitivity_score, criteria.latency_sensitivity),
            self._numeric_match(record.data_intensity_score, criteria.data_intensity),
            self._numeric_match(record.budget_sensitivity_score, criteria.budget_sensitivity),
        )
        overall_score = (2 * use_case_score + sum(categorical_scores) + sum(numeric_scores)) / 10
        document = json.loads(record.architecture_json)
        endpoint = document.get("metadata", {}).get("endpoint")
        return RankedArchitecture(
            record=record,
            endpoint=endpoint,
            overall_score=overall_score,
            operations_score=float(record.ops_preference == criteria.ops_preference),
            budget_score=self._numeric_match(record.budget_sensitivity_score, criteria.budget_sensitivity),
        )

    @staticmethod
    def _numeric_match(score: float, requested_level: Level) -> float:
        return max(0.0, 1.0 - abs(score - LEVEL_SCORES[requested_level]))

    @staticmethod
    def _infer_use_case(record: ArchitectureRecord) -> UseCase | None:
        document = json.loads(record.architecture_json)
        searchable_text = json.dumps(document).lower().replace("-", "_")
        for use_case in USE_CASES:
            if use_case in searchable_text:
                return use_case
        return None
