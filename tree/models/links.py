"""HATEOAS link models for hypermedia navigation."""

from pydantic import BaseModel, Field


class Link(BaseModel):
    """A hypermedia link with optional metadata."""

    href: str = Field(..., description="URL of the linked resource")
    title: str | None = Field(None, description="Human-readable description of the link")

    model_config = {"extra": "allow"}  # Allow additional fields if needed
