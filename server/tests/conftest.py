"""Fixtures for server API tests."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from aws_parser_mocks.testing import find_free_port_range, running_mock_clouds
from fastapi.testclient import TestClient

import server.main as api
from server.architecture_service import ArchitectureService


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[TestClient, ArchitectureService]]:
    """Provide an API client backed by an isolated, already-created SQLite database."""
    database_path = tmp_path / "architectures.sqlite"
    service = ArchitectureService(database_path)
    service.create_schema()
    monkeypatch.setattr(api, "architecture_service", service)
    monkeypatch.setattr(api, "DATABASE_PATH", database_path)

    with TestClient(api.app) as test_client:
        yield test_client, service


@pytest.fixture(scope="session")
def mock_clouds() -> Iterator[dict[str, str]]:
    """Deploy the bundled mock clouds once and tear them down after the test session."""
    if shutil.which("docker") is None:
        pytest.skip("Docker is required for server integration tests")

    docker_info = subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if docker_info.returncode != 0:
        pytest.skip("Docker is not available")

    port_base = find_free_port_range(10)
    with running_mock_clouds("server-api-tests", port_base) as endpoints:
        yield endpoints
