"""Test utilities for running the bundled LocalStack mock clouds."""

from __future__ import annotations

import os
import socket
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import as_file, files


MOCK_SERVICE_NAMES = (
    "WEB_APPLICATION",
    "PUBLIC_API",
    "ECOMMERCE",
    "REAL_TIME_ANALYTICS",
    "BATCH_PROCESSING",
    "EVENT_PROCESSING",
    "MEDIA_DELIVERY",
    "INTERNAL_TOOL",
    "IOT_INGESTION",
    "ML_INFERENCE",
)


def find_free_port_range(size: int) -> int:
    """Find a contiguous localhost port range for an isolated Compose project."""
    for port_base in range(4600, 65000 - size):
        sockets = []
        try:
            for port in range(port_base, port_base + size):
                sock = socket.socket()
                sock.bind(("127.0.0.1", port))
                sockets.append(sock)
            return port_base
        except OSError:
            pass
        finally:
            for sock in sockets:
                sock.close()

    raise RuntimeError("Could not find a free localhost port range for mock clouds")


def mock_port_environment(port_base: int) -> dict[str, str]:
    """Return Compose environment variables for the requested host-port range."""
    return {
        f"{service_name}_PORT": str(port_base + offset)
        for offset, service_name in enumerate(MOCK_SERVICE_NAMES)
    }


def mock_endpoint(architecture_id: str) -> str:
    """Return the configured localhost endpoint for a mock architecture id."""
    environment_name = architecture_id.replace("-", "_").upper()
    return f"http://localhost:{os.environ[f'{environment_name}_PORT']}"


@contextmanager
def running_mock_clouds(project_name: str, port_base: int = 4566) -> Iterator[dict[str, str]]:
    """Start the bundled mock clouds and remove their containers and volumes afterward."""
    compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
    with as_file(compose_resource) as compose_file:
        command = [
            "docker",
            "compose",
            "--parallel",
            "10",
            "-f",
            str(compose_file),
            "-p",
            project_name,
        ]
        environment = os.environ.copy()
        ports = mock_port_environment(port_base)
        environment.update(ports)
        endpoints = {
            service_name.removesuffix("_PORT").lower(): f"http://localhost:{port}"
            for service_name, port in ports.items()
        }
        try:
            subprocess.run(
                [*command, "up", "--detach", "--wait"],
                check=True,
                env=environment,
            )
            yield endpoints
        finally:
            subprocess.run(
                [*command, "down", "--volumes", "--remove-orphans"],
                check=False,
                env=environment,
            )
