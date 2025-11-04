"""Context builder for computing zipper-style context information."""

from tree.models import Breadcrumb, Context, Node
from tree.services.tree import TreeService
from tree.types import NodeId


class ContextBuilder:
    """Builds context information for nodes in a tree."""

    def __init__(self, tree: TreeService) -> None:
        """Initialize context builder with tree service."""
        self.tree = tree

    def build_context(self, node_id: NodeId) -> Context:
        """Build zipper-style context with breadcrumbs for a node.

        Args:
            node_id: ID of the node to build context for

        Returns:
            Context with depth, sibling position, and breadcrumbs
        """
        node = self.tree.get_node(node_id)
        breadcrumbs = self._compute_breadcrumbs(node)
        siblings = self.tree.get_siblings(node_id)
        children = self.tree.get_children(node_id)

        # Find position of current node in siblings list
        sibling_position = next(i for i, s in enumerate(siblings) if s.id == node_id)

        return Context(
            depth=len(breadcrumbs),
            sibling_position=sibling_position,
            total_siblings=len(siblings),
            has_children=not node.is_leaf,
            children_count=len(children),
            breadcrumbs=breadcrumbs,
        )

    def _compute_breadcrumbs(self, node: Node) -> list[Breadcrumb]:
        """Walk up to root building breadcrumb trail.

        Args:
            node: Node to start from

        Returns:
            List of breadcrumbs from root to parent (not including current node)
        """
        breadcrumbs: list[Breadcrumb] = []
        current_id = node.parent_id

        while current_id is not None:
            parent = self.tree.get_node(current_id)
            breadcrumbs.insert(
                0,
                Breadcrumb(
                    id=parent.id,
                    description=parent.description,
                ),
            )
            current_id = parent.parent_id

        return breadcrumbs
