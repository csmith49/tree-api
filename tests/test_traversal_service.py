"""Tests for TraversalService."""

import pytest

from tree.services.traversal import TraversalService
from tree.services.tree import TreeService


@pytest.fixture
def sample_tree() -> tuple[TreeService, TraversalService]:
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

    traversal = TraversalService(tree)
    return tree, traversal


class TestDFSTraversal:
    """Test depth-first traversal."""

    def test_next_dfs_down(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test DFS going down to first child."""
        _, traversal = sample_tree

        next_node = traversal.compute_next_dfs("root")
        assert next_node is not None
        assert next_node.id == "a"

    def test_next_dfs_right(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test DFS going right to next sibling."""
        _, traversal = sample_tree

        next_node = traversal.compute_next_dfs("a1")
        assert next_node is not None
        assert next_node.id == "a2"

    def test_next_dfs_up_and_right(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test DFS going up then right."""
        _, traversal = sample_tree

        # From a2, should go up to a, then right to b
        next_node = traversal.compute_next_dfs("a2")
        assert next_node is not None
        assert next_node.id == "b"

    def test_next_dfs_from_last_node_returns_none(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test that DFS from last node returns None."""
        _, traversal = sample_tree

        next_node = traversal.compute_next_dfs("b1")
        assert next_node is None

    def test_prev_dfs_to_parent(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test DFS going back to parent."""
        _, traversal = sample_tree

        prev_node = traversal.compute_prev_dfs("a1")
        assert prev_node is not None
        assert prev_node.id == "a"

    def test_prev_dfs_to_left_sibling_descendant(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test DFS going to rightmost descendant of left sibling."""
        _, traversal = sample_tree

        # From b, should go to rightmost descendant of a, which is a2
        prev_node = traversal.compute_prev_dfs("b")
        assert prev_node is not None
        assert prev_node.id == "a2"

    def test_prev_dfs_from_root_returns_none(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test that prev from root returns None."""
        _, traversal = sample_tree

        prev_node = traversal.compute_prev_dfs("root")
        assert prev_node is None

    def test_traverse_dfs_full_tree(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test full DFS traversal."""
        _, traversal = sample_tree

        nodes = list(traversal.traverse_dfs("root"))
        node_ids = [n.id for n in nodes]

        # DFS order: root, a, a1, a2, b, b1
        assert node_ids == ["root", "a", "a1", "a2", "b", "b1"]

    def test_traverse_dfs_from_subtree(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test DFS traversal from a subtree.

        Note: DFS continues to siblings after exhausting subtree.
        """
        _, traversal = sample_tree

        nodes = list(traversal.traverse_dfs("a"))
        node_ids = [n.id for n in nodes]

        # DFS from 'a' continues: a, a1, a2, b, b1
        assert node_ids == ["a", "a1", "a2", "b", "b1"]


class TestBFSTraversal:
    """Test breadth-first traversal."""

    def test_next_bfs_same_level(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test BFS going to next node on same level."""
        _, traversal = sample_tree

        next_node = traversal.compute_next_bfs("a")
        assert next_node is not None
        assert next_node.id == "b"

    def test_next_bfs_next_level(self, sample_tree: tuple[TreeService, TraversalService]) -> None:
        """Test BFS going to next level."""
        _, traversal = sample_tree

        # After b, should go to first node of next level (a1)
        next_node = traversal.compute_next_bfs("b")
        assert next_node is not None
        assert next_node.id == "a1"

    def test_next_bfs_from_last_node_returns_none(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test that BFS from last node returns None."""
        _, traversal = sample_tree

        next_node = traversal.compute_next_bfs("b1")
        assert next_node is None

    def test_traverse_bfs_full_tree(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test full BFS traversal."""
        _, traversal = sample_tree

        nodes = list(traversal.traverse_bfs("root"))
        node_ids = [n.id for n in nodes]

        # BFS order: root, a, b, a1, a2, b1
        assert node_ids == ["root", "a", "b", "a1", "a2", "b1"]

    def test_traverse_bfs_from_subtree(
        self, sample_tree: tuple[TreeService, TraversalService]
    ) -> None:
        """Test BFS traversal from a subtree."""
        _, traversal = sample_tree

        nodes = list(traversal.traverse_bfs("a"))
        node_ids = [n.id for n in nodes]

        # BFS from a: a, a1, a2
        assert node_ids == ["a", "a1", "a2"]


class TestTraversalOnDifferentTrees:
    """Test traversal on different tree structures."""

    def test_traversal_on_linear_tree(self) -> None:
        """Test traversal on a linear tree (linked list)."""
        tree = TreeService()
        tree.create_node("1", "Node 1")
        tree.create_node("2", "Node 2", parent_id="1")
        tree.create_node("3", "Node 3", parent_id="2")

        traversal = TraversalService(tree)

        # DFS and BFS should be the same for linear tree
        dfs_nodes = [n.id for n in traversal.traverse_dfs("1")]
        bfs_nodes = [n.id for n in traversal.traverse_bfs("1")]

        assert dfs_nodes == ["1", "2", "3"]
        assert bfs_nodes == ["1", "2", "3"]

    def test_traversal_on_single_node(self) -> None:
        """Test traversal on a single node."""
        tree = TreeService()
        tree.create_node("only", "Only node")

        traversal = TraversalService(tree)

        dfs_nodes = list(traversal.traverse_dfs("only"))
        bfs_nodes = list(traversal.traverse_bfs("only"))

        assert len(dfs_nodes) == 1
        assert dfs_nodes[0].id == "only"
        assert len(bfs_nodes) == 1
        assert bfs_nodes[0].id == "only"

    def test_traversal_on_wide_tree(self) -> None:
        """Test traversal on a wide tree (many siblings)."""
        tree = TreeService()
        tree.create_node("root", "Root")
        for i in range(5):
            tree.create_node(f"child-{i}", f"Child {i}", parent_id="root")

        traversal = TraversalService(tree)

        dfs_nodes = [n.id for n in traversal.traverse_dfs("root")]
        bfs_nodes = [n.id for n in traversal.traverse_bfs("root")]

        # DFS: root, then all children in order
        assert dfs_nodes[0] == "root"
        assert set(dfs_nodes[1:]) == {f"child-{i}" for i in range(5)}

        # BFS: root, then all children in order (same as DFS for depth 1)
        assert bfs_nodes[0] == "root"
        assert bfs_nodes[1:] == [f"child-{i}" for i in range(5)]
