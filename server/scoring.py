"""Configurable resource-weighted architecture scoring."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping


SCORING_VERSION = "1"


@dataclass(frozen=True)
class ProfileResult:
    """Inferred profile values plus the signals that led to each conclusion."""

    values: dict[str, str | float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ScoringConfig:
    """Tunable weights, thresholds, and defaults for every profile dimension."""

    data_weights: Mapping[str, float] = field(
        default_factory=lambda: {
            "aws_s3_bucket": 0.15,
            "aws_dynamodb_table": 0.30,
            "aws_kinesis_stream": 0.50,
            "aws_sqs_queue": 0.10,
        }
    )
    scale_weights: Mapping[str, float] = field(
        default_factory=lambda: {
            "aws_s3_bucket": 1,
            "aws_dynamodb_table": 1,
            "aws_sqs_queue": 1,
            "aws_kinesis_stream": 2,
            "aws_ec2_instance": 2,
        }
    )
    managed_resource_types: frozenset[str] = frozenset(
        {"aws_s3_bucket", "aws_dynamodb_table", "aws_sqs_queue", "aws_kinesis_stream"}
    )
    medium_scale_threshold: float = 3
    large_scale_threshold: float = 7
    traffic_kinesis_confidence: float = 0.65
    traffic_queue_confidence: float = 0.55
    traffic_name_hint_confidence: float = 0.25
    traffic_default_confidence: float = 0.05
    processing_kinesis_confidence: float = 0.9
    processing_queue_confidence: float = 0.85
    processing_name_hint_confidence: float = 0.25
    processing_default_confidence: float = 0.05
    latency_base_score: float = 0.5
    latency_hint_weight: float = 0.1
    latency_hints: tuple[str, ...] = ("api", "web", "real-time", "realtime", "interactive")
    latency_hint_confidence: float = 0.2
    latency_default_confidence: float = 0.05
    availability_requirement: str = "standard"
    availability_confidence: float = 0.05
    managed_ops_confidence: float = 0.65
    balanced_ops_confidence: float = 0.55
    self_managed_ops_confidence: float = 0.5
    default_ops_confidence: float = 0.05
    on_demand_budget_score: float = 0.7
    default_budget_score: float = 0.5
    on_demand_budget_confidence: float = 0.3
    default_budget_confidence: float = 0.05


class ResourceWeightedScoringPolicy:
    """Infer a workload profile from the resources stored in an architecture JSON document."""

    def __init__(
        self,
        config: ScoringConfig | None = None,
        data_weights: Mapping[str, float] | None = None,
        scale_weights: Mapping[str, float] | None = None,
    ) -> None:
        config = config or ScoringConfig()
        if data_weights is not None:
            config = replace(config, data_weights=data_weights)
        if scale_weights is not None:
            config = replace(config, scale_weights=scale_weights)
        self.config = config

    def score(self, architecture: dict[str, Any]) -> ProfileResult:
        """Return deterministic profile values with confidence and evidence."""
        resources = architecture.get("resources", [])
        resources_by_type = self._group_by_type(resources)
        resource_counts = {
            resource_type: len(items)
            for resource_type, items in resources_by_type.items()
        }
        resource_names = self._resource_names(resources)

        scale_weight = self._weighted_total(resource_counts, self.config.scale_weights)
        data_score = min(1.0, self._weighted_total(resource_counts, self.config.data_weights))
        managed_count = sum(
            resource_counts.get(resource_type, 0)
            for resource_type in self.config.managed_resource_types
        )
        ec2_count = resource_counts.get("aws_ec2_instance", 0)
        kinesis_count = resource_counts.get("aws_kinesis_stream", 0)
        sqs_count = resource_counts.get("aws_sqs_queue", 0)

        scale = self._scale_for(scale_weight)
        traffic_pattern, traffic_confidence, traffic_evidence = self._traffic_pattern(
            kinesis_count,
            sqs_count,
            resource_names,
        )
        processing_style, processing_confidence, processing_evidence = self._processing_style(
            kinesis_count,
            sqs_count,
            resource_names,
        )
        ops_preference, ops_confidence, ops_evidence = self._ops_preference(
            managed_count,
            ec2_count,
        )
        latency_hint_count = self._latency_hint_count(resource_names)
        on_demand_tables = self._on_demand_table_count(resources_by_type)

        values = {
            "scale": scale,
            "traffic_pattern": traffic_pattern,
            "latency_sensitivity_score": min(
                1.0,
                self.config.latency_base_score + self.config.latency_hint_weight * latency_hint_count,
            ),
            "processing_style": processing_style,
            "data_intensity_score": data_score,
            "availability_requirement": self.config.availability_requirement,
            "ops_preference": ops_preference,
            "budget_sensitivity_score": (
                self.config.on_demand_budget_score
                if on_demand_tables
                else self.config.default_budget_score
            ),
        }
        metadata = self._metadata(
            resource_counts,
            len(resources),
            scale_weight,
            traffic_confidence,
            traffic_evidence,
            latency_hint_count,
            processing_confidence,
            processing_evidence,
            kinesis_count,
            ops_confidence,
            ops_evidence,
            on_demand_tables,
        )
        return ProfileResult(values=values, metadata=metadata)

    @staticmethod
    def _group_by_type(resources: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for resource in resources:
            grouped.setdefault(resource["type"], []).append(resource)
        return grouped

    @staticmethod
    def _resource_names(resources: list[dict[str, Any]]) -> str:
        return " ".join(resource.get("name", "") or "" for resource in resources).lower()

    @staticmethod
    def _weighted_total(counts: Mapping[str, int], weights: Mapping[str, float]) -> float:
        return sum(counts.get(resource_type, 0) * weight for resource_type, weight in weights.items())

    def _scale_for(self, scale_weight: float) -> str:
        if scale_weight > self.config.large_scale_threshold:
            return "large"
        if scale_weight > self.config.medium_scale_threshold:
            return "medium"
        return "small"

    def _traffic_pattern(
        self,
        kinesis_count: int,
        sqs_count: int,
        resource_names: str,
    ) -> tuple[str, float, list[str]]:
        if kinesis_count:
            return "steady", self.config.traffic_kinesis_confidence, [f"{kinesis_count} Kinesis stream(s) indicate continuous event flow."]
        if sqs_count:
            return "bursty", self.config.traffic_queue_confidence, [f"{sqs_count} SQS queue(s) can absorb bursts of work."]
        if "batch" in resource_names or "scheduled" in resource_names:
            return "scheduled", self.config.traffic_name_hint_confidence, ["A stored resource name contains a batch or scheduling hint."]
        return "unpredictable", self.config.traffic_default_confidence, ["No traffic-shape resource is currently collected."]

    def _processing_style(
        self,
        kinesis_count: int,
        sqs_count: int,
        resource_names: str,
    ) -> tuple[str, float, list[str]]:
        if kinesis_count:
            return "streaming", self.config.processing_kinesis_confidence, [f"{kinesis_count} Kinesis stream(s) were discovered."]
        if sqs_count:
            return "event_driven", self.config.processing_queue_confidence, [f"{sqs_count} SQS queue(s) were discovered."]
        if "batch" in resource_names:
            return "batch", self.config.processing_name_hint_confidence, ["A stored resource name contains a batch hint."]
        return "request_response", self.config.processing_default_confidence, ["No API, Lambda, batch, or event resource is currently collected."]

    def _ops_preference(self, managed_count: int, ec2_count: int) -> tuple[str, float, list[str]]:
        if ec2_count == 0 and managed_count:
            return (
                "managed_services",
                self.config.managed_ops_confidence,
                ["All discovered workload resources are managed AWS services."],
            )
        if ec2_count and managed_count:
            return "balanced", self.config.balanced_ops_confidence, ["Both EC2 instances and managed AWS services were discovered."]
        if ec2_count:
            return "self_managed_ok", self.config.self_managed_ops_confidence, ["Only EC2 workload compute was discovered."]
        return "balanced", self.config.default_ops_confidence, ["No workload resource was discovered."]

    def _latency_hint_count(self, resource_names: str) -> int:
        return sum(hint in resource_names for hint in self.config.latency_hints)

    @staticmethod
    def _on_demand_table_count(resources_by_type: Mapping[str, list[dict[str, Any]]]) -> int:
        return sum(
            table.get("metadata", {}).get("billing_mode") == "PAY_PER_REQUEST"
            for table in resources_by_type.get("aws_dynamodb_table", [])
        )

    def _metadata(
        self,
        resource_counts: dict[str, int],
        resource_count: int,
        scale_weight: float,
        traffic_confidence: float,
        traffic_evidence: list[str],
        latency_hint_count: int,
        processing_confidence: float,
        processing_evidence: list[str],
        kinesis_count: int,
        ops_confidence: float,
        ops_evidence: list[str],
        on_demand_tables: int,
    ) -> dict[str, Any]:
        return {
            "scoring_version": SCORING_VERSION,
            "signals": {
                "resource_counts": resource_counts,
                "scale": {
                    "confidence": min(0.8, 0.25 + 0.08 * resource_count),
                    "evidence": [f"Weighted resource count: {scale_weight}."],
                },
                "traffic_pattern": {"confidence": traffic_confidence, "evidence": traffic_evidence},
                "latency_sensitivity_score": {
                    "confidence": (
                        self.config.latency_hint_confidence
                        if latency_hint_count
                        else self.config.latency_default_confidence
                    ),
                    "evidence": (
                        [f"Resource-name latency hints: {latency_hint_count}."]
                        if latency_hint_count
                        else ["No latency or SLO configuration is currently collected."]
                    ),
                },
                "processing_style": {
                    "confidence": processing_confidence,
                    "evidence": processing_evidence,
                },
                "data_intensity_score": {
                    "confidence": min(0.75, 0.2 + 0.1 * (kinesis_count + resource_counts.get("aws_dynamodb_table", 0))),
                    "evidence": ["Weighted S3, DynamoDB, SQS, and Kinesis resource count."],
                },
                "availability_requirement": {
                    "confidence": self.config.availability_confidence,
                    "evidence": ["No redundancy, replica, or multi-AZ configuration is currently collected."],
                },
                "ops_preference": {"confidence": ops_confidence, "evidence": ops_evidence},
                "budget_sensitivity_score": {
                    "confidence": (
                        self.config.on_demand_budget_confidence
                        if on_demand_tables
                        else self.config.default_budget_confidence
                    ),
                    "evidence": (
                        [f"{on_demand_tables} DynamoDB table(s) use on-demand billing."]
                        if on_demand_tables
                        else ["No cost-control configuration is currently collected."]
                    ),
                },
            },
        }
