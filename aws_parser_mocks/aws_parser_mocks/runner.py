"""Optional Docker-backed mock-cloud runner."""

from __future__ import annotations

import subprocess
from importlib.resources import as_file, files

from aws_parser.DTOs import Architecture


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
    try:
        import docker
    except ImportError as error:
        raise RuntimeError("Install optional mock support with 'pip install aws_parser[mocks]'.") from error

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

    docker_client = docker.from_env()
    containers = docker_client.containers.list(
        filters={"label": f"com.docker.compose.project={project_name}"}
    )
    endpoints = []
    for container in containers:
        bindings = container.attrs["NetworkSettings"]["Ports"].get("4566/tcp")
        if bindings:
            host = bindings[0]["HostIp"]
            endpoints.append(f"http://{'127.0.0.1' if host == '0.0.0.0' else host}:{bindings[0]['HostPort']}")

    from aws_parser import parse

    return [parse(endpoint, region, services) for endpoint in sorted(endpoints)]
