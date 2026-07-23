"""Fixtures for server API tests."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

MOCK_PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "aws_parser_mocks"
if str(MOCK_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(MOCK_PACKAGE_ROOT))

import server.main as api
from aws_parser_mocks.testing import running_mock_clouds
from server.architecture_service import ArchitectureService


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, ArchitectureService]]:
    """Provide an API client backed by an isolated, already-created SQLite database."""
    database_path = tmp_path / "architectures.sqlite"
    service = ArchitectureService(database_path)
    service.create_schema()
    monkeypatch.setattr(api, "architecture_service", service)
    monkeypatch.setattr(api, "DATABASE_PATH", database_path)

    with TestClient(api.app) as test_client:
        yield test_client, service


@pytest.fixture(scope="session")
def mock_clouds() -> Iterator[None]:
    """Deploy the bundled mock clouds once and tear them down after the test session."""
    if shutil.which("docker") is None:
        pytest.skip("Docker is required for server integration tests")

    try:
        with running_mock_clouds("server-api-tests"):
            yield
    except subprocess.CalledProcessError as error:
        pytest.skip(f"Could not start LocalStack mock clouds: {error}")
