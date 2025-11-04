"""Dependency injection for FastAPI."""

from tree.services.traversal import TraversalService
from tree.services.tree import TreeService
from tree.services.zipper import ZipperService
from tree.utils.context import ContextBuilder
from tree.utils.link_builder import LinkBuilder

# Singleton instances
_tree_service: TreeService | None = None
_zipper_service: ZipperService | None = None
_traversal_service: TraversalService | None = None
_context_builder: ContextBuilder | None = None
_link_builder: LinkBuilder | None = None


def get_tree_service() -> TreeService:
    """Get or create the TreeService singleton."""
    global _tree_service
    if _tree_service is None:
        _tree_service = TreeService()
    return _tree_service


def get_zipper_service() -> ZipperService:
    """Get or create the ZipperService singleton."""
    global _zipper_service
    if _zipper_service is None:
        tree = get_tree_service()
        _zipper_service = ZipperService(tree)
    return _zipper_service


def get_traversal_service() -> TraversalService:
    """Get or create the TraversalService singleton."""
    global _traversal_service
    if _traversal_service is None:
        tree = get_tree_service()
        _traversal_service = TraversalService(tree)
    return _traversal_service


def get_context_builder() -> ContextBuilder:
    """Get or create the ContextBuilder singleton."""
    global _context_builder
    if _context_builder is None:
        tree = get_tree_service()
        _context_builder = ContextBuilder(tree)
    return _context_builder


def get_link_builder() -> LinkBuilder:
    """Get or create the LinkBuilder singleton."""
    global _link_builder
    if _link_builder is None:
        tree = get_tree_service()
        zipper = get_zipper_service()
        traversal = get_traversal_service()
        _link_builder = LinkBuilder(tree, zipper, traversal)
    return _link_builder
