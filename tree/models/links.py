"""HATEOAS link models for hypermedia navigation."""

from pydantic import BaseModel, Field

from tree.types import NodeId


class Link(BaseModel):
    """A hypermedia link with optional metadata."""

    href: NodeId = Field(..., description="Node ID or URL of the linked resource")
    title: str | None = Field(None, description="Human-readable description of the link")

    model_config = {"extra": "allow"}  # Allow additional fields if needed
