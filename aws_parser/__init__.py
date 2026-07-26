"""AWS architecture discovery package."""

from . import DTOs
from .extractors.localstack import LocalStackArchitectureExtractor
from .models import Architecture, Relationship, Resource, Tag


def parse(
    endpoint: str,
    name: str,
    region: str = "us-east-1",
    services: set[str] | None = None,
) -> Architecture:
    """Discover observed AWS-compatible resources at an endpoint."""
    return LocalStackArchitectureExtractor(endpoint, name, region, services).extract()


def parse_mocks(
    project_name: str = "aws-parser-mocks",
    region: str = "us-east-1",
    services: set[str] | None = None,
) -> list[Architecture]:
    """Deploy and parse bundled mocks after installing ``aws_parser[mocks]``."""
    try:
        from aws_parser_mocks import parse_mocks as optional_parse_mocks
    except ImportError as error:
        raise RuntimeError(
            "Install optional mock support with 'pip install aws_parser[mocks]'."
        ) from error
    return optional_parse_mocks(project_name, region, services)


def teardown_mocks(project_name: str = "aws-parser-mocks") -> None:
    """Remove bundled mock containers and volumes."""
    try:
        from aws_parser_mocks import teardown_mocks as optional_teardown_mocks
    except ImportError as error:
        raise RuntimeError(
            "Install optional mock support with 'pip install aws_parser[mocks]'."
        ) from error
    optional_teardown_mocks(project_name)


__all__ = [
    "Architecture",
    "DTOs",
    "Relationship",
    "Resource",
    "Tag",
    "parse",
    "parse_mocks",
    "teardown_mocks",
]
