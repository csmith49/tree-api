"""Tests for TreeService."""

import pytest

from tree.services.tree import (
    CircularReferenceError,
    InvalidOperationError,
    TreeNotFoundError,
    TreeService,
)


class TestTreeServiceBasics:
    """Test basic TreeService operations."""

    def test_create_root_node(self) -> None:
        """Test creating a root node."""
        tree = TreeService()
        node = tree.create_node("root", "Root node")

        assert node.id == "root"
        assert node.description == "Root node"
        assert node.parent_id is None
        assert node.is_leaf is True
        assert tree.node_count() == 1

    def test_create_child_node(self) -> None:
        """Test creating a child node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        child = tree.create_node("child-1", "Child 1", parent_id="root")

        assert child.id == "child-1"
        assert child.parent_id == "root"
        assert child.is_leaf is True

        # Parent should no longer be a leaf
        root = tree.get_node("root")
        assert root.is_leaf is False

    def test_create_node_with_metadata(self) -> None:
        """Test creating a node with metadata."""
        tree = TreeService()
        node = tree.create_node("node-1", "Test", metadata={"key": "value"})

        assert node.metadata == {"key": "value"}

    def test_create_duplicate_node_fails(self) -> None:
        """Test that creating a duplicate node fails."""
        tree = TreeService()
        tree.create_node("node-1", "First")

        with pytest.raises(InvalidOperationError, match="already exists"):
            tree.create_node("node-1", "Duplicate")

    def test_create_node_with_invalid_parent_fails(self) -> None:
        """Test that creating a node with non-existent parent fails."""
        tree = TreeService()

        with pytest.raises(TreeNotFoundError, match="Parent node.*not found"):
            tree.create_node("child-1", "Child", parent_id="nonexistent")

    def test_create_multiple_roots_fails(self) -> None:
        """Test that creating multiple root nodes fails."""
        tree = TreeService()
        tree.create_node("root", "Root")

        with pytest.raises(InvalidOperationError, match="Root node already exists"):
            tree.create_node("root2", "Another root")


class TestTreeServiceRetrieval:
    """Test node retrieval operations."""

    def test_get_node(self) -> None:
        """Test getting a node by ID."""
        tree = TreeService()
        created = tree.create_node("node-1", "Test")
        retrieved = tree.get_node("node-1")

        assert retrieved.id == created.id
        assert retrieved.description == created.description

    def test_get_nonexistent_node_fails(self) -> None:
        """Test that getting a non-existent node fails."""
        tree = TreeService()

        with pytest.raises(TreeNotFoundError, match="not found"):
            tree.get_node("nonexistent")

    def test_get_children(self) -> None:
        """Test getting children of a node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child 1", parent_id="root")
        tree.create_node("child-2", "Child 2", parent_id="root")

        children = tree.get_children("root")
        assert len(children) == 2
        assert {c.id for c in children} == {"child-1", "child-2"}

    def test_get_children_of_leaf_returns_empty(self) -> None:
        """Test getting children of a leaf node returns empty list."""
        tree = TreeService()
        tree.create_node("root", "Root")

        children = tree.get_children("root")
        assert children == []

    def test_get_siblings(self) -> None:
        """Test getting siblings of a node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child 1", parent_id="root")
        tree.create_node("child-2", "Child 2", parent_id="root")
        tree.create_node("child-3", "Child 3", parent_id="root")

        siblings = tree.get_siblings("child-2")
        assert len(siblings) == 3
        assert {s.id for s in siblings} == {"child-1", "child-2", "child-3"}

    def test_get_siblings_of_root_returns_only_root(self) -> None:
        """Test that root node has no siblings."""
        tree = TreeService()
        tree.create_node("root", "Root")

        siblings = tree.get_siblings("root")
        assert len(siblings) == 1
        assert siblings[0].id == "root"

    def test_get_parent(self) -> None:
        """Test getting parent of a node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child 1", parent_id="root")

        parent = tree.get_parent("child-1")
        assert parent is not None
        assert parent.id == "root"

    def test_get_parent_of_root_returns_none(self) -> None:
        """Test that root node has no parent."""
        tree = TreeService()
        tree.create_node("root", "Root")

        parent = tree.get_parent("root")
        assert parent is None

    def test_get_root(self) -> None:
        """Test getting the root node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child", parent_id="root")

        root = tree.get_root()
        assert root is not None
        assert root.id == "root"

    def test_get_root_when_empty_returns_none(self) -> None:
        """Test getting root from empty tree returns None."""
        tree = TreeService()

        root = tree.get_root()
        assert root is None


class TestTreeServiceUpdate:
    """Test node update operations."""

    def test_update_description(self) -> None:
        """Test updating node description."""
        tree = TreeService()
        tree.create_node("node-1", "Original")

        updated = tree.update_node("node-1", description="Updated")
        assert updated.description == "Updated"

        retrieved = tree.get_node("node-1")
        assert retrieved.description == "Updated"

    def test_update_metadata(self) -> None:
        """Test updating node metadata."""
        tree = TreeService()
        tree.create_node("node-1", "Test", metadata={"old": "value"})

        updated = tree.update_node("node-1", metadata={"new": "data"})
        assert updated.metadata == {"new": "data"}

    def test_update_both_fields(self) -> None:
        """Test updating both description and metadata."""
        tree = TreeService()
        tree.create_node("node-1", "Original")

        updated = tree.update_node("node-1", description="New", metadata={"key": "val"})
        assert updated.description == "New"
        assert updated.metadata == {"key": "val"}

    def test_update_nonexistent_node_fails(self) -> None:
        """Test updating non-existent node fails."""
        tree = TreeService()

        with pytest.raises(TreeNotFoundError):
            tree.update_node("nonexistent", description="Test")

    def test_update_timestamp_changes(self) -> None:
        """Test that updated_at timestamp changes on update."""
        tree = TreeService()
        node = tree.create_node("node-1", "Test")
        original_time = node.updated_at

        updated = tree.update_node("node-1", description="Updated")
        assert updated.updated_at > original_time


class TestTreeServiceDelete:
    """Test node deletion operations."""

    def test_delete_leaf_node(self) -> None:
        """Test deleting a leaf node."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child", parent_id="root")

        tree.delete_node("child-1")

        assert tree.node_count() == 1
        with pytest.raises(TreeNotFoundError):
            tree.get_node("child-1")

        # Parent should become leaf again
        root = tree.get_node("root")
        assert root.is_leaf is True

    def test_delete_node_with_children_deletes_descendants(self) -> None:
        """Test that deleting a node deletes all descendants."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child 1", parent_id="root")
        tree.create_node("grandchild-1", "Grandchild 1", parent_id="child-1")

        tree.delete_node("child-1")

        assert tree.node_count() == 1
        with pytest.raises(TreeNotFoundError):
            tree.get_node("child-1")
        with pytest.raises(TreeNotFoundError):
            tree.get_node("grandchild-1")

    def test_delete_root_node_fails(self) -> None:
        """Test that deleting root node fails."""
        tree = TreeService()
        tree.create_node("root", "Root")

        with pytest.raises(InvalidOperationError, match="Cannot delete root"):
            tree.delete_node("root")

    def test_delete_nonexistent_node_fails(self) -> None:
        """Test deleting non-existent node fails."""
        tree = TreeService()

        with pytest.raises(TreeNotFoundError):
            tree.delete_node("nonexistent")

    def test_delete_middle_child_updates_siblings(self) -> None:
        """Test deleting a middle child updates parent correctly."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child-1", "Child 1", parent_id="root")
        tree.create_node("child-2", "Child 2", parent_id="root")
        tree.create_node("child-3", "Child 3", parent_id="root")

        tree.delete_node("child-2")

        children = tree.get_children("root")
        assert len(children) == 2
        assert {c.id for c in children} == {"child-1", "child-3"}


class TestTreeServiceMove:
    """Test node move operations."""

    def test_move_node_to_new_parent(self) -> None:
        """Test moving a node to a new parent."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("parent-1", "Parent 1", parent_id="root")
        tree.create_node("parent-2", "Parent 2", parent_id="root")
        tree.create_node("child", "Child", parent_id="parent-1")

        moved = tree.move_node("child", "parent-2")

        assert moved.parent_id == "parent-2"

        # Verify child is in new parent's children
        parent2_children = tree.get_children("parent-2")
        assert any(c.id == "child" for c in parent2_children)

        # Verify child is not in old parent's children
        parent1_children = tree.get_children("parent-1")
        assert not any(c.id == "child" for c in parent1_children)

    def test_move_node_updates_parent_leaf_status(self) -> None:
        """Test that moving a node updates both parents' leaf status."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("parent-1", "Parent 1", parent_id="root")
        tree.create_node("parent-2", "Parent 2", parent_id="root")
        tree.create_node("child", "Child", parent_id="parent-1")

        # Before: parent-1 has child, parent-2 is leaf
        assert tree.get_node("parent-1").is_leaf is False
        assert tree.get_node("parent-2").is_leaf is True

        tree.move_node("child", "parent-2")

        # After: parent-1 is leaf, parent-2 has child
        assert tree.get_node("parent-1").is_leaf is True
        assert tree.get_node("parent-2").is_leaf is False

    def test_move_root_node_fails(self) -> None:
        """Test that moving root node fails."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("other", "Other", parent_id="root")

        with pytest.raises(InvalidOperationError, match="Cannot move root"):
            tree.move_node("root", "other")

    def test_move_to_nonexistent_parent_fails(self) -> None:
        """Test moving to non-existent parent fails."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child", "Child", parent_id="root")

        with pytest.raises(TreeNotFoundError, match="New parent.*not found"):
            tree.move_node("child", "nonexistent")

    def test_move_to_descendant_creates_cycle_fails(self) -> None:
        """Test that moving a node to its own descendant fails."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child", "Child", parent_id="root")
        tree.create_node("grandchild", "Grandchild", parent_id="child")

        # Use child instead of root since root can't be moved
        with pytest.raises(CircularReferenceError, match="would create a cycle"):
            tree.move_node("child", "grandchild")

    def test_move_to_self_creates_cycle_fails(self) -> None:
        """Test that moving a node to itself fails."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("child", "Child", parent_id="root")

        with pytest.raises(CircularReferenceError):
            tree.move_node("child", "child")


class TestTreeServiceComplex:
    """Test complex tree scenarios."""

    def test_build_complex_tree(self) -> None:
        """Test building a multi-level tree."""
        tree = TreeService()

        # Build tree structure
        tree.create_node("root", "Root")
        tree.create_node("a", "A", parent_id="root")
        tree.create_node("b", "B", parent_id="root")
        tree.create_node("a1", "A1", parent_id="a")
        tree.create_node("a2", "A2", parent_id="a")
        tree.create_node("b1", "B1", parent_id="b")

        assert tree.node_count() == 6

        # Verify structure
        root_children = tree.get_children("root")
        assert len(root_children) == 2

        a_children = tree.get_children("a")
        assert len(a_children) == 2

        # Verify leaf status
        assert tree.get_node("root").is_leaf is False
        assert tree.get_node("a").is_leaf is False
        assert tree.get_node("b").is_leaf is False
        assert tree.get_node("a1").is_leaf is True
        assert tree.get_node("a2").is_leaf is True
        assert tree.get_node("b1").is_leaf is True

    def test_node_count_after_operations(self) -> None:
        """Test that node count is accurate after various operations."""
        tree = TreeService()

        assert tree.node_count() == 0

        tree.create_node("root", "Root")
        assert tree.node_count() == 1

        tree.create_node("child-1", "Child 1", parent_id="root")
        tree.create_node("child-2", "Child 2", parent_id="root")
        assert tree.node_count() == 3

        tree.delete_node("child-1")
        assert tree.node_count() == 2

        tree.update_node("root", description="Updated")
        assert tree.node_count() == 2
