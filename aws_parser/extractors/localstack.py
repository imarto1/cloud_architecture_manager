"""Extract observed AWS resources from a LocalStack endpoint."""

from __future__ import annotations

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError

from aws_parser.DTOs.architecture import Architecture
from aws_parser.extractors.aws_discoverers import DEFAULT_DISCOVERERS, ResourceDiscoverer


ACTIVE_STATUSES = {"running", "available"}
INTERNAL_HEALTH_SERVICES = {"sqs-query"}
class LocalStackArchitectureExtractor:
    """Discover resources without inferring a workload's purpose."""

    def __init__(
        self,
        endpoint: str,
        region: str = "us-east-1",
        services: set[str] | None = None,
        discoverers: dict[str, ResourceDiscoverer] | None = None,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.region = region
        self.requested_services = services
        self.discoverers = discoverers or DEFAULT_DISCOVERERS

    def extract(self) -> Architecture:
        enabled_services = self._enabled_services()
        discoverable_services = enabled_services - INTERNAL_HEALTH_SERVICES
        services_to_scan = discoverable_services if self.requested_services is None else self.requested_services
        supported_services = set(self.discoverers)
        warnings = [
            f"Unsupported service: {service}"
            for service in sorted(services_to_scan - supported_services)
        ]
        warnings.extend(
            f"Enabled service not available at endpoint: {service}"
            for service in sorted(services_to_scan - enabled_services)
            if service in supported_services
        )
        errors: dict[str, str] = {}
        resources = []

        for service in sorted(services_to_scan & enabled_services & supported_services):
            try:
                resources.extend(self.discoverers[service].discover(self._client(service), self.region))
            except (BotoCoreError, ClientError) as error:
                errors[service] = str(error)

        return Architecture(
            name=f"LocalStack {self.endpoint}",
            description="Observed resources; no workload purpose has been inferred.",
            resources=resources,
            metadata={
                "provider": "localstack",
                "endpoint": self.endpoint,
                "region": self.region,
                "enabled_services": sorted(enabled_services),
                "unsupported_services": sorted(discoverable_services - supported_services),
                "ignored_health_services": sorted(enabled_services & INTERNAL_HEALTH_SERVICES),
                "warnings": warnings,
                "discovery_errors": errors,
            },
        )

    def _enabled_services(self) -> set[str]:
        response = requests.get(f"{self.endpoint}/_localstack/health", timeout=10)
        response.raise_for_status()
        services = response.json().get("services", {})
        return {
            service
            for service, status in services.items()
            if status in ACTIVE_STATUSES
        }

    def _client(self, service: str):
        return boto3.client(
            service,
            endpoint_url=self.endpoint,
            region_name=self.region,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
