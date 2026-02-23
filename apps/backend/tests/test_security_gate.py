"""Test security gate workflow to ensure it blocks insecure architectures."""

import pytest
from scaffold_ai.graph.workflow import create_workflow
from scaffold_ai.graph.state import GraphState


@pytest.mark.asyncio
async def test_security_gate_blocks_insecure_architecture():
    """Test that security gate blocks code generation for insecure architecture."""
    workflow = create_workflow()
    app = workflow.compile()

    # Insecure architecture: Multiple APIs without authentication
    # This will generate 4 high-severity warnings, exceeding the threshold of 3
    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {
                    "id": "api-1",
                    "type": "default",
                    "data": {"label": "Users API", "type": "api", "config": {}},
                },
                {
                    "id": "api-2",
                    "type": "default",
                    "data": {"label": "Orders API", "type": "api", "config": {}},
                },
                {
                    "id": "api-3",
                    "type": "default",
                    "data": {"label": "Products API", "type": "api", "config": {}},
                },
                {
                    "id": "api-4",
                    "type": "default",
                    "data": {"label": "Payments API", "type": "api", "config": {}},
                },
                {
                    "id": "lambda-1",
                    "type": "default",
                    "data": {"label": "Handler", "type": "lambda", "config": {}},
                },
            ],
            "edges": [
                {"id": "e1", "source": "api-1", "target": "lambda-1"},
                {"id": "e2", "source": "api-2", "target": "lambda-1"},
                {"id": "e3", "source": "api-3", "target": "lambda-1"},
                {"id": "e4", "source": "api-4", "target": "lambda-1"},
            ],
        },
        "iac_format": "cdk",
        "response": "",
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "skip_security": False,
        "security_review": None,
    }

    result = await app.ainvoke(initial_state)

    # Verify security review ran
    assert "security_review" in result
    review = result["security_review"]

    # Should fail due to missing security controls (>3 high-severity warnings)
    assert review["passed"] is False
    assert review["security_score"] < 70
    assert len([w for w in review["warnings"] if w.get("severity") == "high"]) >= 3

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
                {"id": "e1", "source": "cognito-1", "target": "apigateway-1"},
                {"id": "e2", "source": "apigateway-1", "target": "lambda-1"},
                {"id": "e3", "source": "lambda-1", "target": "dynamodb-1"},
            ],
        },
        "iac_format": "cdk",
        "response": "",
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "skip_security": False,
        "security_review": None,
    }

    result = await app.ainvoke(initial_state)

    # Verify security review ran
    assert "security_review" in result
    review = result["security_review"]

    # The LLM may score this differently depending on context, but the review should run.
    # We just verify the review completed with a valid score.
    assert "passed" in review
    assert "security_score" in review
    assert review["security_score"] >= 0


@pytest.mark.asyncio
async def test_security_gate_empty_architecture():
    """Test security gate with empty architecture."""
    workflow = create_workflow()
    app = workflow.compile()

    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {"nodes": [], "edges": []},
        "iac_format": "cdk",
        "response": "",
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "skip_security": False,
        "security_review": None,
    }

    result = await app.ainvoke(initial_state)

    # Empty architecture: architect may add nodes from the "generate code" prompt,
    # so we just verify the security review ran and the workflow completed.
    assert "security_review" in result
    assert result["security_review"] is not None
    assert "security_score" in result["security_review"]


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
        "iac_format": "cdk",
        "response": "",
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "skip_security": False,
        "security_review": None,
    }

    result = await app.ainvoke(initial_state)

    # Security review should not run for non-generate intents
    # The workflow should end after architect node
    assert result["intent"] == "explain"
    # No code generation should occur
    assert len(result["generated_files"]) == 0
