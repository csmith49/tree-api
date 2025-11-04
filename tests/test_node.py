"""Tests for Node model."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from tree.models import Node


class TestNode:
    """Test Node model creation and validation."""

    def test_create_valid_node(self) -> None:
        """Test creating a valid node with all fields."""
        now = datetime.now()
        node = Node(
            id="node-1",
            parent_id="root",
            description="Test node",
            metadata={"key": "value"},
            is_leaf=False,
            created_at=now,
            updated_at=now,
        )

        assert node.id == "node-1"
        assert node.parent_id == "root"
        assert node.description == "Test node"
        assert node.metadata == {"key": "value"}
        assert node.is_leaf is False
        assert node.created_at == now
        assert node.updated_at == now

    def test_create_root_node(self) -> None:
        """Test creating a root node (no parent)."""
        now = datetime.now()
        node = Node(
            id="root",
            parent_id=None,
            description="Root node",
            is_leaf=True,
            created_at=now,
            updated_at=now,
        )

        assert node.id == "root"
        assert node.parent_id is None
        assert node.description == "Root node"
        assert node.metadata == {}  # Default empty dict

    def test_description_required(self) -> None:
        """Test that description is required."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Node(
                id="node-1",
                description="",  # Empty string
                created_at=now,
                updated_at=now,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_description_max_length(self) -> None:
        """Test description maximum length validation."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Node(
                id="node-1",
                description="x" * 1001,  # Too long
                created_at=now,
                updated_at=now,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_description_exactly_max_length(self) -> None:
        """Test description at exactly max length is valid."""
        now = datetime.now()
        node = Node(
            id="node-1",
            description="x" * 1000,  # Exactly at max
            created_at=now,
            updated_at=now,
        )

        assert len(node.description) == 1000

    def test_node_id_required(self) -> None:
        """Test that node ID is required."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Node(
                description="Test",
                created_at=now,
                updated_at=now,
            )  # type: ignore

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_node_id_empty_string_invalid(self) -> None:
        """Test that empty string node ID is invalid."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Node(
                id="",
                description="Test",
                created_at=now,
                updated_at=now,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_node_id_too_long(self) -> None:
        """Test that node ID longer than 255 chars is invalid."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Node(
                id="x" * 256,
                description="Test",
                created_at=now,
                updated_at=now,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)

    def test_metadata_defaults_to_empty_dict(self) -> None:
        """Test that metadata defaults to empty dict."""
        now = datetime.now()
        node = Node(
            id="node-1",
            description="Test",
            created_at=now,
            updated_at=now,
        )

        assert node.metadata == {}
        assert isinstance(node.metadata, dict)

    def test_is_leaf_defaults_to_true(self) -> None:
        """Test that is_leaf defaults to True."""
        now = datetime.now()
        node = Node(
            id="node-1",
            description="Test",
            created_at=now,
            updated_at=now,
        )

        assert node.is_leaf is True

    def test_metadata_custom_types(self) -> None:
        """Test that metadata can contain various types."""
        now = datetime.now()
        node = Node(
            id="node-1",
            description="Test",
            metadata={
                "string": "value",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "list": [1, 2, 3],
                "nested": {"key": "value"},
            },
            created_at=now,
            updated_at=now,
        )

        assert node.metadata["string"] == "value"
        assert node.metadata["number"] == 42
        assert node.metadata["float"] == 3.14
        assert node.metadata["bool"] is True
        assert node.metadata["list"] == [1, 2, 3]
        assert node.metadata["nested"] == {"key": "value"}

    def test_node_serialization(self) -> None:
        """Test that node can be serialized to dict/JSON."""
        now = datetime.now()
        node = Node(
            id="node-1",
            parent_id="root",
            description="Test",
            metadata={"key": "value"},
            is_leaf=False,
            created_at=now,
            updated_at=now,
        )

        data = node.model_dump()
        assert data["id"] == "node-1"
        assert data["parent_id"] == "root"
        assert data["description"] == "Test"
        assert data["metadata"] == {"key": "value"}
        assert data["is_leaf"] is False

        # Test JSON mode
        json_data = node.model_dump(mode="json")
        assert isinstance(json_data["created_at"], str)
        assert isinstance(json_data["updated_at"], str)
