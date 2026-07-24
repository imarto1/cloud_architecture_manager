"""Public entry point for architecture profiling."""

from __future__ import annotations

from typing import Any

from server.scoring import ProfileResult, ResourceWeightedScoringPolicy


DEFAULT_SCORING_POLICY = ResourceWeightedScoringPolicy()


def calculate_profile(architecture: dict[str, Any]) -> ProfileResult:
    """Calculate a profile with the default resource-weighted policy."""
    return DEFAULT_SCORING_POLICY.score(architecture)
