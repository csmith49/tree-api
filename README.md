# Tree Zipper API

FastAPI server implementing zipper-HATEOAS tree navigation for elegant tree manipulation.

## Overview

This API combines **zipper semantics** (focus + context, efficient navigation) with **HATEOAS** (hypermedia links, self-describing resources) to create an API where:
- Each node response includes its "context" (position in tree)
- Links encode all valid zipper operations from current position
- Server computes available moves; client follows links
- No client-side tree model needed - pure hypermedia navigation

See [docs/zippers-plus-hateoas.md](docs/zippers-plus-hateoas.md) for the design philosophy.

## Installation

```bash
# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Run the server
uvicorn tree.main:app --reload

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## API Endpoints

### Node Operations (6 endpoints)
- `GET /nodes/{id}` - Get node with HATEOAS links
- `GET /nodes/{id}/children` - Get all children
- `GET /nodes/{id}/breadcrumbs` - Get path to root
- `POST /nodes/{parentId}/children` - Create child node
- `PATCH /nodes/{id}` - Update node
- `DELETE /nodes/{id}` - Delete node

### Traversal (2 endpoints)
- `GET /nodes/{id}/next?order=dfs` - Next in depth-first order
- `GET /nodes/{id}/next?order=bfs` - Next in breadth-first order

### Zoom Operations (2 endpoints)
- `POST /nodes/{id}/expand` - Expand leaf to branch
- `POST /nodes/{id}/collapse` - Collapse branch to leaf

## Example Response

```json
{
  "id": "node-42",
  "description": "Implement authentication",
  "isLeaf": false,

  "_context": {
    "depth": 2,
    "siblingPosition": 1,
    "totalSiblings": 3,
    "hasChildren": true,
    "breadcrumbs": [
      {"id": "root", "description": "Build web app"},
      {"id": "node-10", "description": "Backend services"}
    ]
  },

  "_links": {
    "self": {"href": "/nodes/node-42"},
    "up": {"href": "/nodes/node-10", "title": "Parent: Backend services"},
    "down": {"href": "/nodes/node-42-child-1", "title": "First child: Set up JWT"},
    "left": {"href": "/nodes/node-41", "title": "Previous sibling"},
    "right": {"href": "/nodes/node-43", "title": "Next sibling"},
    "next-dfs": {"href": "/nodes/node-42-child-1"}
  },

  "_operations": {
    "modify": {"href": "/nodes/node-42", "method": "PATCH", "available": true},
    "expand": {"available": false, "reason": "Node already has children"},
    "collapse": {"href": "/nodes/node-42/collapse", "method": "POST", "available": true}
  }
}
```

## Development

```bash
# Run tests
pytest

# Type checking
mypy tree

# Code formatting
ruff format tree

# Linting
ruff check tree
```

## Project Structure

```
tree-api/
├── tree/              # Main package
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   ├── api/           # API endpoints
│   └── utils/         # Helper functions
├── tests/             # Test suite
└── docs/              # Documentation
```

## Documentation

- [API Design](docs/api.md) - Minimal API specification
- [Zipper-HATEOAS Design](docs/zippers-plus-hateoas.md) - Design philosophy
- [Implementation Plan](docs/implementation-plan.md) - Step-by-step implementation guide

## License

MIT
