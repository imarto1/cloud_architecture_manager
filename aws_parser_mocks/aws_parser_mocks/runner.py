"""Optional Docker-backed mock-cloud runner."""

from __future__ import annotations

import subprocess
from importlib.resources import as_file, files

from aws_parser.DTOs import Architecture
from aws_parser.cli import discover_container_endpoints


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
    compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
    with as_file(compose_resource) as compose_file:
        subprocess.run(
            [
                "docker",
                "compose",
                "--parallel",
                "10",
                "-f",
                str(compose_file),
                "-p",
                project_name,
                "up",
                "--detach",
                "--wait",
            ],
            check=True,
        )

    container_endpoints = discover_container_endpoints(project_name)

    from aws_parser import parse

    return [
        parse(endpoint, container_name, region, services)
        for container_name, endpoint in sorted(container_endpoints.items())
    ]


def teardown_mocks(project_name: str = DEFAULT_MOCK_PROJECT) -> None:
    """Remove the bundled mock containers, networks, and named volumes."""
    compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
    with as_file(compose_resource) as compose_file:
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "-p",
                project_name,
                "down",
                "--volumes",
                "--remove-orphans",
            ],
            check=True,
        )
