"""Tests for the architecture API."""

from __future__ import annotations

import json

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


def test_get_architectures_returns_saved_records(client) -> None:
    test_client, service = client
    service.create(make_record())

    response = test_client.get("/architectures")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "architecture-1",
            "name": "Test architecture",
            "architecture": {"name": "Test architecture", "resources": []},
            "scale": "small",
            "traffic_pattern": "steady",
            "latency_sensitivity_score": 0.2,
            "processing_style": "batch",
            "data_intensity_score": 0.3,
            "availability_requirement": "standard",
            "ops_preference": "balanced",
            "budget_sensitivity_score": 0.4,
            "inserted_at": response.json()[0]["inserted_at"],
        }
    ]


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
    assert len(service.list()) == 1


def test_parse_architecture_returns_502_when_endpoint_is_unreachable(client, monkeypatch) -> None:
    test_client, service = client
    monkeypatch.setattr(
        api,
        "parse",
        lambda *_: (_ for _ in ()).throw(ConnectionError("connection refused")),
    )

    response = test_client.post("/architectures/parse", json={"endpoint": "http://unreachable"})

    assert response.status_code == 502
    assert response.json() == {"detail": "Could not reach the architecture endpoint."}
    assert service.list() == []
