"""Context models for zipper navigation."""

from pydantic import BaseModel, Field

from tree.types import NodeId


class Breadcrumb(BaseModel):
    """A single breadcrumb in the path from root to current node."""

    id: NodeId = Field(..., description="Node ID")
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
