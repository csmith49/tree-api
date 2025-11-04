"""Link builder for computing HATEOAS navigation links."""

from tree.models import Link
from tree.services.traversal import TraversalService
from tree.services.tree import TreeService
from tree.services.zipper import ZipperService
from tree.types import NodeId


class LinkBuilder:
    """Builds HATEOAS navigation links for nodes."""

    def __init__(
        self,
        tree: TreeService,
        zipper: ZipperService,
        traversal: TraversalService,
    ) -> None:
        """Initialize link builder with required services."""
        self.tree = tree
        self.zipper = zipper
        self.traversal = traversal

    def build_links(self, node_id: NodeId) -> dict[str, Link]:
        """Compute all valid navigation links from a node.

        Args:
            node_id: ID of the node to build links for

        Returns:
            Dictionary of link relation names to Link objects
        """
        node = self.tree.get_node(node_id)
        links: dict[str, Link] = {}

        # Self link (always present)
        links["self"] = Link(href=node_id, title=node.description)

        # Root link (always present)
        root = self.tree.get_root()
        if root is not None:
            links["root"] = Link(href=root.id, title=root.description)

        # Parent link (up)
        parent = self.zipper.up(node_id)
        if parent is not None:
            links["up"] = Link(href=parent.id, title=parent.description)

        # First child link (down)
        child = self.zipper.down(node_id)
        if child is not None:
            links["down"] = Link(href=child.id, title=child.description)

        # Previous sibling link (left)
        left_sibling = self.zipper.left(node_id)
        if left_sibling is not None:
            links["left"] = Link(href=left_sibling.id, title=left_sibling.description)

        # Next sibling link (right)
        right_sibling = self.zipper.right(node_id)
        if right_sibling is not None:
            links["right"] = Link(href=right_sibling.id, title=right_sibling.description)

        # Next DFS link
        next_dfs = self.traversal.compute_next_dfs(node_id)
        if next_dfs is not None:
            links["next-dfs"] = Link(href=next_dfs.id, title=next_dfs.description)

        # Previous DFS link
        prev_dfs = self.traversal.compute_prev_dfs(node_id)
        if prev_dfs is not None:
            links["prev-dfs"] = Link(href=prev_dfs.id, title=prev_dfs.description)

        # Next BFS link
        next_bfs = self.traversal.compute_next_bfs(node_id)
        if next_bfs is not None:
            links["next-bfs"] = Link(href=next_bfs.id, title=next_bfs.description)

        # Children collection link (if node has children)
        if not node.is_leaf:
            links["children"] = Link(
                href=f"{node_id}/children",
                title=f"Children of {node.description}",
            )

        return links
