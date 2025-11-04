"""Integration tests for the Tree API."""

import pytest
from fastapi.testclient import TestClient

from tree.main import app


@pytest.fixture(autouse=True)
def reset_services():
    """Reset singleton services before each test."""
    import tree.dependencies as deps

    deps._tree_service = None
    deps._zipper_service = None
    deps._traversal_service = None
    deps._context_builder = None
    deps._link_builder = None
    yield


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestRootEndpoint:
    """Test root endpoints."""

    def test_get_api_root(self, client: TestClient) -> None:
        """Test getting API root."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "links" in data

    def test_get_or_create_root_node(self, client: TestClient) -> None:
        """Test getting/creating root node."""
        response = client.get("/nodes/root")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == "root"
        assert data["is_leaf"] is True
        assert "context" in data
        assert "links" in data
        assert data["context"]["depth"] == 0


class TestNodeCRUD:
    """Test node CRUD operations."""

    def test_get_nonexistent_node_returns_404(self, client: TestClient) -> None:
        """Test getting a non-existent node."""
        response = client.get("/nodes/nonexistent")
        assert response.status_code == 404

    def test_create_and_get_child_node(self, client: TestClient) -> None:
        """Test creating and retrieving a child node."""
        # First create root
        client.get("/nodes/root")

        # Create child
        create_response = client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "Child 1", "metadata": {"key": "value"}},
        )
        assert create_response.status_code == 201
        assert "Location" in create_response.headers
        assert create_response.headers["Location"] == "/nodes/child-1"

        created_data = create_response.json()
        assert created_data["id"] == "child-1"
        assert created_data["parent_id"] == "root"
        assert created_data["description"] == "Child 1"
        assert created_data["metadata"] == {"key": "value"}
        assert created_data["is_leaf"] is True

        # Verify we can get it
        get_response = client.get("/nodes/child-1")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == "child-1"

    def test_create_child_with_invalid_parent_returns_404(self, client: TestClient) -> None:
        """Test creating a child with non-existent parent."""
        response = client.post(
            "/nodes/nonexistent/children",
            json={"id": "child-1", "description": "Child 1"},
        )
        assert response.status_code == 404

    def test_create_duplicate_node_returns_409(self, client: TestClient) -> None:
        """Test creating a duplicate node."""
        client.get("/nodes/root")
        client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "Child 1"},
        )

        # Try to create duplicate
        response = client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "Duplicate"},
        )
        assert response.status_code == 409

    def test_update_node_description(self, client: TestClient) -> None:
        """Test updating a node's description."""
        client.get("/nodes/root")
        client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "Original"},
        )

        # Update description
        response = client.patch(
            "/nodes/child-1",
            json={"description": "Updated"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"

        # Verify persistence
        get_response = client.get("/nodes/child-1")
        assert get_response.json()["description"] == "Updated"

    def test_update_node_metadata(self, client: TestClient) -> None:
        """Test updating a node's metadata."""
        client.get("/nodes/root")
        client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "Test", "metadata": {"old": "value"}},
        )

        # Update metadata
        response = client.patch(
            "/nodes/child-1",
            json={"metadata": {"new": "data"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"] == {"new": "data"}

    def test_update_nonexistent_node_returns_404(self, client: TestClient) -> None:
        """Test updating a non-existent node."""
        response = client.patch(
            "/nodes/nonexistent",
            json={"description": "Updated"},
        )
        assert response.status_code == 404

    def test_delete_node(self, client: TestClient) -> None:
        """Test deleting a node."""
        client.get("/nodes/root")
        client.post(
            "/nodes/root/children",
            json={"id": "child-1", "description": "To delete"},
        )

        # Delete the node
        response = client.delete("/nodes/child-1")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get("/nodes/child-1")
        assert get_response.status_code == 404

    def test_delete_nonexistent_node_returns_404(self, client: TestClient) -> None:
        """Test deleting a non-existent node."""
        response = client.delete("/nodes/nonexistent")
        assert response.status_code == 404

    def test_delete_root_node_returns_409(self, client: TestClient) -> None:
        """Test that deleting root node fails."""
        client.get("/nodes/root")

        response = client.delete("/nodes/root")
        assert response.status_code == 409


class TestChildren:
    """Test children endpoints."""

    def test_get_children_of_leaf_returns_empty(self, client: TestClient) -> None:
        """Test getting children of a leaf node."""
        client.get("/nodes/root")

        response = client.get("/nodes/root/children")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_children_of_branch(self, client: TestClient) -> None:
        """Test getting children of a branch node."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "child-1", "description": "Child 1"})
        client.post("/nodes/root/children", json={"id": "child-2", "description": "Child 2"})

        response = client.get("/nodes/root/children")
        assert response.status_code == 200
        children = response.json()
        assert len(children) == 2
        assert {c["id"] for c in children} == {"child-1", "child-2"}

    def test_get_children_of_nonexistent_node_returns_404(self, client: TestClient) -> None:
        """Test getting children of non-existent node."""
        response = client.get("/nodes/nonexistent/children")
        assert response.status_code == 404


class TestHATEOAS:
    """Test HATEOAS links in responses."""

    def test_node_response_includes_links(self, client: TestClient) -> None:
        """Test that node responses include HATEOAS links."""
        client.get("/nodes/root")
        response = client.get("/nodes/root")

        data = response.json()
        assert "links" in data
        links = data["links"]

        # Should always have self and root
        assert "self" in links
        assert "root" in links
        assert links["self"]["href"] == "root"

    def test_links_reflect_tree_structure(self, client: TestClient) -> None:
        """Test that links accurately reflect tree structure."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "child-1", "description": "Child 1"})

        # Root should now have down link
        root_response = client.get("/nodes/root")
        root_links = root_response.json()["links"]
        assert "down" in root_links
        assert root_links["down"]["href"] == "child-1"

        # Child should have up link
        child_response = client.get("/nodes/child-1")
        child_links = child_response.json()["links"]
        assert "up" in child_links
        assert child_links["up"]["href"] == "root"

    def test_sibling_links(self, client: TestClient) -> None:
        """Test left/right sibling links."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "child-1", "description": "Child 1"})
        client.post("/nodes/root/children", json={"id": "child-2", "description": "Child 2"})

        # First child should have right link
        child1_response = client.get("/nodes/child-1")
        child1_links = child1_response.json()["links"]
        assert "right" in child1_links
        assert child1_links["right"]["href"] == "child-2"
        assert "left" not in child1_links

        # Second child should have left link
        child2_response = client.get("/nodes/child-2")
        child2_links = child2_response.json()["links"]
        assert "left" in child2_links
        assert child2_links["left"]["href"] == "child-1"
        assert "right" not in child2_links


class TestContext:
    """Test context information in responses."""

    def test_context_includes_depth(self, client: TestClient) -> None:
        """Test that context includes correct depth."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "child-1", "description": "Child 1"})
        client.post("/nodes/child-1/children", json={"id": "grandchild-1", "description": "GC 1"})

        # Root depth = 0
        root_response = client.get("/nodes/root")
        assert root_response.json()["context"]["depth"] == 0

        # Child depth = 1
        child_response = client.get("/nodes/child-1")
        assert child_response.json()["context"]["depth"] == 1

        # Grandchild depth = 2
        gc_response = client.get("/nodes/grandchild-1")
        assert gc_response.json()["context"]["depth"] == 2

    def test_context_includes_breadcrumbs(self, client: TestClient) -> None:
        """Test that context includes breadcrumbs."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "child-1", "description": "Child 1"})

        response = client.get("/nodes/child-1")
        context = response.json()["context"]

        assert len(context["breadcrumbs"]) == 1
        assert context["breadcrumbs"][0]["id"] == "root"


class TestZoomOperations:
    """Test expand/collapse operations."""

    def test_expand_leaf_node(self, client: TestClient) -> None:
        """Test expanding a leaf node."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "leaf", "description": "Leaf"})

        # Expand the leaf
        response = client.post(
            "/nodes/leaf/expand",
            json={
                "children": [
                    {"id": "new-1", "description": "New 1"},
                    {"id": "new-2", "description": "New 2"},
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_leaf"] is False

        # Verify children were created
        children_response = client.get("/nodes/leaf/children")
        children = children_response.json()
        assert len(children) == 2

    def test_expand_branch_returns_409(self, client: TestClient) -> None:
        """Test that expanding a branch node fails."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "branch", "description": "Branch"})
        client.post("/nodes/branch/children", json={"id": "child", "description": "Child"})

        # Try to expand already-expanded node
        response = client.post(
            "/nodes/branch/expand",
            json={"children": [{"id": "new", "description": "New"}]},
        )
        assert response.status_code == 409

    def test_collapse_branch_node(self, client: TestClient) -> None:
        """Test collapsing a branch node."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "branch", "description": "Branch"})
        client.post("/nodes/branch/children", json={"id": "child", "description": "Child"})

        # Collapse the branch
        response = client.post(
            "/nodes/branch/collapse",
            json={"summary": "Collapsed branch"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_leaf"] is True
        assert data["description"] == "Collapsed branch"

        # Verify children were deleted
        child_response = client.get("/nodes/child")
        assert child_response.status_code == 404

    def test_collapse_leaf_returns_409(self, client: TestClient) -> None:
        """Test that collapsing a leaf node fails."""
        client.get("/nodes/root")
        client.post("/nodes/root/children", json={"id": "leaf", "description": "Leaf"})

        response = client.post(
            "/nodes/leaf/collapse",
            json={},
        )
        assert response.status_code == 409
