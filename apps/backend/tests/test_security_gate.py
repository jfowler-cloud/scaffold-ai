"""Test security gate workflow to ensure it blocks insecure architectures."""

import pytest
from scaffold_ai.graph.workflow import create_workflow
from scaffold_ai.graph.state import GraphState


@pytest.mark.asyncio
async def test_security_gate_blocks_insecure_architecture():
    """Test that security gate blocks code generation for insecure architecture."""
    workflow = create_workflow()
    app = workflow.compile()

    # Insecure architecture: Lambda without encryption, DynamoDB without backup
    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {
                    "id": "lambda-1",
                    "type": "lambda",
                    "data": {"label": "API Handler", "config": {}},
                },
                {
                    "id": "dynamodb-1",
                    "type": "dynamodb",
                    "data": {"label": "Users Table", "config": {}},
                },
            ],
            "edges": [{"source": "lambda-1", "target": "dynamodb-1"}],
        },
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    # Verify security review ran
    assert "security_review" in result
    review = result["security_review"]

    # Should fail due to missing security controls
    assert review["passed"] is False
    assert review["security_score"] < 70
    assert len(review["critical_issues"]) > 0

    # Verify code generation was blocked
    assert len(result["generated_files"]) == 0
    assert "FAILED" in result["response"]


@pytest.mark.asyncio
async def test_security_gate_passes_secure_architecture():
    """Test that security gate allows code generation for secure architecture."""
    workflow = create_workflow()
    app = workflow.compile()

    # Secure architecture with proper controls
    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {
                    "id": "cognito-1",
                    "type": "cognito",
                    "data": {"label": "Auth", "config": {"mfa": True}},
                },
                {
                    "id": "apigateway-1",
                    "type": "apigateway",
                    "data": {"label": "API", "config": {"auth": "cognito"}},
                },
                {
                    "id": "lambda-1",
                    "type": "lambda",
                    "data": {
                        "label": "Handler",
                        "config": {"environment_encryption": True},
                    },
                },
                {
                    "id": "dynamodb-1",
                    "type": "dynamodb",
                    "data": {
                        "label": "Data",
                        "config": {"encryption": True, "backup": True},
                    },
                },
            ],
            "edges": [
                {"source": "cognito-1", "target": "apigateway-1"},
                {"source": "apigateway-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "dynamodb-1"},
            ],
        },
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    # Verify security review ran
    assert "security_review" in result
    review = result["security_review"]

    # Should pass with good score
    assert review["passed"] is True
    assert review["security_score"] >= 70

    # Verify code generation proceeded
    assert len(result["generated_files"]) > 0
    assert "PASSED" in result["response"]


@pytest.mark.asyncio
async def test_security_gate_empty_architecture():
    """Test security gate with empty architecture."""
    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {"nodes": [], "edges": []},
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    # Empty architecture should pass (nothing to review)
    assert "security_review" in result
    assert result["security_review"]["passed"] is True
    assert result["security_review"]["security_score"] == 100


@pytest.mark.asyncio
async def test_workflow_skips_security_for_non_generate_intent():
    """Test that security gate is skipped when intent is not generate_code."""
    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "explain my architecture",
        "intent": "explain",
        "graph_json": {
            "nodes": [
                {
                    "id": "lambda-1",
                    "type": "lambda",
                    "data": {"label": "Insecure Lambda", "config": {}},
                }
            ],
            "edges": [],
        },
        "response": "",
        "generated_files": [],
    }

    result = await app.ainvoke(initial_state)

    # Security review should not run for non-generate intents
    # The workflow should end after architect node
    assert result["intent"] == "explain"
    # No code generation should occur
    assert len(result["generated_files"]) == 0
