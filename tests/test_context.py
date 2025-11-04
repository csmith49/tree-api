"""Tests for Context and Breadcrumb models."""

import pytest
from pydantic import ValidationError

from tree.models import Breadcrumb, Context


class TestBreadcrumb:
    """Test Breadcrumb model creation and validation."""

    def test_create_valid_breadcrumb(self) -> None:
        """Test creating a valid breadcrumb."""
        breadcrumb = Breadcrumb(
            id="node-1",
            description="Test node",
        )

        assert breadcrumb.id == "node-1"
        assert breadcrumb.description == "Test node"

    def test_breadcrumb_id_required(self) -> None:
        """Test that breadcrumb ID is required."""
        with pytest.raises(ValidationError) as exc_info:
            Breadcrumb(description="Test")  # type: ignore

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_breadcrumb_description_required(self) -> None:
        """Test that breadcrumb description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Breadcrumb(id="node-1")  # type: ignore

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_breadcrumb_id_validation(self) -> None:
        """Test that breadcrumb ID follows NodeId validation."""
        with pytest.raises(ValidationError):
            Breadcrumb(id="", description="Test")  # Empty string

        with pytest.raises(ValidationError):
            Breadcrumb(id="x" * 256, description="Test")  # Too long


class TestContext:
    """Test Context model creation and validation."""

    def test_create_valid_context(self) -> None:
        """Test creating a valid context."""
        context = Context(
            depth=2,
            sibling_position=1,
            total_siblings=3,
            has_children=True,
            children_count=5,
            breadcrumbs=[
                Breadcrumb(id="root", description="Root"),
                Breadcrumb(id="node-1", description="Parent"),
            ],
        )

        assert context.depth == 2
        assert context.sibling_position == 1
        assert context.total_siblings == 3
        assert context.has_children is True
        assert context.children_count == 5
        assert len(context.breadcrumbs) == 2

    def test_create_root_context(self) -> None:
        """Test creating context for root node."""
        context = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=True,
            children_count=2,
            breadcrumbs=[],
        )

        assert context.depth == 0
        assert context.breadcrumbs == []

    def test_breadcrumbs_defaults_to_empty_list(self) -> None:
        """Test that breadcrumbs defaults to empty list."""
        context = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=False,
            children_count=0,
        )

        assert context.breadcrumbs == []
        assert isinstance(context.breadcrumbs, list)

    def test_depth_must_be_non_negative(self) -> None:
        """Test that depth must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                depth=-1,
                sibling_position=0,
                total_siblings=1,
                has_children=False,
                children_count=0,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("depth",) for e in errors)

    def test_depth_zero_is_valid(self) -> None:
        """Test that depth of 0 is valid (root)."""
        context = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=False,
            children_count=0,
        )

        assert context.depth == 0

    def test_sibling_position_must_be_non_negative(self) -> None:
        """Test that sibling_position must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                depth=0,
                sibling_position=-1,
                total_siblings=1,
                has_children=False,
                children_count=0,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sibling_position",) for e in errors)

    def test_total_siblings_must_be_at_least_one(self) -> None:
        """Test that total_siblings must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                depth=0,
                sibling_position=0,
                total_siblings=0,  # Invalid
                has_children=False,
                children_count=0,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("total_siblings",) for e in errors)

    def test_total_siblings_one_is_valid(self) -> None:
        """Test that total_siblings of 1 is valid (only child)."""
        context = Context(
            depth=1,
            sibling_position=0,
            total_siblings=1,
            has_children=False,
            children_count=0,
        )

        assert context.total_siblings == 1

    def test_children_count_must_be_non_negative(self) -> None:
        """Test that children_count must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Context(
                depth=0,
                sibling_position=0,
                total_siblings=1,
                has_children=False,
                children_count=-1,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("children_count",) for e in errors)

    def test_children_count_zero_is_valid(self) -> None:
        """Test that children_count of 0 is valid (leaf)."""
        context = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=False,
            children_count=0,
        )

        assert context.children_count == 0

    def test_has_children_matches_children_count(self) -> None:
        """Test common pattern: has_children matches children_count."""
        # Leaf node
        context_leaf = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=False,
            children_count=0,
        )
        assert context_leaf.has_children is False
        assert context_leaf.children_count == 0

        # Branch node
        context_branch = Context(
            depth=0,
            sibling_position=0,
            total_siblings=1,
            has_children=True,
            children_count=3,
        )
        assert context_branch.has_children is True
        assert context_branch.children_count == 3

    def test_context_serialization(self) -> None:
        """Test that context can be serialized to dict/JSON."""
        context = Context(
            depth=1,
            sibling_position=0,
            total_siblings=2,
            has_children=True,
            children_count=3,
            breadcrumbs=[
                Breadcrumb(id="root", description="Root"),
            ],
        )

        data = context.model_dump()
        assert data["depth"] == 1
        assert data["sibling_position"] == 0
        assert data["total_siblings"] == 2
        assert data["has_children"] is True
        assert data["children_count"] == 3
        assert len(data["breadcrumbs"]) == 1
        assert data["breadcrumbs"][0]["id"] == "root"
