"""Print observed LocalStack cloud architectures as JSON."""

from __future__ import annotations

import argparse
import json
import subprocess
from aws_parser import parse


DEFAULT_PROJECT_NAME = "cloud-architecture-mocks"


def discover_container_endpoints(project_name: str) -> dict[str, str]:
    """Return LocalStack gateway endpoints keyed by Docker container name."""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"label=com.docker.compose.project={project_name}", "--format", "{{.Names}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    endpoints = {}
    for container_name in filter(None, result.stdout.splitlines()):
        inspection = json.loads(
            subprocess.run(
                ["docker", "inspect", container_name], check=True, capture_output=True, text=True
            ).stdout
        )[0]
        gateway_binding = inspection["NetworkSettings"]["Ports"].get("4566/tcp")
        if gateway_binding:
            endpoints[container_name] = f"http://{gateway_binding[0]['HostIp']}:{gateway_binding[0]['HostPort']}"
    return endpoints


def parse_containers(
    container_endpoints: dict[str, str],
    region: str = "us-east-1",
    services: set[str] | None = None,
) -> dict[str, object]:
    """Return each discovered container's top-level architecture model."""
    architectures = {}
    for container_name, endpoint in sorted(container_endpoints.items()):
        architectures[container_name] = parse(endpoint, region, services)
    return architectures


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print LocalStack architectures as JSON.")
    parser.add_argument("--project", default=DEFAULT_PROJECT_NAME, help="Docker Compose project name.")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--service", dest="services", action="append", help="Only scan this service. Repeat as needed.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    container_endpoints = discover_container_endpoints(args.project)
    if not container_endpoints:
        raise SystemExit(f"No LocalStack containers found for Docker Compose project '{args.project}'.")

    architectures = parse_containers(
        container_endpoints,
        args.region,
        set(args.services) if args.services else None,
    )
    print(json.dumps(
        {name: architecture.model_dump(mode="json") for name, architecture in architectures.items()},
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
