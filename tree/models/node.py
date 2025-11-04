"""Node data models for the tree structure."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NodeBase(BaseModel):
    """Base node model with common fields."""

    description: str = Field(..., min_length=1, max_length=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeCreate(NodeBase):
    """Schema for creating a new node."""

    pass


class NodeUpdate(BaseModel):
    """Schema for updating an existing node."""

    description: str | None = Field(None, min_length=1, max_length=1000)
    parent_id: str | None = None
    metadata: dict[str, Any] | None = None


class Node(NodeBase):
    """Full node model with all fields."""

    id: str
    parent_id: str | None = None
    is_leaf: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ExpandRequest(BaseModel):
    """Request body for expanding a leaf node into a branch."""

    children: list[NodeCreate] = Field(..., min_length=1)


class CollapseRequest(BaseModel):
    """Request body for collapsing a branch node into a leaf."""

    summary: str | None = Field(None, min_length=1, max_length=1000)
