import boto3
import json
import time
from pathlib import Path

import pytest
import requests

from aws_parser.extractors.localstack import LocalStackArchitectureExtractor


AWS_ACCESS_KEY_ID = "testing"
AWS_SECRET_ACCESS_KEY = "testing"
AWS_DEFAULT_REGION = "us-east-1"
ARCHITECTURES_FILE = Path(__file__).parents[1] / "aws_parser_mocks" / "assets" / "architectures.json"


def aws_client(service, endpoint):
    return boto3.client(
        service,
        endpoint_url=endpoint,
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def wait_for_scenario(architecture, timeout=30):
    """Wait for one isolated LocalStack cloud to finish its ready-hook."""
    resources = architecture["resources"]
    expected_buckets = set(resources.get("s3_buckets", []))
    expected_tables = set(resources.get("dynamodb_tables", []))
    expected_instances = set(resources.get("ec2_instances", []))
    expected_queues = set(resources.get("sqs_queues", []))
    endpoint = architecture["endpoint"]
    s3, dynamodb, sqs, ec2 = (
        aws_client(service, endpoint) for service in ("s3", "dynamodb", "sqs", "ec2")
    )

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        s3_buckets = {bucket["Name"] for bucket in s3.list_buckets()["Buckets"]}
        dynamodb_tables = set(dynamodb.list_tables()["TableNames"])
        instance_architectures = {
            tag["Value"]
            for reservation in ec2.describe_instances()["Reservations"]
            for instance in reservation["Instances"]
            for tag in instance.get("Tags", [])
            if tag["Key"] == "ArchitectureId"
        }
        queue_names = {
            queue_url.rsplit("/", 1)[-1]
            for queue_url in sqs.list_queues().get("QueueUrls", [])
        }
        if (
            expected_buckets <= s3_buckets
            and expected_tables <= dynamodb_tables
            and expected_instances <= instance_architectures
            and expected_queues <= queue_names
        ):
            return s3_buckets, dynamodb_tables, instance_architectures, queue_names
        time.sleep(0.5)

    pytest.fail(f"LocalStack did not finish seeding the {architecture['id']} cloud")


def test_all_mock_clouds_are_up(localstack_service):
    """Every isolated cloud is reachable and exposes the required AWS services."""
    required_services = {"s3", "ec2", "dynamodb", "iam", "sqs"}

    assert len(localstack_service) == 10
    for health_url in localstack_service:
        response = requests.get(health_url, timeout=5)
        assert response.status_code == 200
        services = response.json()["services"]
        assert {
            service for service in required_services
            if services.get(service) in {"running", "available"}
        } == required_services


def test_scanner_extracts_resources_without_inferring_purpose(localstack_service):
    """The parser observes each cloud from its endpoint, not fixture metadata or names."""
    architectures = json.loads(ARCHITECTURES_FILE.read_text())["architectures"]

    for architecture in architectures:
        discovered = LocalStackArchitectureExtractor(architecture["endpoint"]).extract()

        assert discovered.metadata["endpoint"] == architecture["endpoint"]
        assert "purpose" not in discovered.metadata
        assert discovered.resources


def test_scanner_warns_for_unsupported_requested_service(localstack_service):
    endpoint = "http://localhost:4566"
    discovered = LocalStackArchitectureExtractor(endpoint, services={"invalid-service"}).extract()

    assert discovered.resources == []
    assert discovered.metadata["warnings"] == ["Unsupported service: invalid-service"]


def test_architecture_scenarios_are_isolated_clouds(localstack_service):
    """Each use case has its own endpoint and contains only its declared resources."""
    architectures = json.loads(ARCHITECTURES_FILE.read_text())["architectures"]
    expected_use_cases = {
        "web_application", "public_api", "ecommerce", "real_time_analytics",
        "batch_processing", "event_processing", "media_delivery", "internal_tool",
        "iot_ingestion", "ml_inference",
    }

    assert len(architectures) == 10
    assert {architecture["use_case"] for architecture in architectures} == expected_use_cases
    assert len({architecture["endpoint"] for architecture in architectures}) == 10

    for architecture in architectures:
        buckets, tables, instances, queues = wait_for_scenario(architecture)
        resources = architecture["resources"]
        assert buckets == set(resources.get("s3_buckets", []))
        assert tables == set(resources.get("dynamodb_tables", []))
        assert instances == set(resources.get("ec2_instances", []))
        assert queues == set(resources.get("sqs_queues", []))


def test_web_application_cloud_is_accessible(localstack_service):
    architectures = json.loads(ARCHITECTURES_FILE.read_text())["architectures"]
    web_application = next(item for item in architectures if item["id"] == "web-application")
    buckets, tables, instances, _ = wait_for_scenario(web_application)

    assert buckets == {"web-application-assets"}
    assert tables == {"WebApplicationSessions"}
    assert instances == {"web-application"}
