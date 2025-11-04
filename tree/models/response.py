"""Response schemas for API endpoints."""

from typing import Any

from pydantic import BaseModel, Field

from .links import NavigationLinks, OperationsDict


class Breadcrumb(BaseModel):
    """A single breadcrumb in the path from root to current node."""

    id: str = Field(..., description="Node ID")
    description: str = Field(..., description="Node description")


class Context(BaseModel):
    """Context information about a node's position in the tree (zipper context)."""

    depth: int = Field(..., ge=0, description="Distance from root (root has depth 0)")
    sibling_position: int = Field(
        ..., ge=0, description="Position among siblings (0-indexed)"
    )
    total_siblings: int = Field(..., ge=1, description="Total number of siblings including self")
    has_children: bool = Field(..., description="Whether this node has children")
    children_count: int = Field(..., ge=0, description="Number of direct children")
    breadcrumbs: list[Breadcrumb] = Field(
        default_factory=list, description="Path from root to parent of this node"
    )


class NodeResponse(BaseModel):
    """Full node response with data, context, links, and operations (zipper + HATEOAS)."""

    # Core node data
    id: str = Field(..., description="Unique node identifier")
    description: str = Field(..., description="Node description")
    is_leaf: bool = Field(..., description="Whether this node is a leaf (has no children)")
    parent_id: str | None = Field(None, description="Parent node ID (null for root)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")

    # Zipper context
    context: Context = Field(..., serialization_alias="_context", description="Position and context information")

    # HATEOAS links
    links: NavigationLinks = Field(
        ..., serialization_alias="_links", description="Available navigation links"
    )

    # Available operations
    operations: OperationsDict = Field(
        ..., serialization_alias="_operations", description="Available operations and their status"
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class NodeListResponse(BaseModel):
    """Response for endpoints that return multiple nodes."""

    nodes: list[NodeResponse] = Field(..., description="List of nodes")
    count: int = Field(..., ge=0, description="Total number of nodes returned")


class ErrorResponse(BaseModel):
    """Standard error response with helpful links."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    links: dict[str, Any] = Field(
        default_factory=dict, serialization_alias="_links", description="Links to valid states"
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
