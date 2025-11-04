"""Tests for Link model."""

import pytest
from pydantic import ValidationError

from tree.models import Link


class TestLink:
    """Test Link model creation and validation."""

    def test_create_valid_link(self) -> None:
        """Test creating a valid link with all fields."""
        link = Link(
            href="node-1",
            title="Test node",
        )

        assert link.href == "node-1"
        assert link.title == "Test node"

    def test_create_link_without_title(self) -> None:
        """Test creating a link without optional title."""
        link = Link(href="node-1")

        assert link.href == "node-1"
        assert link.title is None

    def test_href_required(self) -> None:
        """Test that href is required."""
        with pytest.raises(ValidationError) as exc_info:
            Link()  # type: ignore

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("href",) for e in errors)

    def test_href_empty_string_invalid(self) -> None:
        """Test that empty href is invalid (NodeId validation)."""
        with pytest.raises(ValidationError) as exc_info:
            Link(href="")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("href",) for e in errors)

    def test_href_too_long_invalid(self) -> None:
        """Test that href longer than 255 chars is invalid (NodeId validation)."""
        with pytest.raises(ValidationError) as exc_info:
            Link(href="x" * 256)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("href",) for e in errors)

    def test_href_at_max_length_valid(self) -> None:
        """Test that href at exactly 255 chars is valid."""
        link = Link(href="x" * 255)

        assert len(link.href) == 255

    def test_title_can_be_none(self) -> None:
        """Test that title can be explicitly set to None."""
        link = Link(href="node-1", title=None)

        assert link.href == "node-1"
        assert link.title is None

    def test_link_with_path_href(self) -> None:
        """Test link with path-style href."""
        link = Link(href="/nodes/node-1", title="Node 1")

        assert link.href == "/nodes/node-1"
        assert link.title == "Node 1"

    def test_link_serialization(self) -> None:
        """Test that link can be serialized to dict/JSON."""
        link = Link(href="node-1", title="Test node")

        data = link.model_dump()
        assert data["href"] == "node-1"
        assert data["title"] == "Test node"

        # Test with no title
        link_no_title = Link(href="node-1")
        data_no_title = link_no_title.model_dump()
        assert data_no_title["href"] == "node-1"
        assert data_no_title["title"] is None

    def test_link_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed in Link model."""
        # The model_config has "extra": "allow"
        link = Link(
            href="node-1",
            title="Test",
            custom_field="custom_value",  # type: ignore
        )

        assert link.href == "node-1"
        assert link.title == "Test"
        # Extra field should be accessible
        data = link.model_dump()
        assert data.get("custom_field") == "custom_value"

    def test_multiple_links_different_hrefs(self) -> None:
        """Test creating multiple links with different hrefs."""
        links = {
            "self": Link(href="node-1"),
            "parent": Link(href="root", title="Root node"),
            "child": Link(href="node-1-child-1", title="First child"),
            "sibling": Link(href="node-2", title="Next sibling"),
        }

        assert links["self"].href == "node-1"
        assert links["parent"].href == "root"
        assert links["child"].href == "node-1-child-1"
        assert links["sibling"].href == "node-2"

    def test_link_equality(self) -> None:
        """Test that links with same values are equal."""
        link1 = Link(href="node-1", title="Test")
        link2 = Link(href="node-1", title="Test")

        assert link1 == link2

    def test_link_inequality(self) -> None:
        """Test that links with different values are not equal."""
        link1 = Link(href="node-1", title="Test")
        link2 = Link(href="node-2", title="Test")
        link3 = Link(href="node-1", title="Different")

        assert link1 != link2
        assert link1 != link3
