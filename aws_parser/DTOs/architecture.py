"""Schema for an observed cloud-architecture JSON document."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Tag(BaseModel):
    key: str
    value: str


class Resource(BaseModel):
    id: str
    type: str
    region: str
    account_id: str
    name: str | None = None
    tags: list[Tag] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Architecture(BaseModel):
    version: str = "1.0"
    name: str
    description: str | None = None
    resources: list[Resource] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
