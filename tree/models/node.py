"""Node data models for the tree structure."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from tree.types import NodeId


class Node(BaseModel):
    """Core node model representing a single node in the tree."""

    id: NodeId
    parent_id: NodeId | None = None
    description: str = Field(..., min_length=1, max_length=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_leaf: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
