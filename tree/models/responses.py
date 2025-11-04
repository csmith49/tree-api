"""API response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from tree.models.context import Context
from tree.models.links import Link
from tree.types import NodeId


class NodeResponse(BaseModel):
    """Full node response with HATEOAS links and context."""

    id: NodeId
    parent_id: NodeId | None = None
    description: str = Field(..., min_length=1, max_length=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_leaf: bool = True
    created_at: datetime
    updated_at: datetime
    context: Context
    links: dict[str, Link]


class NodeCreate(BaseModel):
    """Request body for creating a new node."""

    id: NodeId
    description: str = Field(..., min_length=1, max_length=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeUpdate(BaseModel):
    """Request body for updating a node."""

    description: str | None = Field(None, min_length=1, max_length=1000)
    metadata: dict[str, Any] | None = None


class ExpandRequest(BaseModel):
    """Request body for expanding a leaf node."""

    children: list[NodeCreate]


class CollapseRequest(BaseModel):
    """Request body for collapsing a branch node."""

    summary: str | None = Field(None, min_length=1, max_length=1000)
