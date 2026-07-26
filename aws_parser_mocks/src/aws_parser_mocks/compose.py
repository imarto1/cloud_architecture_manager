"""Docker Compose lifecycle for bundled mock architectures."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import as_file, files


@dataclass(frozen=True)
class MockComposeProject:
    """Run the packaged Compose project with a stable project name."""

    name: str
    environment: Mapping[str, str] | None = None

    def up(self, parallelism: int = 10) -> None:
        self._run(
            "--parallel",
            str(parallelism),
            "up",
            "--detach",
            "--wait",
        )

    def down(self, *, check: bool = True) -> None:
        self._run(
            "down",
            "--volumes",
            "--remove-orphans",
            check=check,
        )

    def _run(self, *arguments: str, check: bool = True) -> None:
        compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
        environment = os.environ.copy()
        if self.environment:
            environment.update(self.environment)

        with as_file(compose_resource) as compose_file:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "--file",
                    str(compose_file),
                    "--project-name",
                    self.name,
                    *arguments,
                ],
                check=check,
                env=environment,
            )
