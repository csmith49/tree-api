"""Tests for ZipperService."""

import pytest

from tree.services.tree import InvalidOperationError, TreeNotFoundError, TreeService
from tree.services.zipper import ZipperService


@pytest.fixture
def sample_tree() -> tuple[TreeService, ZipperService]:
    """Create a sample tree for testing.

    Structure:
        root
        ├── a
        │   ├── a1
        │   └── a2
        └── b
            └── b1
    """
    tree = TreeService()
    tree.create_node("root", "Root")
    tree.create_node("a", "A", parent_id="root")
    tree.create_node("b", "B", parent_id="root")
    tree.create_node("a1", "A1", parent_id="a")
    tree.create_node("a2", "A2", parent_id="a")
    tree.create_node("b1", "B1", parent_id="b")

    zipper = ZipperService(tree)
    return tree, zipper


class TestZipperNavigation:
    """Test zipper navigation operations."""

    def test_up_from_child_to_parent(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating up from child to parent."""
        _, zipper = sample_tree

        parent = zipper.up("a")
        assert parent is not None
        assert parent.id == "root"

    def test_up_from_root_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating up from root returns None."""
        _, zipper = sample_tree

        parent = zipper.up("root")
        assert parent is None

    def test_down_to_first_child(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating down to first child."""
        _, zipper = sample_tree

        child = zipper.down("root")
        assert child is not None
        assert child.id == "a"  # First child

    def test_down_from_leaf_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating down from leaf returns None."""
        _, zipper = sample_tree

        child = zipper.down("a1")
        assert child is None

    def test_left_to_previous_sibling(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating left to previous sibling."""
        _, zipper = sample_tree

        sibling = zipper.left("a2")
        assert sibling is not None
        assert sibling.id == "a1"

    def test_left_from_first_sibling_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating left from first sibling returns None."""
        _, zipper = sample_tree

        sibling = zipper.left("a1")
        assert sibling is None

    def test_left_from_root_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating left from root returns None."""
        _, zipper = sample_tree

        sibling = zipper.left("root")
        assert sibling is None

    def test_right_to_next_sibling(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating right to next sibling."""
        _, zipper = sample_tree

        sibling = zipper.right("a")
        assert sibling is not None
        assert sibling.id == "b"

    def test_right_from_last_sibling_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating right from last sibling returns None."""
        _, zipper = sample_tree

        sibling = zipper.right("b")
        assert sibling is None

    def test_right_from_root_returns_none(
        self, sample_tree: tuple[TreeService, ZipperService]
    ) -> None:
        """Test that navigating right from root returns None."""
        _, zipper = sample_tree

        sibling = zipper.right("root")
        assert sibling is None

    def test_root_returns_root_node(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test getting root node."""
        _, zipper = sample_tree

        root = zipper.root()
        assert root is not None
        assert root.id == "root"

    def test_root_on_empty_tree_returns_none(self) -> None:
        """Test getting root from empty tree returns None."""
        tree = TreeService()
        zipper = ZipperService(tree)

        root = zipper.root()
        assert root is None


class TestZipperCombinedNavigation:
    """Test combined navigation sequences."""

    def test_navigate_down_then_up(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating down then back up."""
        _, zipper = sample_tree

        # Start at root, go down to first child
        child = zipper.down("root")
        assert child is not None
        assert child.id == "a"

        # Go back up to root
        parent = zipper.up(child.id)
        assert parent is not None
        assert parent.id == "root"

    def test_navigate_left_then_right(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating left then right."""
        _, zipper = sample_tree

        # Start at a2, go left to a1
        left_sibling = zipper.left("a2")
        assert left_sibling is not None
        assert left_sibling.id == "a1"

        # Go right back to a2
        right_sibling = zipper.right(left_sibling.id)
        assert right_sibling is not None
        assert right_sibling.id == "a2"

    def test_navigate_to_grandchild(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test navigating from root to grandchild."""
        _, zipper = sample_tree

        # root -> a -> a1
        child = zipper.down("root")
        assert child is not None
        assert child.id == "a"

        grandchild = zipper.down(child.id)
        assert grandchild is not None
        assert grandchild.id == "a1"


class TestZipperExpand:
    """Test expand (zoom in) operation."""

    def test_expand_leaf_node(self) -> None:
        """Test expanding a leaf node into a branch."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("leaf", "Leaf", parent_id="root")

        zipper = ZipperService(tree)

        # Expand leaf with two children
        expanded = zipper.expand(
            "leaf",
            [
                ("child-1", "Child 1", {}),
                ("child-2", "Child 2", {"key": "value"}),
            ],
        )

        assert expanded.id == "leaf"
        assert expanded.is_leaf is False

        # Verify children were created
        children = tree.get_children("leaf")
        assert len(children) == 2
        assert {c.id for c in children} == {"child-1", "child-2"}

    def test_expand_branch_node_fails(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test that expanding a branch node fails."""
        _, zipper = sample_tree

        with pytest.raises(InvalidOperationError, match="not a leaf"):
            zipper.expand("a", [("new-child", "New Child", {})])

    def test_expand_with_metadata(self) -> None:
        """Test expanding with child metadata."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("leaf", "Leaf", parent_id="root")

        zipper = ZipperService(tree)

        zipper.expand(
            "leaf",
            [("child", "Child", {"priority": "high", "count": 42})],
        )

        child = tree.get_node("child")
        assert child.metadata == {"priority": "high", "count": 42}

    def test_expand_empty_children_list(self) -> None:
        """Test expanding with empty children list."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("leaf", "Leaf", parent_id="root")

        zipper = ZipperService(tree)

        # Expanding with no children should still work
        expanded = zipper.expand("leaf", [])

        # Node should still be a leaf since no children were added
        assert expanded.is_leaf is True


class TestZipperCollapse:
    """Test collapse (zoom out) operation."""

    def test_collapse_branch_node(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test collapsing a branch node into a leaf."""
        tree, zipper = sample_tree

        # Collapse node 'a' which has children a1 and a2
        collapsed = zipper.collapse("a")

        assert collapsed.id == "a"
        assert collapsed.is_leaf is True

        # Verify children were deleted
        children = tree.get_children("a")
        assert len(children) == 0

        # Verify descendants no longer exist
        with pytest.raises(TreeNotFoundError):
            tree.get_node("a1")
        with pytest.raises(TreeNotFoundError):
            tree.get_node("a2")

    def test_collapse_with_summary(self, sample_tree: tuple[TreeService, ZipperService]) -> None:
        """Test collapsing with a summary description."""
        _, zipper = sample_tree

        collapsed = zipper.collapse("a", summary="A (completed)")

        assert collapsed.description == "A (completed)"
        assert collapsed.is_leaf is True

    def test_collapse_leaf_node_fails(self) -> None:
        """Test that collapsing a leaf node fails."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("leaf", "Leaf", parent_id="root")

        zipper = ZipperService(tree)

        with pytest.raises(InvalidOperationError, match="already a leaf"):
            zipper.collapse("leaf")

    def test_collapse_deletes_all_descendants(self) -> None:
        """Test that collapse deletes all descendants recursively."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("a", "A", parent_id="root")
        tree.create_node("a1", "A1", parent_id="a")
        tree.create_node("a1a", "A1a", parent_id="a1")

        zipper = ZipperService(tree)

        # Collapse 'a' should delete a1 and a1a
        zipper.collapse("a")

        assert tree.node_count() == 2  # Only root and a remain

        with pytest.raises(TreeNotFoundError):
            tree.get_node("a1")
        with pytest.raises(TreeNotFoundError):
            tree.get_node("a1a")


class TestZipperExpandCollapseCycle:
    """Test expand/collapse cycles."""

    def test_expand_then_collapse(self) -> None:
        """Test expanding a leaf then collapsing it back."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("node", "Node", parent_id="root")

        zipper = ZipperService(tree)

        # Start as leaf
        assert tree.get_node("node").is_leaf is True

        # Expand
        zipper.expand("node", [("child-1", "Child 1", {}), ("child-2", "Child 2", {})])
        assert tree.get_node("node").is_leaf is False
        assert tree.node_count() == 4

        # Collapse back
        zipper.collapse("node")
        assert tree.get_node("node").is_leaf is True
        assert tree.node_count() == 2  # Only root and node remain

    def test_multiple_expand_collapse_cycles(self) -> None:
        """Test multiple expand/collapse cycles."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("node", "Node", parent_id="root")

        zipper = ZipperService(tree)

        for i in range(3):
            # Expand
            zipper.expand("node", [(f"child-{i}", f"Child {i}", {})])
            assert tree.get_node("node").is_leaf is False

            # Collapse
            zipper.collapse("node", summary=f"Summary {i}")
            assert tree.get_node("node").is_leaf is True
            assert tree.get_node("node").description == f"Summary {i}"
