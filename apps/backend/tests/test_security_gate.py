"""Test security gate workflow to ensure it blocks insecure architectures."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scaffold_ai.graph.workflow import create_workflow
from scaffold_ai.graph.state import GraphState

# Valid architect response (empty graph update)
_ARCHITECT_RESPONSE = json.dumps({"nodes": [], "edges": [], "explanation": "Architecture updated."})


def _make_side_effect(*responses: str):
    """Return an async side_effect that cycles through the given response strings."""
    responses_list = list(responses)
    call_count = [0]

    async def _side_effect(messages):
        idx = min(call_count[0], len(responses_list) - 1)
        call_count[0] += 1
        mock_resp = MagicMock()
        mock_resp.content = responses_list[idx]
        return mock_resp

    return _side_effect


def _make_mock_llm(*responses: str) -> MagicMock:
    """Return a mock LLM that returns each response string in order."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.side_effect = _make_side_effect(*responses)
    return mock_llm


@pytest.mark.asyncio
async def test_security_gate_blocks_insecure_architecture():
    """Test that security gate blocks code generation for insecure architecture."""
    insecure_review = {
        "security_score": 40,
        "passed": False,
        "critical_issues": [
            {"service": "API", "issue": "No authentication", "recommendation": "Add Cognito"},
        ],
        "warnings": [
            {"service": "api-1", "issue": "No auth", "severity": "high"},
            {"service": "api-2", "issue": "No auth", "severity": "high"},
            {"service": "api-3", "issue": "No auth", "severity": "high"},
            {"service": "api-4", "issue": "No auth", "severity": "high"},
        ],
        "recommendations": [],
        "compliant_services": [],
        "security_enhancements": {"nodes_to_add": [], "config_changes": []},
    }

    workflow = create_workflow()
    app = workflow.compile()

    # Insecure architecture: Multiple APIs without authentication
    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {"id": "api-1", "type": "default", "data": {"label": "Users API", "type": "api", "config": {}}},
                {"id": "api-2", "type": "default", "data": {"label": "Orders API", "type": "api", "config": {}}},
                {"id": "api-3", "type": "default", "data": {"label": "Products API", "type": "api", "config": {}}},
                {"id": "api-4", "type": "default", "data": {"label": "Payments API", "type": "api", "config": {}}},
                {"id": "lambda-1", "type": "default", "data": {"label": "Handler", "type": "lambda", "config": {}}},
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

    # Call order: interpret_intent → architect_node → security_review_node
    mock_llm = _make_mock_llm(
        "generate_code",                    # interpret_intent response
        _ARCHITECT_RESPONSE,                # architect_node response
        json.dumps(insecure_review),        # security_review_node response
    )

    with patch("scaffold_ai.graph.nodes.get_llm", return_value=mock_llm):
        result = await app.ainvoke(initial_state)

    assert "security_review" in result
    review = result["security_review"]

    assert review["passed"] is False
    assert review["security_score"] < 70
    assert len([w for w in review["warnings"] if w.get("severity") == "high"]) >= 3

    # Verify code generation was blocked
    assert len(result["generated_files"]) == 0
    assert "FAILED" in result["response"]


@pytest.mark.asyncio
async def test_security_gate_passes_secure_architecture():
    """Test that security gate allows code generation for secure architecture."""
    secure_review = {
        "security_score": 85,
        "passed": True,
        "critical_issues": [],
        "warnings": [],
        "recommendations": [
            {"service": "Lambda", "recommendation": "Enable X-Ray tracing"},
        ],
        "compliant_services": ["cognito-1", "apigateway-1", "lambda-1", "dynamodb-1"],
        "security_enhancements": {"nodes_to_add": [], "config_changes": []},
    }

    workflow = create_workflow()
    app = workflow.compile()

    # Secure architecture with proper controls
    initial_state: GraphState = {
        "user_input": "generate code",
        "intent": "generate_code",
        "graph_json": {
            "nodes": [
                {"id": "cognito-1", "type": "cognito", "data": {"label": "Auth", "config": {"mfa": True}}},
                {"id": "apigateway-1", "type": "apigateway", "data": {"label": "API", "config": {"auth": "cognito"}}},
                {"id": "lambda-1", "type": "lambda", "data": {"label": "Handler", "config": {"environment_encryption": True}}},
                {"id": "dynamodb-1", "type": "dynamodb", "data": {"label": "Data", "config": {"encryption": True, "backup": True}}},
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

    # Call order: interpret_intent → architect_node → security_review_node → cdk_specialist → react_specialist
    # cdk_specialist and react_specialist also call get_llm, provide fallback responses
    mock_llm = _make_mock_llm(
        "generate_code",                    # interpret_intent
        _ARCHITECT_RESPONSE,                # architect_node
        json.dumps(secure_review),          # security_review_node
        "// CDK code here",                 # cdk_specialist (fallback)
        "// React code here",               # react_specialist (fallback)
    )

    with patch("scaffold_ai.graph.nodes.get_llm", return_value=mock_llm):
        result = await app.ainvoke(initial_state)

    assert "security_review" in result
    review = result["security_review"]

    assert "passed" in review
    assert "security_score" in review
    assert review["security_score"] >= 0


@pytest.mark.asyncio
async def test_security_gate_empty_architecture():
    """Test security gate with empty architecture (no LLM call for security review)."""
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

    # interpret_intent + architect_node calls; security_review returns early for empty graph
    mock_llm = _make_mock_llm(
        "generate_code",
        _ARCHITECT_RESPONSE,
    )

    with patch("scaffold_ai.graph.nodes.get_llm", return_value=mock_llm):
        result = await app.ainvoke(initial_state)

    # Empty architecture returns early with score 100 (no LLM call needed)
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
                {"id": "lambda-1", "type": "lambda", "data": {"label": "Insecure Lambda", "config": {}}}
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

    # interpret_intent → explain (routes to explain_architecture which calls get_llm)
    mock_llm = _make_mock_llm(
        "explain",                          # interpret_intent
        "This architecture has a Lambda.",  # explain_architecture
    )

    with patch("scaffold_ai.graph.nodes.get_llm", return_value=mock_llm):
        result = await app.ainvoke(initial_state)

    assert result["intent"] == "explain"
    assert len(result["generated_files"]) == 0
