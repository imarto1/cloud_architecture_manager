"""Provisional workload profiling for parsed architecture documents."""

from __future__ import annotations

import random
from typing import Any


def calculate_profile(architecture: dict[str, Any]) -> dict[str, str | float]:
    """Return random scores until architecture-aware scoring is implemented."""
    del architecture  # Reserved for the future scoring implementation.
    return {
        "scale": random.choice(("small", "medium", "large")),
        "traffic_pattern": random.choice(
            ("steady", "bursty", "spiky", "scheduled", "unpredictable")
        ),
        "latency_sensitivity_score": random.random(),
        "processing_style": random.choice(
            ("request_response", "event_driven", "batch", "streaming")
        ),
        "data_intensity_score": random.random(),
        "availability_requirement": random.choice(("standard", "high", "critical")),
        "ops_preference": random.choice(
            ("managed_services", "balanced", "self_managed_ok")
        ),
        "budget_sensitivity_score": random.random(),
    }
