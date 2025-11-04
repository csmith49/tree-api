"""Tests for type aliases and validation."""

import pytest
from pydantic import BaseModel, Field, ValidationError

from tree.types import NodeId


class TestNodeIdTypeAlias:
    """Test NodeId type alias validation."""

    def test_valid_node_id(self) -> None:
        """Test that valid node IDs are accepted."""

        class TestModel(BaseModel):
            node_id: NodeId

        # Short ID
        model1 = TestModel(node_id="a")
        assert model1.node_id == "a"

        # Common format
        model2 = TestModel(node_id="node-123")
        assert model2.node_id == "node-123"

        # UUID-like format
        model3 = TestModel(node_id="550e8400-e29b-41d4-a716-446655440000")
        assert model3.node_id == "550e8400-e29b-41d4-a716-446655440000"

        # Path-like format
        model4 = TestModel(node_id="/nodes/node-1")
        assert model4.node_id == "/nodes/node-1"

    def test_node_id_empty_string_invalid(self) -> None:
        """Test that empty string is invalid for NodeId."""

        class TestModel(BaseModel):
            node_id: NodeId

        with pytest.raises(ValidationError) as exc_info:
            TestModel(node_id="")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("node_id",) for e in errors)

    def test_node_id_too_long_invalid(self) -> None:
        """Test that NodeId longer than 255 chars is invalid."""

        class TestModel(BaseModel):
            node_id: NodeId

        with pytest.raises(ValidationError) as exc_info:
            TestModel(node_id="x" * 256)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("node_id",) for e in errors)

    def test_node_id_at_max_length_valid(self) -> None:
        """Test that NodeId at exactly 255 chars is valid."""

        class TestModel(BaseModel):
            node_id: NodeId

        model = TestModel(node_id="x" * 255)
        assert len(model.node_id) == 255

    def test_optional_node_id(self) -> None:
        """Test that Optional[NodeId] works correctly."""

        class TestModel(BaseModel):
            node_id: NodeId | None = None

        # With value
        model1 = TestModel(node_id="node-1")
        assert model1.node_id == "node-1"

        # Without value
        model2 = TestModel()
        assert model2.node_id is None

        # Explicit None
        model3 = TestModel(node_id=None)
        assert model3.node_id is None

    def test_node_id_in_list(self) -> None:
        """Test NodeId in list type annotations."""

        class TestModel(BaseModel):
            node_ids: list[NodeId]

        model = TestModel(node_ids=["node-1", "node-2", "node-3"])
        assert model.node_ids == ["node-1", "node-2", "node-3"]

    def test_node_id_in_dict(self) -> None:
        """Test NodeId in dict type annotations."""

        class TestModel(BaseModel):
            nodes: dict[NodeId, str]

        model = TestModel(
            nodes={
                "node-1": "First node",
                "node-2": "Second node",
            }
        )
        assert model.nodes["node-1"] == "First node"
        assert model.nodes["node-2"] == "Second node"

    def test_node_id_validation_in_nested_model(self) -> None:
        """Test NodeId validation in nested models."""

        class ChildModel(BaseModel):
            child_id: NodeId

        class ParentModel(BaseModel):
            parent_id: NodeId
            child: ChildModel

        model = ParentModel(
            parent_id="parent-1",
            child=ChildModel(child_id="child-1"),
        )

        assert model.parent_id == "parent-1"
        assert model.child.child_id == "child-1"

    def test_node_id_with_field_default(self) -> None:
        """Test NodeId with Field default values."""

        class TestModel(BaseModel):
            node_id: NodeId = Field(default="default-id")

        # With value
        model1 = TestModel(node_id="custom-id")
        assert model1.node_id == "custom-id"

        # Without value (uses default)
        model2 = TestModel()
        assert model2.node_id == "default-id"

    def test_node_id_consistency_across_models(self) -> None:
        """Test that NodeId is consistent across different model types."""
        from datetime import datetime

        from tree.models import Breadcrumb, Link, Node

        # All these should accept the same ID format
        test_id = "consistent-id-123"

        breadcrumb = Breadcrumb(id=test_id, description="Test")
        link = Link(href=test_id)
        node = Node(
            id=test_id,
            description="Test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert breadcrumb.id == test_id
        assert link.href == test_id
        assert node.id == test_id

    def test_node_id_special_characters(self) -> None:
        """Test NodeId with various special characters."""

        class TestModel(BaseModel):
            node_id: NodeId

        # Hyphens
        model1 = TestModel(node_id="node-with-hyphens")
        assert model1.node_id == "node-with-hyphens"

        # Underscores
        model2 = TestModel(node_id="node_with_underscores")
        assert model2.node_id == "node_with_underscores"

        # Dots
        model3 = TestModel(node_id="node.with.dots")
        assert model3.node_id == "node.with.dots"

        # Slashes (path-like)
        model4 = TestModel(node_id="parent/child/node")
        assert model4.node_id == "parent/child/node"

        # Numbers
        model5 = TestModel(node_id="123456")
        assert model5.node_id == "123456"
