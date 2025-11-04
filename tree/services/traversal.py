"""Traversal service for DFS and BFS tree traversal."""

from collections import deque
from collections.abc import Iterator

from tree.models import Node
from tree.services.tree import TreeService
from tree.types import NodeId


class TraversalService:
    """Tree traversal algorithms (DFS and BFS)."""

    def __init__(self, tree: TreeService) -> None:
        """Initialize traversal service with a tree."""
        self.tree = tree

    def compute_next_dfs(self, node_id: NodeId) -> Node | None:
        """Compute the next node in depth-first order.

        Priority: down > right > (up then right)

        Args:
            node_id: Current node ID

        Returns:
            Next node in DFS order, or None if no next node
        """
        node = self.tree.get_node(node_id)

        # Try down (first child)
        children = self.tree.get_children(node_id)
        if children:
            return children[0]

        # Try right (next sibling)
        if node.parent_id is not None:
            siblings = self.tree.get_siblings(node_id)
            try:
                current_index = next(i for i, s in enumerate(siblings) if s.id == node_id)
                if current_index < len(siblings) - 1:
                    return siblings[current_index + 1]
            except StopIteration:
                pass

        # Go up and try right
        current = node
        while current.parent_id is not None:
            parent = self.tree.get_parent(current.id)
            if parent is None:
                break

            # Try to get next sibling of parent
            parent_siblings = self.tree.get_siblings(parent.id)
            try:
                parent_index = next(i for i, s in enumerate(parent_siblings) if s.id == parent.id)
                if parent_index < len(parent_siblings) - 1:
                    return parent_siblings[parent_index + 1]
            except StopIteration:
                pass

            current = parent

        return None

    def compute_prev_dfs(self, node_id: NodeId) -> Node | None:
        """Compute the previous node in depth-first order.

        Args:
            node_id: Current node ID

        Returns:
            Previous node in DFS order, or None if no previous node
        """
        node = self.tree.get_node(node_id)

        # If this is root, no previous
        if node.parent_id is None:
            return None

        # Try left (previous sibling)
        siblings = self.tree.get_siblings(node_id)
        try:
            current_index = next(i for i, s in enumerate(siblings) if s.id == node_id)
        except StopIteration:
            return None

        if current_index > 0:
            # Go to rightmost descendant of left sibling
            left_sibling = siblings[current_index - 1]
            return self._rightmost_descendant(left_sibling.id)

        # No left sibling, go to parent
        return self.tree.get_parent(node_id)

    def _rightmost_descendant(self, node_id: NodeId) -> Node:
        """Get the rightmost descendant of a node (for prev_dfs)."""
        current = self.tree.get_node(node_id)

        while not current.is_leaf:
            children = self.tree.get_children(current.id)
            if not children:
                break
            # Go to last child
            current = children[-1]

        return current

    def compute_next_bfs(self, node_id: NodeId) -> Node | None:
        """Compute the next node in breadth-first order.

        Args:
            node_id: Current node ID

        Returns:
            Next node in BFS order, or None if no next node
        """
        # Do a BFS traversal and find the current node, then return the next one
        root = self.tree.get_root()
        if root is None:
            return None

        queue: deque[Node] = deque([root])
        found_current = False

        while queue:
            current = queue.popleft()

            if found_current:
                # This is the next node after the one we're looking for
                return current

            if current.id == node_id:
                found_current = True

            # Add children to queue
            children = self.tree.get_children(current.id)
            queue.extend(children)

        return None

    def traverse_dfs(self, start_node_id: NodeId) -> Iterator[Node]:
        """Generate all nodes in depth-first order starting from a node.

        Args:
            start_node_id: Node ID to start traversal from

        Yields:
            Nodes in DFS order
        """
        current_id: NodeId | None = start_node_id

        while current_id is not None:
            node = self.tree.get_node(current_id)
            yield node

            next_node = self.compute_next_dfs(current_id)
            current_id = next_node.id if next_node else None

    def traverse_bfs(self, start_node_id: NodeId) -> Iterator[Node]:
        """Generate all nodes in breadth-first order starting from a node.

        Args:
            start_node_id: Node ID to start traversal from

        Yields:
            Nodes in BFS order
        """
        start_node = self.tree.get_node(start_node_id)
        queue: deque[Node] = deque([start_node])

        while queue:
            node = queue.popleft()
            yield node

            # Add children to queue
            children = self.tree.get_children(node.id)
            queue.extend(children)
