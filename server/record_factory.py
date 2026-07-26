"""Creation of persistence records from parsed architecture documents."""

from __future__ import annotations

import json
import uuid
from typing import Any

from server.models import ArchitectureRecord
from server.profiling import calculate_profile


def create_architecture_record(document: dict[str, Any]) -> ArchitectureRecord:
    """Create a complete persistence record from a parsed architecture."""
    profile = calculate_profile(document)
    return ArchitectureRecord(
        id=str(uuid.uuid4()),
        name=document["name"],
        architecture_json=json.dumps(document),
        profile_metadata=json.dumps(profile.metadata),
        **profile.values,
    )
