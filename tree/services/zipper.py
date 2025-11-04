"""Zipper service for tree navigation and zoom operations."""

from typing import Any

from tree.models import Node
from tree.services.tree import TreeService
from tree.types import NodeId


class ZipperService:
    """Zipper-style navigation and zoom operations for trees."""

    def __init__(self, tree: TreeService) -> None:
        """Initialize zipper service with a tree."""
        self.tree = tree

    def up(self, node_id: NodeId) -> Node | None:
        """Navigate up to parent node."""
        return self.tree.get_parent(node_id)

    def down(self, node_id: NodeId) -> Node | None:
        """Navigate down to first child node."""
        children = self.tree.get_children(node_id)
        if not children:
            return None
        return children[0]

    def left(self, node_id: NodeId) -> Node | None:
        """Navigate left to previous sibling."""
        node = self.tree.get_node(node_id)
        if node.parent_id is None:
            # Root has no siblings
            return None

        siblings = self.tree.get_siblings(node_id)
        try:
            current_index = next(i for i, s in enumerate(siblings) if s.id == node_id)
        except StopIteration:
            return None

        if current_index == 0:
            # Already at first sibling
            return None

        return siblings[current_index - 1]

    def right(self, node_id: NodeId) -> Node | None:
        """Navigate right to next sibling."""
        node = self.tree.get_node(node_id)
        if node.parent_id is None:
            # Root has no siblings
            return None

        siblings = self.tree.get_siblings(node_id)
        try:
            current_index = next(i for i, s in enumerate(siblings) if s.id == node_id)
        except StopIteration:
            return None

        if current_index == len(siblings) - 1:
            # Already at last sibling
            return None

        return siblings[current_index + 1]

    def root(self) -> Node | None:
        """Get the root node."""
        return self.tree.get_root()

    def expand(
        self,
        node_id: NodeId,
        children_data: list[tuple[NodeId, str, dict[str, Any]]],
    ) -> Node:
        """Expand a leaf node into a branch with children.

        Args:
            node_id: ID of the leaf node to expand
            children_data: List of (id, description, metadata) tuples for children

        Returns:
            The expanded node (now a branch)

        Raises:
            InvalidOperationError: If node is not a leaf
        """
        from tree.services.tree import InvalidOperationError

        node = self.tree.get_node(node_id)
        if not node.is_leaf:
            raise InvalidOperationError(f"Node {node_id} is not a leaf, cannot expand")

        # Create all children
        for child_id, description, metadata in children_data:
            self.tree.create_node(
                node_id=child_id,
                description=description,
                parent_id=node_id,
                metadata=metadata,
            )

        # Return updated node (will now be a branch)
        return self.tree.get_node(node_id)

    def collapse(self, node_id: NodeId, summary: str | None = None) -> Node:
        """Collapse a branch node into a leaf, deleting all descendants.

        Args:
            node_id: ID of the branch node to collapse
            summary: Optional new description for the collapsed node

        Returns:
            The collapsed node (now a leaf)

        Raises:
            InvalidOperationError: If node is already a leaf
        """
        from tree.services.tree import InvalidOperationError

        node = self.tree.get_node(node_id)
        if node.is_leaf:
            raise InvalidOperationError(f"Node {node_id} is already a leaf, cannot collapse")

        # Delete all children (recursively)
        children = self.tree.get_children(node_id)
        for child in children:
            self.tree.delete_node(child.id)

        # Update description if summary provided
        if summary is not None:
            return self.tree.update_node(node_id, description=summary)

        # Return updated node (will now be a leaf)
        return self.tree.get_node(node_id)
