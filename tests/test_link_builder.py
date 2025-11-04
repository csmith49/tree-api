"""Tests for LinkBuilder."""

import pytest

from tree.services.traversal import TraversalService
from tree.services.tree import TreeService
from tree.services.zipper import ZipperService
from tree.utils.link_builder import LinkBuilder


@pytest.fixture
def sample_tree() -> tuple[TreeService, LinkBuilder]:
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
    traversal = TraversalService(tree)
    builder = LinkBuilder(tree, zipper, traversal)

    return tree, builder


class TestLinkBuilderBasicLinks:
    """Test basic link generation."""

    def test_self_link_always_present(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that self link is always present."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "self" in links
        assert links["self"].href == "a"
        assert links["self"].title == "A"

    def test_root_link_always_present(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that root link is always present."""
        _, builder = sample_tree

        links = builder.build_links("a1")

        assert "root" in links
        assert links["root"].href == "root"
        assert links["root"].title == "Root"

    def test_links_include_titles(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that links include node descriptions as titles."""
        _, builder = sample_tree

        links = builder.build_links("a")

        # Check various links have titles
        assert links["self"].title == "A"
        assert links["up"].title == "Root"
        assert links["down"].title == "A1"


class TestLinkBuilderNavigationLinks:
    """Test zipper navigation links."""

    def test_up_link_for_child_node(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test up link points to parent."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "up" in links
        assert links["up"].href == "root"

    def test_no_up_link_for_root(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that root has no up link."""
        _, builder = sample_tree

        links = builder.build_links("root")

        assert "up" not in links

    def test_down_link_for_branch_node(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test down link points to first child."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "down" in links
        assert links["down"].href == "a1"

    def test_no_down_link_for_leaf(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that leaf nodes have no down link."""
        _, builder = sample_tree

        links = builder.build_links("a1")

        assert "down" not in links

    def test_left_link_for_non_first_sibling(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test left link points to previous sibling."""
        _, builder = sample_tree

        links = builder.build_links("b")

        assert "left" in links
        assert links["left"].href == "a"

    def test_no_left_link_for_first_sibling(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test that first sibling has no left link."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "left" not in links

    def test_right_link_for_non_last_sibling(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test right link points to next sibling."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "right" in links
        assert links["right"].href == "b"

    def test_no_right_link_for_last_sibling(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test that last sibling has no right link."""
        _, builder = sample_tree

        links = builder.build_links("b")

        assert "right" not in links


class TestLinkBuilderTraversalLinks:
    """Test DFS/BFS traversal links."""

    def test_next_dfs_link(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test next-dfs link follows DFS order."""
        _, builder = sample_tree

        # From root, next DFS should be 'a' (first child)
        links = builder.build_links("root")
        assert "next-dfs" in links
        assert links["next-dfs"].href == "a"

        # From 'a', next DFS should be 'a1' (down to first child)
        links = builder.build_links("a")
        assert links["next-dfs"].href == "a1"

        # From 'a1', next DFS should be 'a2' (right sibling)
        links = builder.build_links("a1")
        assert links["next-dfs"].href == "a2"

    def test_no_next_dfs_link_at_end(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that last node has no next-dfs link."""
        _, builder = sample_tree

        links = builder.build_links("b1")

        assert "next-dfs" not in links

    def test_prev_dfs_link(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test prev-dfs link follows reverse DFS order."""
        _, builder = sample_tree

        # From 'a1', prev DFS should be 'a' (parent)
        links = builder.build_links("a1")
        assert "prev-dfs" in links
        assert links["prev-dfs"].href == "a"

        # From 'b', prev DFS should be 'a2' (rightmost descendant of left sibling)
        links = builder.build_links("b")
        assert links["prev-dfs"].href == "a2"

    def test_no_prev_dfs_link_at_start(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that root has no prev-dfs link."""
        _, builder = sample_tree

        links = builder.build_links("root")

        assert "prev-dfs" not in links

    def test_next_bfs_link(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test next-bfs link follows BFS order."""
        _, builder = sample_tree

        # From 'a', next BFS should be 'b' (next on same level)
        links = builder.build_links("a")
        assert "next-bfs" in links
        assert links["next-bfs"].href == "b"

        # From 'b', next BFS should be 'a1' (first node of next level)
        links = builder.build_links("b")
        assert links["next-bfs"].href == "a1"

    def test_no_next_bfs_link_at_end(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that last node has no next-bfs link."""
        _, builder = sample_tree

        links = builder.build_links("b1")

        assert "next-bfs" not in links


class TestLinkBuilderChildrenLink:
    """Test children collection link."""

    def test_children_link_for_branch_node(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test that branch nodes have children link."""
        _, builder = sample_tree

        links = builder.build_links("a")

        assert "children" in links
        assert links["children"].href == "a/children"
        assert "Children of A" in links["children"].title

    def test_no_children_link_for_leaf(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that leaf nodes have no children link."""
        _, builder = sample_tree

        links = builder.build_links("a1")

        assert "children" not in links

    def test_children_link_includes_parent_info(
        self, sample_tree: tuple[TreeService, LinkBuilder]
    ) -> None:
        """Test that children link includes parent description."""
        _, builder = sample_tree

        links = builder.build_links("root")

        assert "children" in links
        assert "Root" in links["children"].title


class TestLinkBuilderEdgeCases:
    """Test edge cases and special scenarios."""

    def test_links_for_single_node_tree(self) -> None:
        """Test links for a tree with only one node."""
        tree = TreeService()
        tree.create_node("only", "Only node")

        zipper = ZipperService(tree)
        traversal = TraversalService(tree)
        builder = LinkBuilder(tree, zipper, traversal)

        links = builder.build_links("only")

        # Should only have self and root (which are the same)
        assert "self" in links
        assert "root" in links
        assert links["self"].href == "only"
        assert links["root"].href == "only"

        # No navigation links
        assert "up" not in links
        assert "down" not in links
        assert "left" not in links
        assert "right" not in links
        assert "next-dfs" not in links
        assert "next-bfs" not in links

    def test_links_for_linear_tree(self) -> None:
        """Test links for a linear tree (linked list)."""
        tree = TreeService()
        tree.create_node("1", "Node 1")
        tree.create_node("2", "Node 2", parent_id="1")
        tree.create_node("3", "Node 3", parent_id="2")

        zipper = ZipperService(tree)
        traversal = TraversalService(tree)
        builder = LinkBuilder(tree, zipper, traversal)

        # Middle node should have up, down, next-dfs, prev-dfs
        links = builder.build_links("2")

        assert "up" in links
        assert links["up"].href == "1"
        assert "down" in links
        assert links["down"].href == "3"

        # No left/right (no siblings)
        assert "left" not in links
        assert "right" not in links

    def test_links_for_wide_tree(self) -> None:
        """Test links for a tree with many siblings."""
        tree = TreeService()
        tree.create_node("root", "Root")
        for i in range(5):
            tree.create_node(f"child-{i}", f"Child {i}", parent_id="root")

        zipper = ZipperService(tree)
        traversal = TraversalService(tree)
        builder = LinkBuilder(tree, zipper, traversal)

        # Middle child should have left and right
        links = builder.build_links("child-2")

        assert "left" in links
        assert links["left"].href == "child-1"
        assert "right" in links
        assert links["right"].href == "child-3"

    def test_all_links_have_href(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that all generated links have href."""
        _, builder = sample_tree

        links = builder.build_links("a")

        for rel, link in links.items():
            assert link.href is not None
            assert len(link.href) > 0

    def test_all_links_have_title(self, sample_tree: tuple[TreeService, LinkBuilder]) -> None:
        """Test that all generated links have title."""
        _, builder = sample_tree

        links = builder.build_links("a")

        for rel, link in links.items():
            assert link.title is not None
            assert len(link.title) > 0
