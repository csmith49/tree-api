"""Node CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from tree.dependencies import (
    get_context_builder,
    get_link_builder,
    get_tree_service,
    get_zipper_service,
)
from tree.models.responses import (
    CollapseRequest,
    ExpandRequest,
    NodeCreate,
    NodeResponse,
    NodeUpdate,
)
from tree.services.tree import (
    InvalidOperationError,
    TreeNotFoundError,
    TreeService,
)
from tree.services.zipper import ZipperService
from tree.types import NodeId
from tree.utils.context import ContextBuilder
from tree.utils.link_builder import LinkBuilder

router = APIRouter()


def build_node_response(
    node_id: NodeId,
    tree: TreeService,
    context_builder: ContextBuilder,
    link_builder: LinkBuilder,
) -> NodeResponse:
    """Build a complete NodeResponse with context and links."""
    node = tree.get_node(node_id)
    context = context_builder.build_context(node_id)
    links = link_builder.build_links(node_id)

    return NodeResponse(
        id=node.id,
        parent_id=node.parent_id,
        description=node.description,
        metadata=node.metadata,
        is_leaf=node.is_leaf,
        created_at=node.created_at,
        updated_at=node.updated_at,
        context=context,
        links=links,
    )


@router.get("/root", response_model=NodeResponse)
def get_root(
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Get or create the root node."""
    root = tree.get_root()

    # Auto-create root if it doesn't exist
    if root is None:
        root = tree.create_node("root", "Root")

    return build_node_response("root", tree, context_builder, link_builder)


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: NodeId,
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Get a single node with HATEOAS links and context."""
    try:
        return build_node_response(node_id, tree, context_builder, link_builder)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{node_id}/children", response_model=list[NodeResponse])
def get_children(
    node_id: NodeId,
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> list[NodeResponse]:
    """Get all children of a node."""
    try:
        children = tree.get_children(node_id)
        return [
            build_node_response(child.id, tree, context_builder, link_builder) for child in children
        ]
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{parent_id}/children",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_child(
    parent_id: NodeId,
    node_data: NodeCreate,
    response: Response,
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Create a new child node."""
    try:
        tree.create_node(
            node_id=node_data.id,
            description=node_data.description,
            parent_id=parent_id,
            metadata=node_data.metadata,
        )
        # Set Location header
        response.headers["Location"] = f"/nodes/{node_data.id}"
        return build_node_response(node_data.id, tree, context_builder, link_builder)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: NodeId,
    node_data: NodeUpdate,
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Update a node's description or metadata."""
    try:
        tree.update_node(
            node_id=node_id,
            description=node_data.description,
            metadata=node_data.metadata,
        )
        return build_node_response(node_id, tree, context_builder, link_builder)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(
    node_id: NodeId,
    tree: TreeService = Depends(get_tree_service),
) -> None:
    """Delete a node and all its descendants."""
    try:
        tree.delete_node(node_id)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{node_id}/expand", response_model=NodeResponse)
def expand_node(
    node_id: NodeId,
    expand_data: ExpandRequest,
    zipper: ZipperService = Depends(get_zipper_service),
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Expand a leaf node into a branch with children."""
    try:
        children_data = [
            (child.id, child.description, child.metadata) for child in expand_data.children
        ]
        zipper.expand(node_id, children_data)
        return build_node_response(node_id, tree, context_builder, link_builder)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{node_id}/collapse", response_model=NodeResponse)
def collapse_node(
    node_id: NodeId,
    collapse_data: CollapseRequest,
    zipper: ZipperService = Depends(get_zipper_service),
    tree: TreeService = Depends(get_tree_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    link_builder: LinkBuilder = Depends(get_link_builder),
) -> NodeResponse:
    """Collapse a branch node into a leaf, deleting all descendants."""
    try:
        zipper.collapse(node_id, summary=collapse_data.summary)
        return build_node_response(node_id, tree, context_builder, link_builder)
    except TreeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
