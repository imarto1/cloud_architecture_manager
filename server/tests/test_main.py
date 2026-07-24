"""Tests for the architecture API."""

from __future__ import annotations

import json
from typing import NoReturn

from requests import ConnectionError

import server.main as api
from server.models import ArchitectureRecord


def make_record() -> ArchitectureRecord:
    return ArchitectureRecord(
        id="architecture-1",
        name="Test architecture",
        architecture_json=json.dumps({"name": "Test architecture", "resources": []}),
        scale="small",
        traffic_pattern="steady",
        latency_sensitivity_score=0.2,
        processing_style="batch",
        data_intensity_score=0.3,
        availability_requirement="standard",
        ops_preference="balanced",
        budget_sensitivity_score=0.4,
    )


def raise_connection_error(*_args: object) -> NoReturn:
    raise ConnectionError("connection refused")


def test_get_architectures_returns_saved_records(client) -> None:
    test_client, service = client
    service.create(make_record())

    response = test_client.get("/architectures")

    assert response.status_code == 200
    body = response.json()[0]
    assert body["id"] == "architecture-1"
    assert body["name"] == "Test architecture"
    assert body["architecture"] == {"name": "Test architecture", "resources": []}
    assert body["profile_metadata"] == {}
    assert body["scale"] == "small"
    assert body["traffic_pattern"] == "steady"
    assert body["latency_sensitivity_score"] == 0.2
    assert body["processing_style"] == "batch"
    assert body["data_intensity_score"] == 0.3
    assert body["availability_requirement"] == "standard"
    assert body["ops_preference"] == "balanced"
    assert body["budget_sensitivity_score"] == 0.4
    assert body["inserted_at"]


def test_get_architecture_excludes_optional_data_by_default(client) -> None:
    test_client, service = client
    service.create(make_record())

    response = test_client.get("/architectures/architecture-1")

    assert response.status_code == 200
    assert response.json()["id"] == "architecture-1"
    assert "profile_metadata" not in response.json()
    assert "architecture" not in response.json()


def test_get_architecture_can_include_optional_data(client) -> None:
    test_client, service = client
    service.create(make_record())

    response = test_client.get(
        "/architectures/architecture-1"
        "?include_profile_metadata=true&include_architecture_data=true"
    )

    assert response.status_code == 200
    assert response.json()["profile_metadata"] == {}
    assert response.json()["architecture"] == {"name": "Test architecture", "resources": []}


def test_get_architecture_returns_404_for_an_unknown_id(client) -> None:
    test_client, _ = client

    response = test_client.get("/architectures/unknown")

    assert response.status_code == 404
    assert response.json() == {"detail": "Architecture not found."}


def test_parse_architecture_saves_discovered_mock_architecture(client, mock_clouds) -> None:
    test_client, service = client

    response = test_client.post(
        "/architectures/parse",
        json={"endpoint": mock_clouds["web_application"], "services": ["s3"]},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["architecture"]["metadata"]["endpoint"] == mock_clouds["web_application"]
    assert body["inserted_at"]
    assert body["profile_metadata"]["scoring_version"] == "1"
    assert len(service.list()) == 1


def test_parse_architecture_returns_502_when_endpoint_is_unreachable(client, monkeypatch) -> None:
    test_client, service = client
    monkeypatch.setattr(
        api,
        "parse",
        raise_connection_error,
    )

    response = test_client.post("/architectures/parse", json={"endpoint": "http://unreachable"})

    assert response.status_code == 502
    assert response.json() == {"detail": "Could not reach the architecture endpoint."}
    assert service.list() == []
