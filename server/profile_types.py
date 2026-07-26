"""Shared types for architecture profiles and recommendation criteria."""

from __future__ import annotations

from typing import Literal, TypedDict

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
Scale = Literal["small", "medium", "large"]
TrafficPattern = Literal["steady", "bursty", "spiky", "scheduled", "unpredictable"]
Level = Literal["low", "medium", "high"]
ProcessingStyle = Literal["request_response", "event_driven", "batch", "streaming"]
AvailabilityRequirement = Literal["standard", "high", "critical"]
OpsPreference = Literal["managed_services", "balanced", "self_managed_ok"]


class ProfileValues(TypedDict):
    """Persisted characteristics inferred from an architecture document."""

    scale: Scale
    traffic_pattern: TrafficPattern
    latency_sensitivity_score: float
    processing_style: ProcessingStyle
    data_intensity_score: float
    availability_requirement: AvailabilityRequirement
    ops_preference: OpsPreference
    budget_sensitivity_score: float
