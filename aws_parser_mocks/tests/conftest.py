from collections.abc import Iterator
from importlib.resources import as_file, files

import pytest
import requests


@pytest.fixture(scope="session")
def docker_compose_file() -> Iterator[str]:
    compose_resource = files("aws_parser_mocks").joinpath("assets/docker-compose.yml")
    with as_file(compose_resource) as compose_path:
        yield str(compose_path)


@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    """Start all independent mock clouds concurrently."""
    return "docker compose --parallel 10"


def is_responsive(url: str) -> bool:
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
    except (requests.RequestException, ValueError):
        return False

    services = response.json().get("services", {})
    required_services = {"s3", "ec2", "dynamodb", "iam", "sqs"}
    healthy_states = {"running", "available"}
    return all(services.get(service) in healthy_states for service in required_services)


@pytest.fixture(scope="session")
def localstack_service(docker_services) -> list[str]:
    """Ensure that LocalStack is up and responsive."""
    urls = [f"http://localhost:{port}/_localstack/health" for port in range(4566, 4576)]
    docker_services.wait_until_responsive(
        timeout=60.0,
        pause=0.5,
        check=lambda: all(is_responsive(url) for url in urls),
    )
    return urls
