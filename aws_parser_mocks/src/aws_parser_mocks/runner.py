"""Optional Docker-backed mock-cloud runner."""

from __future__ import annotations

from aws_parser.cli import discover_container_endpoints
from aws_parser.models import Architecture
from aws_parser_mocks.compose import MockComposeProject

DEFAULT_MOCK_PROJECT = "aws-parser-mocks"


def parse_mocks(
    project_name: str = DEFAULT_MOCK_PROJECT,
    region: str = "us-east-1",
    services: set[str] | None = None,
) -> list[Architecture]:
    """Deploy bundled LocalStack mocks and return one parsed architecture per container.

    Containers and named volumes remain deployed after parsing. Install the
    ``mocks`` extra to use this feature.
    """
    MockComposeProject(project_name).up()

    container_endpoints = discover_container_endpoints(project_name)

    from aws_parser import parse

    return [
        parse(endpoint, container_name, region, services)
        for container_name, endpoint in sorted(container_endpoints.items())
    ]


def teardown_mocks(project_name: str = DEFAULT_MOCK_PROJECT) -> None:
    """Remove the bundled mock containers, networks, and named volumes."""
    MockComposeProject(project_name).down()
