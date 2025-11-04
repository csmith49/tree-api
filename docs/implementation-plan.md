# FastAPI Implementation Plan: Zipper-HATEOAS Tree API

## Overview

This document outlines the step-by-step implementation plan for building a FastAPI server that implements the zipper-HATEOAS tree navigation API as described in [zippers-plus-hateoas.md](zippers-plus-hateoas.md) and [api.md](api.md).

## Project Structure

```
tree-api/
├── tree/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── node.py          # Node data models (Pydantic)
│   │   ├── links.py         # HATEOAS link models
│   │   └── response.py      # Response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tree.py          # Tree operations & storage
│   │   ├── zipper.py        # Zipper navigation logic
│   │   └── traversal.py     # DFS/BFS traversal algorithms
│   ├── api/
│   │   ├── __init__.py
│   │   ├── nodes.py         # Node CRUD endpoints
│   │   ├── traversal.py     # Traversal endpoints
│   │   └── zoom.py          # Expand/collapse endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── link_builder.py  # HATEOAS link generation
│   │   └── context.py       # Context computation
│   └── config.py            # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   ├── test_traversal.py
│   ├── test_zoom.py
│   └── test_zipper.py
├── pyproject.toml           # Dependencies
└── README.md
```

## Implementation Phases

### Phase 1: Foundation & Data Models

**Goal:** Set up project infrastructure and core data models

#### 1.1 Project Setup
- [ ] Configure `pyproject.toml` with dependencies:
  - FastAPI
  - Uvicorn (ASGI server)
  - Pydantic v2
  - Python-multipart (for form data)
  - Pytest (testing)
  - httpx (test client)
- [ ] Set up development tools:
  - Ruff or Black (formatting)
  - mypy (type checking)
  - pytest-cov (coverage)

#### 1.2 Core Data Models (`tree/models/`)
- [ ] **`node.py`**: Define Node data structures
  ```python
  class NodeBase(BaseModel):
      description: str
      metadata: dict[str, Any] = {}

  class NodeCreate(NodeBase):
      pass

  class NodeUpdate(BaseModel):
      description: str | None = None
      parent_id: str | None = None

  class Node(NodeBase):
      id: str
      parent_id: str | None
      is_leaf: bool
      created_at: datetime
      updated_at: datetime
  ```

- [ ] **`links.py`**: Define HATEOAS link structures
  ```python
  class Link(BaseModel):
      href: str
      title: str | None = None
      method: str = "GET"

  class NavigationLinks(BaseModel):
      self: Link
      up: Link | None = None
      down: Link | None = None
      left: Link | None = None
      right: Link | None = None
      root: Link
      children: Link | None = None
      next_dfs: Link | None = None
      next_bfs: Link | None = None

  class Operation(BaseModel):
      href: str | None = None
      method: str | None = None
      accepts: str | None = None
      available: bool
      reason: str | None = None
  ```

- [ ] **`response.py`**: Define response schemas
  ```python
  class Context(BaseModel):
      depth: int
      sibling_position: int
      total_siblings: int
      has_children: bool
      children_count: int
      breadcrumbs: list[dict[str, str]]

  class NodeResponse(BaseModel):
      id: str
      description: str
      is_leaf: bool
      parent_id: str | None = None
      metadata: dict[str, Any] = {}
      _context: Context
      _links: NavigationLinks
      _operations: dict[str, Operation]
  ```

### Phase 2: Core Services & Business Logic

**Goal:** Implement tree storage and zipper navigation logic

#### 2.1 Tree Service (`tree/services/tree.py`)
- [ ] In-memory tree storage (dict-based initially)
  ```python
  class TreeService:
      def __init__(self):
          self._nodes: dict[str, Node] = {}
          self._children: dict[str, list[str]] = {}

      def create_node(parent_id: str | None, data: NodeCreate) -> Node
      def get_node(node_id: str) -> Node | None
      def update_node(node_id: str, data: NodeUpdate) -> Node
      def delete_node(node_id: str) -> bool
      def get_children(node_id: str) -> list[Node]
      def get_siblings(node_id: str) -> list[Node]
      def get_parent(node_id: str) -> Node | None
      def move_node(node_id: str, new_parent_id: str) -> Node
  ```

- [ ] Validation logic:
  - Prevent circular references
  - Ensure root node cannot be deleted
  - Validate parent existence
  - Check for orphaned nodes

#### 2.2 Zipper Service (`tree/services/zipper.py`)
- [ ] Implement zipper navigation operations:
  ```python
  class ZipperService:
      def __init__(self, tree_service: TreeService):
          self.tree = tree_service

      def up(node_id: str) -> Node | None
      def down(node_id: str) -> Node | None
      def left(node_id: str) -> Node | None
      def right(node_id: str) -> Node | None
      def root() -> Node
  ```

- [ ] Zoom operations:
  ```python
  def expand(node_id: str, children: list[NodeCreate]) -> Node
  def collapse(node_id: str, summary: str | None) -> Node
  ```

- [ ] Validation:
  - Can only expand leaf nodes
  - Can only collapse non-leaf nodes
  - Handle empty children lists

#### 2.3 Traversal Service (`tree/services/traversal.py`)
- [ ] DFS traversal algorithm:
  ```python
  def compute_next_dfs(node_id: str) -> Node | None:
      # Priority: down > right > (up then right)
      pass

  def compute_prev_dfs(node_id: str) -> Node | None:
      pass
  ```

- [ ] BFS traversal algorithm:
  ```python
  def compute_next_bfs(node_id: str) -> Node | None:
      # Level-order traversal
      pass
  ```

- [ ] Full traversal generators:
  ```python
  def traverse_dfs(start_node_id: str) -> Iterator[Node]
  def traverse_bfs(start_node_id: str) -> Iterator[Node]
  ```

### Phase 3: HATEOAS Link Generation

**Goal:** Automatically compute links and context for responses

#### 3.1 Link Builder (`tree/utils/link_builder.py`)
- [ ] Implement link computation:
  ```python
  class LinkBuilder:
      def __init__(self, tree: TreeService, zipper: ZipperService):
          self.tree = tree
          self.zipper = zipper

      def build_links(node: Node) -> NavigationLinks:
          """Compute all valid navigation links from node"""
          links = NavigationLinks(
              self=Link(href=f"/nodes/{node.id}"),
              root=Link(href="/nodes/root")
          )

          # Add up/down/left/right based on tree structure
          # Add next-dfs/next-bfs from traversal service
          return links

      def build_operations(node: Node) -> dict[str, Operation]:
          """Compute available operations based on node state"""
          ops = {
              "modify": Operation(
                  href=f"/nodes/{node.id}",
                  method="PATCH",
                  available=True
              ),
              "delete": Operation(
                  href=f"/nodes/{node.id}",
                  method="DELETE",
                  available=not node.is_root
              )
          }

          # Add expand/collapse based on is_leaf
          return ops
  ```

#### 3.2 Context Builder (`tree/utils/context.py`)
- [ ] Implement context computation:
  ```python
  class ContextBuilder:
      def __init__(self, tree: TreeService):
          self.tree = tree

      def build_context(node: Node) -> Context:
          """Build zipper-style context with breadcrumbs"""
          breadcrumbs = self._compute_breadcrumbs(node)
          siblings = self.tree.get_siblings(node.id)
          children = self.tree.get_children(node.id)

          return Context(
              depth=len(breadcrumbs),
              sibling_position=siblings.index(node),
              total_siblings=len(siblings),
              has_children=not node.is_leaf,
              children_count=len(children),
              breadcrumbs=breadcrumbs
          )

      def _compute_breadcrumbs(node: Node) -> list[dict]:
          """Walk up to root building breadcrumb trail"""
          breadcrumbs = []
          current = node.parent_id
          while current:
              parent = self.tree.get_node(current)
              breadcrumbs.insert(0, {
                  "id": parent.id,
                  "description": parent.description
              })
              current = parent.parent_id
          return breadcrumbs
  ```

### Phase 4: API Endpoints

**Goal:** Expose tree operations through REST API

#### 4.1 Node CRUD Endpoints (`tree/api/nodes.py`)
- [ ] **GET `/nodes/{id}`** - Get single node with links
  - Query params: `?expand=children,parent&depth=1&fields=id,description`
  - Returns: Full `NodeResponse` with HATEOAS links
  - Status: 200 OK, 404 Not Found

- [ ] **GET `/nodes/{id}/children`** - Get all children
  - Query params: `?limit=50&offset=0`
  - Returns: List of `NodeResponse` objects
  - Status: 200 OK

- [ ] **GET `/nodes/{id}/breadcrumbs`** - Get path to root
  - Returns: Array of parent nodes from root to current
  - Status: 200 OK

- [ ] **POST `/nodes/{parentId}/children`** - Create child node
  - Body: `NodeCreate`
  - Returns: Created `NodeResponse` with location header
  - Status: 201 Created, 404 Parent Not Found

- [ ] **PATCH `/nodes/{id}`** - Update node
  - Body: `NodeUpdate` (description or parent_id)
  - Returns: Updated `NodeResponse`
  - Status: 200 OK, 404 Not Found, 409 Conflict (circular ref)

- [ ] **DELETE `/nodes/{id}`** - Delete node
  - Returns: 204 No Content
  - Status: 404 Not Found, 409 Conflict (is root)

#### 4.2 Traversal Endpoints (`tree/api/traversal.py`)
- [ ] **GET `/nodes/{id}/next?order=dfs`** - Next in DFS order
  - Returns: `NodeResponse` or 404 if no next
  - Status: 200 OK, 404 Not Found

- [ ] **GET `/nodes/{id}/next?order=bfs`** - Next in BFS order
  - Returns: `NodeResponse` or 404 if no next
  - Status: 200 OK, 404 Not Found

- [ ] Optional: Full traversal endpoints
  - **GET `/nodes/{id}/traverse?order=dfs&limit=100`**
  - Returns: Paginated list of nodes in traversal order

#### 4.3 Zoom Endpoints (`tree/api/zoom.py`)
- [ ] **POST `/nodes/{id}/expand`** - Expand leaf to branch
  - Body: `{"children": [NodeCreate, ...]}`
  - Returns: Updated `NodeResponse` with new children
  - Status: 200 OK, 409 Conflict (already has children)

- [ ] **POST `/nodes/{id}/collapse`** - Collapse branch to leaf
  - Body: `{"summary": "optional updated description"}`
  - Returns: Updated `NodeResponse` as leaf
  - Status: 200 OK, 409 Conflict (already leaf)
  - Side effect: Deletes all descendant nodes

#### 4.4 Root Endpoint
- [ ] **GET `/nodes/root`** - Get or create root node
  - Auto-creates root if doesn't exist
  - Returns: `NodeResponse`

#### 4.5 Main App (`tree/main.py`)
- [ ] FastAPI app setup:
  ```python
  from fastapi import FastAPI
  from tree.api import nodes, traversal, zoom

  app = FastAPI(title="Tree Zipper API", version="1.0.0")

  app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
  app.include_router(traversal.router, prefix="/nodes", tags=["traversal"])
  app.include_router(zoom.router, prefix="/nodes", tags=["zoom"])

  @app.get("/")
  def read_root():
      return {
          "message": "Tree Zipper API",
          "_links": {
              "root": {"href": "/nodes/root"},
              "docs": {"href": "/docs"}
          }
      }
  ```

- [ ] Dependency injection setup:
  ```python
  def get_tree_service() -> TreeService:
      # Singleton instance
      return tree_service

  def get_zipper_service(tree: TreeService = Depends(get_tree_service)) -> ZipperService:
      return ZipperService(tree)
  ```

- [ ] CORS middleware (if needed)
- [ ] Exception handlers for 404, 409, 500

### Phase 5: Error Handling & Validation

**Goal:** Robust error handling with helpful error responses

#### 5.1 Custom Exceptions
- [ ] Define domain exceptions:
  ```python
  class NodeNotFoundError(Exception): pass
  class CircularReferenceError(Exception): pass
  class InvalidOperationError(Exception): pass
  class RootNodeError(Exception): pass
  ```

#### 5.2 Exception Handlers
- [ ] Convert exceptions to HTTP responses:
  ```python
  @app.exception_handler(NodeNotFoundError)
  async def node_not_found_handler(request, exc):
      return JSONResponse(
          status_code=404,
          content={
              "error": "Node not found",
              "message": str(exc),
              "_links": {
                  "root": {"href": "/nodes/root"}
              }
          }
      )
  ```

#### 5.3 Validation
- [ ] Request validation with Pydantic
- [ ] Business rule validation in services
- [ ] Return helpful error messages with links to valid states

### Phase 6: Testing

**Goal:** Comprehensive test coverage

#### 6.1 Unit Tests
- [ ] Test tree service operations (CRUD)
- [ ] Test zipper navigation (up/down/left/right)
- [ ] Test traversal algorithms (DFS/BFS correctness)
- [ ] Test link builder (correct link generation)
- [ ] Test context builder (breadcrumbs, position)

#### 6.2 Integration Tests
- [ ] Test API endpoints with TestClient
- [ ] Test full navigation workflows
- [ ] Test expand/collapse operations
- [ ] Test error cases (404, 409)
- [ ] Test HATEOAS link correctness

#### 6.3 Test Fixtures
- [ ] Create sample tree structures:
  ```python
  @pytest.fixture
  def sample_tree():
      """
      root
      ├── A
      │   ├── A1
      │   └── A2
      └── B
          └── B1
      """
      return build_sample_tree()
  ```

### Phase 7: Advanced Features (Optional)

#### 7.1 Query Parameter Support
- [ ] `?expand=children,parent` - Eager load related nodes
- [ ] `?depth=N` - Control traversal depth
- [ ] `?fields=id,description` - Sparse fieldsets

#### 7.2 Pagination
- [ ] Paginate children lists for large nodes
- [ ] Cursor-based pagination for traversals

#### 7.3 Caching
- [ ] ETag support for node versioning
- [ ] Cache-Control headers
- [ ] Conditional requests (If-None-Match)

#### 7.4 Persistence
- [ ] Replace in-memory storage with database:
  - SQLite for simple deployment
  - PostgreSQL with ltree for production
  - MongoDB for document-style storage

#### 7.5 WebSocket Support
- [ ] Real-time tree updates
- [ ] Push notifications for node changes

#### 7.6 Batch Operations
- [ ] `POST /nodes/batch/expand` - Expand multiple nodes
- [ ] `POST /nodes/batch/move` - Move multiple nodes

## Implementation Sequence

### Week 1: Foundation
1. Setup project (pyproject.toml, structure)
2. Implement data models (Phase 1.2)
3. Implement tree service (Phase 2.1)
4. Write tests for tree service

### Week 2: Navigation
5. Implement zipper service (Phase 2.2)
6. Implement traversal service (Phase 2.3)
7. Write tests for zipper and traversal
8. Implement link builder (Phase 3.1)

### Week 3: API Endpoints
9. Implement context builder (Phase 3.2)
10. Implement node CRUD endpoints (Phase 4.1)
11. Implement traversal endpoints (Phase 4.2)
12. Write integration tests for endpoints

### Week 4: Polish
13. Implement zoom endpoints (Phase 4.3)
14. Implement error handling (Phase 5)
15. Complete test coverage (Phase 6)
16. Documentation and examples

### Week 5+: Advanced (Optional)
17. Add query parameter support
18. Add pagination
19. Add caching/ETags
20. Replace in-memory storage with DB

## Key Design Decisions

### 1. Storage Strategy
**Initial:** In-memory dictionary for simplicity
- `_nodes: dict[str, Node]` - Node lookup
- `_children: dict[str, list[str]]` - Parent-to-children mapping
- `_root_id: str` - Root node reference

**Future:** PostgreSQL with ltree extension for hierarchical queries

### 2. ID Generation
Use UUID4 for node IDs:
```python
import uuid
node_id = str(uuid.uuid4())
```
Benefits: No collision risk, globally unique, URL-safe

### 3. URL Structure
Follow REST conventions:
- `/nodes/{id}` - Resource-oriented
- `/nodes/{id}/children` - Sub-resource
- `/nodes/{id}/next?order=dfs` - Query params for variants

### 4. Link Relations
Use semantic link relations:
- `up`, `down`, `left`, `right` - Zipper navigation
- `next-dfs`, `next-bfs` - Traversal
- `self`, `root` - Standard HATEOAS

### 5. Response Format
Include three sections in every node response:
1. **Data**: Node properties (id, description, etc.)
2. **`_context`**: Position information (depth, breadcrumbs, etc.)
3. **`_links`**: Navigation links
4. **`_operations`**: Available actions with availability status

### 6. Error Responses
Include helpful links in errors:
```json
{
  "error": "Node not found",
  "message": "Node 'abc123' does not exist",
  "_links": {
    "root": {"href": "/nodes/root"},
    "docs": {"href": "/docs"}
  }
}
```

## Success Criteria

### Functional
- [ ] All 10 core endpoints working
- [ ] HATEOAS links correctly generated
- [ ] Zipper navigation (up/down/left/right) functional
- [ ] DFS and BFS traversal working
- [ ] Expand/collapse operations working
- [ ] Proper error handling (404, 409)

### Non-Functional
- [ ] 90%+ test coverage
- [ ] API documented with OpenAPI/Swagger
- [ ] Response time < 100ms for single node operations
- [ ] Type-safe (passes mypy --strict)
- [ ] Clean code (passes ruff/black)

### Documentation
- [ ] README with quickstart guide
- [ ] API examples for common workflows
- [ ] Architecture decision records (ADRs)
- [ ] Deployment guide

## Common Pitfalls to Avoid

1. **Circular References**: Always validate parent_id changes to prevent cycles
2. **Orphaned Nodes**: When deleting, decide whether to cascade or prevent deletion
3. **Race Conditions**: Consider concurrent modifications (add locking if needed)
4. **Large Trees**: Implement pagination early to avoid performance issues
5. **Link Explosion**: Be selective about which links to include (avoid over-engineering)
6. **Tight Coupling**: Keep link generation separate from business logic
7. **Over-Normalization**: Balance between "pure REST" and practical usability

## Resources

- FastAPI docs: https://fastapi.tiangolo.com
- HATEOAS: https://en.wikipedia.org/wiki/HATEOAS
- Zipper paper: Huet, G. (1997). "The Zipper"
- HAL specification: http://stateless.co/hal_specification.html
- JSON:API: https://jsonapi.org

## Next Steps

After implementation:
1. Deploy to production environment
2. Create client libraries (Python, TypeScript)
3. Build example applications (task planner, mind mapper)
4. Monitor performance and optimize
5. Gather user feedback and iterate
