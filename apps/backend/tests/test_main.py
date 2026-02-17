"""Tests for the FastAPI application."""

import pytest
from httpx import AsyncClient, ASGITransport

from scaffold_ai.main import app


@pytest.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health(client):
    """Test the health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_chat_new_feature(client):
    """Test chat endpoint with a new feature request."""
    response = await client.post(
        "/api/chat",
        json={
            "user_input": "Add a database to store user data",
            "graph_json": {"nodes": [], "edges": []},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_sample_graph(client):
    """Test the sample graph endpoint."""
    response = await client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
