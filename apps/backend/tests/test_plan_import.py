"""Tests for plan import API endpoints."""

import pytest
from fastapi.testclient import TestClient

from scaffold_ai.main import app

client = TestClient(app)


def test_import_plan_success():
    """Test successful plan import."""
    plan_data = {
        "plan_id": "test-plan-123",
        "project_name": "Test Project",
        "description": "A test project description",
        "architecture": "Full Serverless",
        "tech_stack": {
            "frontend": "React",
            "backend": "Lambda",
            "database": "DynamoDB",
        },
        "requirements": {
            "users": "1K-10K",
            "uptime": "99.9%",
            "data_size": "<1GB",
        },
    }

    response = client.post("/api/import/plan", json=plan_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert data["message"] == "Plan imported successfully"
    assert "initial_prompt" in data
    assert "Test Project" in data["initial_prompt"]
    assert "Full Serverless" in data["initial_prompt"]


def test_import_plan_with_full_plan():
    """Test plan import with full plan data."""
    plan_data = {
        "plan_id": "test-plan-456",
        "project_name": "Full Test",
        "description": "Complete test",
        "architecture": "Hybrid",
        "tech_stack": {"api": "FastAPI"},
        "requirements": {"users": "100-1K"},
        "full_plan": {
            "basics": {"name": "Full Test"},
            "technical": {"user_count": "100-1K"},
        },
    }

    response = client.post("/api/import/plan", json=plan_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


def test_get_imported_plan():
    """Test retrieving an imported plan."""
    # First import a plan
    plan_data = {
        "plan_id": "test-retrieve",
        "project_name": "Retrieve Test",
        "description": "Test retrieval",
        "architecture": "Serverless",
        "tech_stack": {"frontend": "Vue"},
        "requirements": {"users": "<100"},
    }

    import_response = client.post("/api/import/plan", json=plan_data)
    session_id = import_response.json()["session_id"]

    # Now retrieve it
    response = client.get(f"/api/import/plan/{session_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["plan_id"] == "test-retrieve"
    assert data["project_name"] == "Retrieve Test"
    assert data["architecture"] == "Serverless"
    assert data["tech_stack"]["frontend"] == "Vue"
    assert "imported_at" in data


def test_get_nonexistent_plan():
    """Test retrieving a plan that doesn't exist."""
    response = client.get("/api/import/plan/nonexistent-session-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_import_plan_missing_fields():
    """Test plan import with missing required fields."""
    incomplete_data = {
        "plan_id": "incomplete",
        # Missing required fields
    }

    response = client.post("/api/import/plan", json=incomplete_data)
    
    # Should fail validation
    assert response.status_code == 422


def test_import_plan_rate_limit():
    """Test that rate limiting is applied to import endpoint."""
    # Make multiple requests
    responses = []
    for i in range(25):  # Exceed the 20/minute limit
        plan_data = {
            "plan_id": f"rate-test-{i}",
            "project_name": "Rate Test",
            "description": "Testing rate limits",
            "architecture": "Serverless",
            "tech_stack": {"api": "FastAPI"},
            "requirements": {"users": "<100"},
        }
        response = client.post("/api/import/plan", json=plan_data)
        responses.append(response.status_code)

    # At least one should be rate limited
    assert 429 in responses


def test_initial_prompt_format():
    """Test that the initial prompt is properly formatted."""
    plan_data = {
        "plan_id": "prompt-test",
        "project_name": "Prompt Format Test",
        "description": "Testing prompt generation",
        "architecture": "Microservices",
        "tech_stack": {
            "frontend": "Angular",
            "backend": "Spring Boot",
            "database": "PostgreSQL",
        },
        "requirements": {
            "users": "10K-100K",
            "uptime": "99.99%",
            "data_size": "10-100GB",
        },
    }

    response = client.post("/api/import/plan", json=plan_data)
    prompt = response.json()["initial_prompt"]

    # Verify prompt contains all key information
    assert "Prompt Format Test" in prompt
    assert "Microservices" in prompt
    assert "Angular" in prompt
    assert "Spring Boot" in prompt
    assert "PostgreSQL" in prompt
    assert "10K-100K" in prompt
    assert "99.99%" in prompt
    assert "10-100GB" in prompt
