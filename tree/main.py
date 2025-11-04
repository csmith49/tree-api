"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from tree.api import nodes

app = FastAPI(
    title="Tree Zipper API",
    version="1.0.0",
    description="REST API implementing zipper-style tree navigation with HATEOAS",
)

# Include routers
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])


@app.get("/", response_class=JSONResponse)
def read_root() -> dict[str, str | dict[str, dict[str, str]]]:
    """API root with links to main endpoints."""
    return {
        "message": "Tree Zipper API",
        "links": {
            "root": {"href": "/nodes/root", "title": "Get root node"},
            "docs": {"href": "/docs", "title": "API documentation"},
        },
    }
