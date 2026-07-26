"""Unit tests for the optional mock runner."""

from __future__ import annotations

from unittest.mock import Mock

import aws_parser
from aws_parser.models import Architecture
from aws_parser_mocks import runner


def test_parse_mocks_uses_container_names_for_architectures(monkeypatch) -> None:
    compose_project = Mock()
    compose_factory = Mock(return_value=compose_project)
    monkeypatch.setattr(
        runner,
        "discover_container_endpoints",
        lambda _project_name: {
            "mock-web-1": "http://127.0.0.1:4566",
            "mock-api-1": "http://127.0.0.1:4567",
        },
    )
    monkeypatch.setattr(runner, "MockComposeProject", compose_factory)

    calls = []

    def fake_parse(endpoint, name, region, services):
        calls.append((endpoint, name, region, services))
        return Architecture(name=name, metadata={"endpoint": endpoint})

    monkeypatch.setattr(aws_parser, "parse", fake_parse)

    architectures = runner.parse_mocks(
        project_name="mock",
        region="eu-west-1",
        services={"s3"},
    )

    compose_factory.assert_called_once_with("mock")
    compose_project.up.assert_called_once_with()
    assert [architecture.name for architecture in architectures] == [
        "mock-api-1",
        "mock-web-1",
    ]
    assert calls == [
        ("http://127.0.0.1:4567", "mock-api-1", "eu-west-1", {"s3"}),
        ("http://127.0.0.1:4566", "mock-web-1", "eu-west-1", {"s3"}),
    ]


def test_teardown_mocks_removes_containers_and_volumes(monkeypatch) -> None:
    compose_project = Mock()
    compose_factory = Mock(return_value=compose_project)
    monkeypatch.setattr(runner, "MockComposeProject", compose_factory)

    runner.teardown_mocks("mock")

    compose_factory.assert_called_once_with("mock")
    compose_project.down.assert_called_once_with()
