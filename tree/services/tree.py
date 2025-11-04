"""Tree service for managing nodes and tree structure."""

from datetime import datetime
from typing import Any

from tree.models import Node
from tree.types import NodeId


class TreeNotFoundError(Exception):
    """Raised when a node is not found."""

    pass


class CircularReferenceError(Exception):
    """Raised when an operation would create a circular reference."""

    pass


class InvalidOperationError(Exception):
    """Raised when an invalid operation is attempted."""

    pass


class TreeService:
    """In-memory tree storage and management."""

    def __init__(self) -> None:
        """Initialize empty tree storage."""
        self._nodes: dict[NodeId, Node] = {}
        self._children: dict[NodeId, list[NodeId]] = {}
        self._root_id: NodeId | None = None

    def create_node(
        self,
        node_id: NodeId,
        description: str,
        parent_id: NodeId | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Node:
        """Create a new node in the tree."""
        if node_id in self._nodes:
            raise InvalidOperationError(f"Node {node_id} already exists")

        if parent_id is not None and parent_id not in self._nodes:
            raise TreeNotFoundError(f"Parent node {parent_id} not found")

        now = datetime.now()
        node = Node(
            id=node_id,
            parent_id=parent_id,
            description=description,
            metadata=metadata or {},
            is_leaf=True,
            created_at=now,
            updated_at=now,
        )

        self._nodes[node_id] = node
        self._children[node_id] = []

        if parent_id is None:
            # This is a root node
            if self._root_id is not None:
                raise InvalidOperationError("Root node already exists")
            self._root_id = node_id
        else:
            # Add to parent's children
            self._children[parent_id].append(node_id)
            # Parent is no longer a leaf
            parent = self._nodes[parent_id]
            self._nodes[parent_id] = parent.model_copy(update={"is_leaf": False, "updated_at": now})

        return node

    def get_node(self, node_id: NodeId) -> Node:
        """Get a node by ID."""
        if node_id not in self._nodes:
            raise TreeNotFoundError(f"Node {node_id} not found")
        return self._nodes[node_id]

    def update_node(
        self,
        node_id: NodeId,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Node:
        """Update a node's description or metadata."""
        node = self.get_node(node_id)

        updates: dict[str, Any] = {"updated_at": datetime.now()}
        if description is not None:
            updates["description"] = description
        if metadata is not None:
            updates["metadata"] = metadata

        updated_node = node.model_copy(update=updates)
        self._nodes[node_id] = updated_node
        return updated_node

    def delete_node(self, node_id: NodeId) -> None:
        """Delete a node and all its descendants."""
        node = self.get_node(node_id)

        if node_id == self._root_id:
            raise InvalidOperationError("Cannot delete root node")

        # Delete all descendants first
        for child_id in list(self._children.get(node_id, [])):
            self.delete_node(child_id)

        # Remove from parent's children list
        if node.parent_id:
            parent_children = self._children[node.parent_id]
            parent_children.remove(node_id)

            # Update parent's is_leaf status
            if len(parent_children) == 0:
                parent = self._nodes[node.parent_id]
                self._nodes[node.parent_id] = parent.model_copy(
                    update={"is_leaf": True, "updated_at": datetime.now()}
                )

        # Delete the node
        del self._nodes[node_id]
        del self._children[node_id]

    def get_children(self, node_id: NodeId) -> list[Node]:
        """Get all children of a node."""
        self.get_node(node_id)  # Verify node exists
        child_ids = self._children.get(node_id, [])
        return [self._nodes[child_id] for child_id in child_ids]

    def get_siblings(self, node_id: NodeId) -> list[Node]:
        """Get all siblings of a node (including itself)."""
        node = self.get_node(node_id)

        if node.parent_id is None:
            # Root node has no siblings
            return [node]

        # Get parent's children (which includes this node)
        return self.get_children(node.parent_id)

    def get_parent(self, node_id: NodeId) -> Node | None:
        """Get the parent of a node."""
        node = self.get_node(node_id)
        if node.parent_id is None:
            return None
        return self._nodes[node.parent_id]

    def move_node(self, node_id: NodeId, new_parent_id: NodeId) -> Node:
        """Move a node to a new parent."""
        node = self.get_node(node_id)

        if node_id == self._root_id:
            raise InvalidOperationError("Cannot move root node")

        if new_parent_id not in self._nodes:
            raise TreeNotFoundError(f"New parent {new_parent_id} not found")

        # Check for circular reference
        if self._would_create_cycle(node_id, new_parent_id):
            raise CircularReferenceError(
                f"Moving {node_id} to {new_parent_id} would create a cycle"
            )

        old_parent_id = node.parent_id
        now = datetime.now()

        # Remove from old parent
        if old_parent_id:
            old_parent_children = self._children[old_parent_id]
            old_parent_children.remove(node_id)

            # Update old parent's is_leaf status
            if len(old_parent_children) == 0:
                old_parent = self._nodes[old_parent_id]
                self._nodes[old_parent_id] = old_parent.model_copy(
                    update={"is_leaf": True, "updated_at": now}
                )

        # Add to new parent
        self._children[new_parent_id].append(node_id)

        # Update new parent's is_leaf status
        new_parent = self._nodes[new_parent_id]
        self._nodes[new_parent_id] = new_parent.model_copy(
            update={"is_leaf": False, "updated_at": now}
        )

        # Update node's parent_id
        updated_node = node.model_copy(update={"parent_id": new_parent_id, "updated_at": now})
        self._nodes[node_id] = updated_node

        return updated_node

    def _would_create_cycle(self, node_id: NodeId, new_parent_id: NodeId) -> bool:
        """Check if moving node_id under new_parent_id would create a cycle."""
        # Walk up from new_parent_id to see if we reach node_id
        current: NodeId | None = new_parent_id
        while current is not None:
            if current == node_id:
                return True
            current_node = self._nodes[current]
            current = current_node.parent_id
        return False

    def get_root(self) -> Node | None:
        """Get the root node."""
        if self._root_id is None:
            return None
        return self._nodes[self._root_id]

    def node_count(self) -> int:
        """Get total number of nodes in the tree."""
        return len(self._nodes)
