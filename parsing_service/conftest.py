import pytest
import os
import requests
import time
from requests.exceptions import ConnectionError

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "mock", "aws", "docker-compose.yml")


@pytest.fixture(scope="session")
def docker_compose_command():
    """Start all independent mock clouds concurrently."""
    return "docker compose --parallel 10"

def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            health = response.json()
            # Ensure required services are in 'running' or 'available' state
            services = health.get("services", {})
            required_services = ["s3", "ec2", "dynamodb", "iam", "sqs"]
            for svc in required_services:
                status = services.get(svc)
                if status not in ["running", "available"]:
                    return False
            return True
    except (ConnectionError, requests.exceptions.RequestException):
        return False

@pytest.fixture(scope="session")
def localstack_service(docker_ip, docker_services):
    """Ensure that LocalStack is up and responsive."""
    if not os.path.exists("/var/run/docker.sock") and os.name != 'nt':
        pytest.skip("Docker not available")
    
    urls = [f"http://localhost:{port}/_localstack/health" for port in range(4566, 4576)]
    try:
        docker_services.wait_until_responsive(
            timeout=60.0, pause=0.5, check=lambda: all(is_responsive(url) for url in urls)
        )
    except Exception as e:
        pytest.skip(f"LocalStack failed to start: {e}")
    return urls

@pytest.fixture(scope="session", autouse=True)
def parsing_service_tests_setup(localstack_service):
    """Auto-use fixture to deploy mock AWS before running parsing_service tests."""
    return localstack_service
