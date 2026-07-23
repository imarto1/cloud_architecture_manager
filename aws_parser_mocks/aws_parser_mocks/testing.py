"""Test utilities for running the bundled LocalStack mock clouds."""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import as_file, files


@contextmanager
def running_mock_clouds(project_name: str) -> Iterator[None]:
    """Start the bundled mock clouds and remove their containers and volumes afterward."""
    compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
    with as_file(compose_resource) as compose_file:
        command = ["docker", "compose", "--parallel", "10", "-f", str(compose_file), "-p", project_name]
        try:
            subprocess.run([*command, "up", "--detach", "--wait"], check=True)
            yield
        finally:
            subprocess.run(
                [*command, "down", "--volumes", "--remove-orphans"],
                check=False,
            )
