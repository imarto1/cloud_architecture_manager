"""Tests for deterministic architecture profiling."""

from server.profiling import calculate_profile
from server.scoring import ResourceWeightedScoringPolicy


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
