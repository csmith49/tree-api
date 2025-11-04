Design recommendation for your planning tool
Start with this minimal core (10 operations):
Nodes (6):
GET    /nodes/{id}                # With ?expand, ?depth options
GET    /nodes/{id}/children
GET    /nodes/{id}/breadcrumbs    # Path to root
POST   /nodes/{parentId}/children # Create child
PATCH  /nodes/{id}                # Update description or move
DELETE /nodes/{id}                # Delete node
Traversal (2):
GET /nodes/{id}/next?order=dfs    # Next in depth-first
GET /nodes/{id}/next?order=bfs    # Next in breadth-first
Zoom operations (2):
POST /nodes/{id}/expand           # Convert leaf to branch
POST /nodes/{id}/collapse         # Convert branch to leaf
Every response includes HATEOAS links:
json{
  "id": "node1",
  "description": "Gather requirements",
  "parentId": "root",
  "isLeaf": false,
  "_links": {
    "self": {"href": "/nodes/node1"},
    "parent": {"href": "/nodes/root"},
    "children": {"href": "/nodes/node1/children"},
    "next-dfs": {"href": "/nodes/node2"},
    "prev-sibling": {"href": "/nodes/node0"},
    "expand": {"href": "/nodes/node1/expand", "method": "POST"},
    "collapse": {"href": "/nodes/node1/collapse", "method": "POST"}
  }
}
This design:

✅ Minimal: 10 endpoints cover all requirements
✅ Elegant: Follows established patterns (zipper + REST)
✅ Complete: Handles all operations (zoom, traverse, CRUD, breadcrumbs)
✅ Extensible: Easy to add features without breaking changes
✅ Standard: Uses industry best practices (HATEOAS, query params)
✅ Efficient: Lazy loading default, explicit expansion

Implementation notes
Query parameters to support:

?expand=children,parent — Include related nodes
?depth=0|1|2|n — Control traversal depth
?fields=id,description — Sparse fieldsets

Response codes:

200 OK — Successful read
201 Created — Node created
204 No Content — Successful delete
404 Not Found — Node doesn't exist
409 Conflict — Invalid operation (e.g., collapse leaf, expand non-leaf)

Validation rules:

Cannot expand non-leaf nodes (already have children)
Cannot collapse leaf nodes (no children to collapse)
Cannot move node to its own descendant (circular reference)
Cannot delete root node

Performance considerations:

Cache node responses with ETags
Paginate children for nodes with many descendants
Consider max depth limits for recursive expansion
Index parentId for efficient child queries

This minimal API design synthesizes the best ideas from functional programming zippers and REST API patterns, providing a clean, elegant interface for manipulating tree-structured agent plans.
