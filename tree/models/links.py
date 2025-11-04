"""HATEOAS link models for hypermedia navigation."""

from pydantic import BaseModel, Field


class Link(BaseModel):
    """A hypermedia link with optional metadata."""

    href: str = Field(..., description="URL of the linked resource")
    title: str | None = Field(None, description="Human-readable description of the link")
    method: str = Field("GET", description="HTTP method for this link")


class NavigationLinks(BaseModel):
    """All navigation links available from a node (zipper operations)."""

    self: Link = Field(..., description="Link to this node")
    root: Link = Field(..., description="Link to the root node")

    # Zipper navigation
    up: Link | None = Field(None, description="Link to parent node (zipper: up)")
    down: Link | None = Field(None, description="Link to first child (zipper: down)")
    left: Link | None = Field(None, description="Link to previous sibling (zipper: left)")
    right: Link | None = Field(None, description="Link to next sibling (zipper: right)")

    # Child access
    children: Link | None = Field(None, description="Link to all children of this node")

    # Traversal helpers
    next_dfs: Link | None = Field(None, description="Next node in depth-first order")
    next_bfs: Link | None = Field(None, description="Next node in breadth-first order")
    prev_dfs: Link | None = Field(None, description="Previous node in depth-first order")


class Operation(BaseModel):
    """An available operation with its availability status."""

    href: str | None = Field(None, description="URL for this operation")
    method: str | None = Field(None, description="HTTP method for this operation")
    accepts: str | None = Field(None, description="Content-Type accepted by this operation")
    available: bool = Field(..., description="Whether this operation is currently available")
    reason: str | None = Field(
        None, description="Explanation if operation is unavailable"
    )


class OperationsDict(BaseModel):
    """All operations available on a node."""

    modify: Operation = Field(..., description="Update node description or metadata")
    delete: Operation = Field(..., description="Delete this node")
    expand: Operation = Field(..., description="Expand leaf node into branch with children")
    collapse: Operation = Field(..., description="Collapse branch node into leaf")
