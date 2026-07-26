"""Backward-compatible model imports.

New code should import these models from :mod:`aws_parser.models`.
"""

from . import architecture
from .architecture import Architecture, Relationship, Resource, Tag

__all__ = [
    "Architecture",
    "Relationship",
    "Resource",
    "Tag",
    "architecture",
]
