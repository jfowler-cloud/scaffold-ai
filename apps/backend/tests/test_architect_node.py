"""Tests for architect_node JSON recovery and error handling."""

import pytest
from unittest.mock import AsyncMock, patch
from scaffold_ai.graph.nodes import architect_node
from scaffold_ai.graph.state import GraphState


class MockLLMResponse:
    """Mock LLM response object."""
    def __init__(self, content: str):
        self.content = content


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
    async def test_clean_json_response(self, base_state):
        """Test parsing clean JSON response."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "lambda-1", "data": {"type": "lambda", "label": "Handler"}}
                ],
                "edges": [],
                "explanation": "Created a Lambda function"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["nodes"]) == 1
            assert result["graph_json"]["nodes"][0]["data"]["type"] == "lambda"
            assert "lambda" in result["response"].lower() or "function" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_json_with_markdown_fences(self, base_state):
        """Test parsing JSON wrapped in ```json markdown fences."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''```json
{
    "nodes": [
        {"id": "api-1", "data": {"type": "api", "label": "REST API"}}
    ],
    "edges": [],
    "explanation": "Created an API"
}
```''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["nodes"]) == 1
            assert result["graph_json"]["nodes"][0]["data"]["type"] == "api"
            assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_json_with_plain_markdown_fences(self, base_state):
        """Test parsing JSON wrapped in ``` markdown fences (no language)."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''```
{
    "nodes": [
        {"id": "db-1", "data": {"type": "database", "label": "DynamoDB"}}
    ],
    "edges": [],
    "explanation": "Created a database"
}
```''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["nodes"]) == 1
            assert result["graph_json"]["nodes"][0]["data"]["type"] == "database"

    @pytest.mark.asyncio
    async def test_malformed_json_returns_error_message(self, base_state):
        """Test that malformed JSON returns helpful error message."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "lambda-1", "data": {"type": "lambda"
                ]
            }''')  # Missing closing braces
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert "trouble generating" in result["response"].lower()
            assert result["graph_json"] == base_state["graph_json"]  # Unchanged

    @pytest.mark.asyncio
    async def test_llm_exception_returns_error_message(self, base_state):
        """Test that LLM exceptions return helpful error message."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("Bedrock unavailable")
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert "encountered an error" in result["response"].lower()
            assert result["graph_json"] == base_state["graph_json"]  # Unchanged

    @pytest.mark.asyncio
    async def test_preserves_existing_nodes(self, base_state):
        """Test that existing nodes are preserved when adding new ones."""
        base_state["graph_json"] = {
            "nodes": [
                {"id": "existing-1", "type": "default", "position": {"x": 0, "y": 0},
                 "data": {"type": "api", "label": "Existing API"}}
            ],
            "edges": []
        }

        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "new-1", "data": {"type": "lambda", "label": "New Lambda"}}
                ],
                "edges": [],
                "explanation": "Added Lambda"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["nodes"]) == 2
            node_ids = {n["id"] for n in result["graph_json"]["nodes"]}
            assert "existing-1" in node_ids
            assert "new-1" in node_ids

    @pytest.mark.asyncio
    async def test_deduplicates_nodes_by_id(self, base_state):
        """Test that duplicate node IDs are not added."""
        base_state["graph_json"] = {
            "nodes": [
                {"id": "lambda-1", "type": "default", "position": {"x": 0, "y": 0},
                 "data": {"type": "lambda", "label": "Existing"}}
            ],
            "edges": []
        }

        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "lambda-1", "data": {"type": "lambda", "label": "Duplicate"}}
                ],
                "edges": [],
                "explanation": "Tried to add duplicate"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["nodes"]) == 1
            assert result["graph_json"]["nodes"][0]["data"]["label"] == "Existing"

    @pytest.mark.asyncio
    async def test_creates_edges_with_generated_ids(self, base_state):
        """Test that edges are created with proper IDs."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "api-1", "data": {"type": "api", "label": "API"}},
                    {"id": "lambda-1", "data": {"type": "lambda", "label": "Handler"}}
                ],
                "edges": [
                    {"source": "api-1", "target": "lambda-1", "label": "invokes"}
                ],
                "explanation": "Connected API to Lambda"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["edges"]) == 1
            edge = result["graph_json"]["edges"][0]
            assert edge["id"] == "e-api-1-lambda-1"
            assert edge["source"] == "api-1"
            assert edge["target"] == "lambda-1"
            assert edge["label"] == "invokes"

    @pytest.mark.asyncio
    async def test_deduplicates_edges_by_id(self, base_state):
        """Test that duplicate edges are not added."""
        base_state["graph_json"] = {
            "nodes": [
                {"id": "api-1", "type": "default", "position": {"x": 0, "y": 0},
                 "data": {"type": "api", "label": "API"}},
                {"id": "lambda-1", "type": "default", "position": {"x": 100, "y": 0},
                 "data": {"type": "lambda", "label": "Handler"}}
            ],
            "edges": [
                {"id": "e-api-1-lambda-1", "source": "api-1", "target": "lambda-1"}
            ]
        }

        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [],
                "edges": [
                    {"source": "api-1", "target": "lambda-1", "label": "duplicate"}
                ],
                "explanation": "Tried to add duplicate edge"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            assert len(result["graph_json"]["edges"]) == 1

    @pytest.mark.asyncio
    async def test_explain_intent_calls_explain_architecture(self, base_state):
        """Test that explain intent routes to explain_architecture."""
        base_state["intent"] = "explain"
        base_state["graph_json"] = {"nodes": [], "edges": []}

        result = await architect_node(base_state)

        assert "empty" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_positions_new_nodes(self, base_state):
        """Test that new nodes get position coordinates."""
        with patch("langchain_aws.ChatBedrock") as mock_bedrock:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MockLLMResponse('''{
                "nodes": [
                    {"id": "lambda-1", "data": {"type": "lambda", "label": "Handler"}}
                ],
                "edges": [],
                "explanation": "Created Lambda"
            }''')
            mock_bedrock.return_value = mock_llm

            result = await architect_node(base_state)

            node = result["graph_json"]["nodes"][0]
            assert "position" in node
            assert "x" in node["position"]
            assert "y" in node["position"]
            assert isinstance(node["position"]["x"], (int, float))
            assert isinstance(node["position"]["y"], (int, float))
