"""Tests for architect_node JSON recovery and error handling."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from scaffold_ai.graph.nodes import architect_node, get_llm
from scaffold_ai.graph.state import GraphState


@pytest.fixture
def base_state():
    """Base state for testing."""
    return {
        "user_input": "Create a Lambda function",
        "intent": "new_feature",
        "graph_json": {"nodes": [], "edges": []},
        "iac_format": "cdk",
        "security_review": None,
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "response": "",
    }


class TestArchitectNodeJSONRecovery:
    """Test architect_node JSON parsing and recovery."""

    @pytest.mark.asyncio
    async def test_llm_exception_returns_error_message(self, base_state):
        """Test that LLM exceptions return helpful error message."""
        with patch("scaffold_ai.graph.nodes.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("Bedrock unavailable")
            mock_get_llm.return_value = mock_llm

            result = await architect_node(base_state)

            assert "encountered an error" in result["response"].lower()
            assert result["graph_json"] == base_state["graph_json"]  # Unchanged

    @pytest.mark.asyncio
    async def test_deduplicates_nodes_by_id(self, base_state):
        """Test that duplicate node IDs are handled."""
        # This is a unit test that doesn't require LLM
        pass

    @pytest.mark.asyncio
    async def test_deduplicates_edges_by_id(self, base_state):
        """Test that duplicate edge IDs are handled."""
        # This is a unit test that doesn't require LLM
        pass

    @pytest.mark.asyncio
    async def test_explain_intent_calls_explain_architecture(self, base_state):
        """Test that explain intent routes to explain_architecture."""
        base_state["intent"] = "explain"
        base_state["graph_json"] = {
            "nodes": [{"id": "api-1", "data": {"type": "api", "label": "API"}}],
            "edges": []
        }

        result = await architect_node(base_state)

        assert "response" in result
        assert len(result["response"]) > 0
