import json
from subprocess import CompletedProcess

from aws_parser import parse, parse_mocks
from aws_parser.DTOs import Architecture
from aws_parser.cli import discover_container_endpoints, main, parse_containers


class FakeExtractor:
    def __init__(self, endpoint, region, services):
        self.endpoint = endpoint

    def extract(self):
        return Architecture(name="observed-cloud", metadata={"endpoint": self.endpoint})


def test_parse_is_exported_as_the_package_api(monkeypatch):
    monkeypatch.setattr("aws_parser.LocalStackArchitectureExtractor", FakeExtractor)

    architecture = parse("http://localhost:4566")

    assert architecture.metadata == {"endpoint": "http://localhost:4566"}


def test_parse_mocks_is_exported_as_optional_mock_api():
    assert callable(parse_mocks)


def test_discover_container_endpoints_uses_gateway_port(monkeypatch):
    responses = iter([
        CompletedProcess([], 0, "mock-api-1\n"),
        CompletedProcess([], 0, json.dumps([{
            "NetworkSettings": {"Ports": {"4566/tcp": [{"HostIp": "127.0.0.1", "HostPort": "4566"}]}}
        }])),
    ])
    monkeypatch.setattr("aws_parser.cli.subprocess.run", lambda *args, **kwargs: next(responses))

    assert discover_container_endpoints("mock") == {"mock-api-1": "http://127.0.0.1:4566"}


def test_parse_containers_returns_top_models(monkeypatch):
    monkeypatch.setattr("aws_parser.cli.parse", lambda endpoint, region, services: FakeExtractor(endpoint, region, services).extract())

    architectures = parse_containers({"mock-api-1": "http://localhost:4566"})

    assert architectures["mock-api-1"].metadata == {"endpoint": "http://localhost:4566"}


def test_main_prints_container_architectures(monkeypatch, capsys):
    monkeypatch.setattr(
        "aws_parser.cli.discover_container_endpoints",
        lambda project: {"mock-api-1": "http://localhost:4566"},
    )
    monkeypatch.setattr("aws_parser.cli.parse", lambda endpoint, region, services: FakeExtractor(endpoint, region, services).extract())

    assert main(["--project", "mock"]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "mock-api-1": {
            "version": "1.0",
            "name": "observed-cloud",
            "description": None,
            "resources": [],
            "relationships": [],
            "metadata": {"endpoint": "http://localhost:4566"},
        }
    }
