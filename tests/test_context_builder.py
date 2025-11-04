"""Tests for ContextBuilder."""

import pytest

from tree.services.tree import TreeService
from tree.utils.context import ContextBuilder


@pytest.fixture
def sample_tree() -> tuple[TreeService, ContextBuilder]:
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

    builder = ContextBuilder(tree)
    return tree, builder


class TestContextBuilderBasics:
    """Test basic context building."""

    def test_build_context_for_root(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test building context for root node."""
        _, builder = sample_tree

        context = builder.build_context("root")

        assert context.depth == 0  # No ancestors
        assert context.sibling_position == 0
        assert context.total_siblings == 1  # Root is its own sibling
        assert context.has_children is True
        assert context.children_count == 2
        assert context.breadcrumbs == []

    def test_build_context_for_child(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test building context for first-level child."""
        _, builder = sample_tree

        context = builder.build_context("a")

        assert context.depth == 1  # One ancestor (root)
        assert context.sibling_position == 0  # First sibling
        assert context.total_siblings == 2  # a and b
        assert context.has_children is True
        assert context.children_count == 2
        assert len(context.breadcrumbs) == 1
        assert context.breadcrumbs[0].id == "root"
        assert context.breadcrumbs[0].description == "Root"

    def test_build_context_for_grandchild(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test building context for second-level child."""
        _, builder = sample_tree

        context = builder.build_context("a1")

        assert context.depth == 2  # Two ancestors (root, a)
        assert context.sibling_position == 0  # First sibling
        assert context.total_siblings == 2  # a1 and a2
        assert context.has_children is False
        assert context.children_count == 0
        assert len(context.breadcrumbs) == 2
        assert context.breadcrumbs[0].id == "root"
        assert context.breadcrumbs[1].id == "a"

    def test_build_context_for_leaf(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test building context for leaf node."""
        _, builder = sample_tree

        context = builder.build_context("b1")

        assert context.depth == 2
        assert context.has_children is False
        assert context.children_count == 0
        assert len(context.breadcrumbs) == 2


class TestContextBuilderSiblingPosition:
    """Test sibling position calculation."""

    def test_sibling_position_first_child(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test sibling position for first child."""
        _, builder = sample_tree

        context = builder.build_context("a")
        assert context.sibling_position == 0

    def test_sibling_position_second_child(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test sibling position for second child."""
        _, builder = sample_tree

        context = builder.build_context("b")
        assert context.sibling_position == 1

    def test_sibling_position_with_many_siblings(self) -> None:
        """Test sibling position with many siblings."""
        tree = TreeService()
        tree.create_node("root", "Root")
        for i in range(5):
            tree.create_node(f"child-{i}", f"Child {i}", parent_id="root")

        builder = ContextBuilder(tree)

        for i in range(5):
            context = builder.build_context(f"child-{i}")
            assert context.sibling_position == i
            assert context.total_siblings == 5


class TestContextBuilderBreadcrumbs:
    """Test breadcrumb computation."""

    def test_breadcrumbs_empty_for_root(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test that root has no breadcrumbs."""
        _, builder = sample_tree

        context = builder.build_context("root")
        assert context.breadcrumbs == []

    def test_breadcrumbs_order(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test that breadcrumbs are ordered from root to parent."""
        _, builder = sample_tree

        context = builder.build_context("a1")

        assert len(context.breadcrumbs) == 2
        assert context.breadcrumbs[0].id == "root"
        assert context.breadcrumbs[1].id == "a"

    def test_breadcrumbs_deep_tree(self) -> None:
        """Test breadcrumbs on a deep tree."""
        tree = TreeService()
        tree.create_node("1", "Level 1")
        tree.create_node("2", "Level 2", parent_id="1")
        tree.create_node("3", "Level 3", parent_id="2")
        tree.create_node("4", "Level 4", parent_id="3")

        builder = ContextBuilder(tree)
        context = builder.build_context("4")

        assert context.depth == 3
        assert len(context.breadcrumbs) == 3
        assert [b.id for b in context.breadcrumbs] == ["1", "2", "3"]

    def test_breadcrumbs_include_descriptions(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test that breadcrumbs include node descriptions."""
        _, builder = sample_tree

        context = builder.build_context("a1")

        assert context.breadcrumbs[0].description == "Root"
        assert context.breadcrumbs[1].description == "A"


class TestContextBuilderChildrenInfo:
    """Test children information in context."""

    def test_has_children_for_branch(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test has_children is true for branch nodes."""
        _, builder = sample_tree

        context = builder.build_context("a")
        assert context.has_children is True
        assert context.children_count == 2

    def test_has_children_for_leaf(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test has_children is false for leaf nodes."""
        _, builder = sample_tree

        context = builder.build_context("a1")
        assert context.has_children is False
        assert context.children_count == 0

    def test_children_count_accuracy(self) -> None:
        """Test that children_count is accurate."""
        tree = TreeService()
        tree.create_node("root", "Root")
        tree.create_node("parent", "Parent", parent_id="root")

        for i in range(7):
            tree.create_node(f"child-{i}", f"Child {i}", parent_id="parent")

        builder = ContextBuilder(tree)
        context = builder.build_context("parent")

        assert context.children_count == 7


class TestContextBuilderDepth:
    """Test depth calculation."""

    def test_depth_root_is_zero(self, sample_tree: tuple[TreeService, ContextBuilder]) -> None:
        """Test that root depth is 0."""
        _, builder = sample_tree

        context = builder.build_context("root")
        assert context.depth == 0

    def test_depth_matches_breadcrumb_length(
        self, sample_tree: tuple[TreeService, ContextBuilder]
    ) -> None:
        """Test that depth equals number of breadcrumbs."""
        _, builder = sample_tree

        for node_id in ["root", "a", "a1"]:
            context = builder.build_context(node_id)
            assert context.depth == len(context.breadcrumbs)

    def test_depth_calculation_in_deep_tree(self) -> None:
        """Test depth in a very deep tree."""
        tree = TreeService()
        tree.create_node("0", "Level 0")

        for i in range(1, 10):
            tree.create_node(str(i), f"Level {i}", parent_id=str(i - 1))

        builder = ContextBuilder(tree)

        for i in range(10):
            context = builder.build_context(str(i))
            assert context.depth == i
