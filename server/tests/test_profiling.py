"""Tests for deterministic architecture profiling."""

from server.profiling import calculate_profile
from server.scoring import ResourceWeightedScoringPolicy, ScoringConfig


def test_streaming_managed_architecture_has_explainable_profile() -> None:
    profile = calculate_profile(
        {
            "resources": [
                {"type": "aws_s3_bucket", "name": "events", "metadata": {}},
                {"type": "aws_dynamodb_table", "name": "state", "metadata": {}},
                {"type": "aws_kinesis_stream", "name": "events", "metadata": {}},
            ]
        }
    )

    assert profile.values["processing_style"] == "streaming"
    assert profile.values["traffic_pattern"] == "steady"
    assert profile.values["ops_preference"] == "managed_services"
    assert profile.values["data_intensity_score"] == 0.95
    assert profile.metadata["signals"]["processing_style"]["confidence"] == 0.9


def test_custom_data_weights_can_override_the_default_policy() -> None:
    policy = ResourceWeightedScoringPolicy(data_weights={"aws_s3_bucket": 0.8})

    profile = policy.score({"resources": [{"type": "aws_s3_bucket", "metadata": {}}]})

    assert profile.values["data_intensity_score"] == 0.8


def test_custom_configuration_controls_non_data_dimensions() -> None:
    policy = ResourceWeightedScoringPolicy(
        ScoringConfig(
            medium_scale_threshold=1,
            large_scale_threshold=2,
            latency_base_score=0.2,
            latency_hint_weight=0.3,
            latency_hints=("interactive",),
            availability_requirement="high",
            availability_confidence=0.6,
            default_budget_score=0.4,
        )
    )

    profile = policy.score(
        {
            "resources": [
                {"type": "aws_s3_bucket", "name": "interactive-assets", "metadata": {}},
                {"type": "aws_s3_bucket", "name": "archive", "metadata": {}},
            ]
        }
    )

    assert profile.values["scale"] == "medium"
    assert profile.values["latency_sensitivity_score"] == 0.5
    assert profile.values["availability_requirement"] == "high"
    assert profile.values["budget_sensitivity_score"] == 0.4
    assert profile.metadata["signals"]["availability_requirement"]["confidence"] == 0.6
