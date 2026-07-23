"""AWS architecture discovery package."""

from . import DTOs
from .DTOs.architecture import Architecture, Relationship, Resource, Tag
from .extractors.localstack import LocalStackArchitectureExtractor


def parse(
    endpoint: str,
    region: str = "us-east-1",
    services: set[str] | None = None,
) -> Architecture:
    """Discover observed AWS-compatible resources at an endpoint."""
    return LocalStackArchitectureExtractor(endpoint, region, services).extract()


def parse_mocks(*args, **kwargs):
    """Deploy and parse bundled mocks after installing ``aws_parser[mocks]``."""
    try:
        from aws_parser_mocks import parse_mocks as optional_parse_mocks
    except ImportError as error:
        raise RuntimeError("Install optional mock support with 'pip install aws_parser[mocks]'.") from error
    return optional_parse_mocks(*args, **kwargs)


__all__ = [
    "parse",
    "parse_mocks",
    "DTOs",
    "Architecture",
    "Relationship",
    "Resource",
    "Tag",
]
