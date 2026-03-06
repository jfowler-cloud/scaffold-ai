"""Tests for the Step Functions Lambda handlers — replaces test_security_gate.py and test_units.py."""
import json
import sys
import os
from unittest.mock import patch, MagicMock
import pytest

# Add functions to path for direct import
FUNCTIONS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "functions")


def _mock_strands(response: str):
    """Return a mock Strands Agent that returns the given string."""
    mock_agent = MagicMock()
    mock_agent.return_value = response
    mock_agent.__str__ = lambda self: response
    return mock_agent


# ── interpret handler ──────────────────────────────────────────────────────────

class TestInterpretHandler:
    def _run(self, user_input: str, agent_response: str = "new_feature") -> dict:
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "interpret"))
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "shared"))
        import importlib
        import handler as h
        importlib.reload(h)

        mock_agent_instance = MagicMock()
        mock_agent_instance.return_value = agent_response
        mock_agent_instance.__call__ = lambda self, x: agent_response

        with patch("handler.Agent") as MockAgent, \
             patch("handler.BedrockModel"), \
             patch("handler.app_config"):
            MockAgent.return_value = mock_agent_instance
            return h.handler({"user_input": user_input, "graph_json": {}, "iac_format": "cdk"})

    def test_keyword_fallback_generate_code(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "interpret"))
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "shared"))
        import handler as h
        assert h._keyword_classify("generate the CDK code") == "generate_code"

    def test_keyword_fallback_modify_graph(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "interpret"))
        import handler as h
        assert h._keyword_classify("remove the database") == "modify_graph"

    def test_keyword_fallback_explain(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "interpret"))
        import handler as h
        assert h._keyword_classify("what does this do?") == "explain"

    def test_keyword_fallback_default_new_feature(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "interpret"))
        import handler as h
        assert h._keyword_classify("xyzzy frobble") == "new_feature"


# ── security_review handler ────────────────────────────────────────────────────

class TestSecurityReviewHandler:
    def _load(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "security_review"))
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "shared"))
        import importlib
        import handler as h
        importlib.reload(h)
        return h

    def test_empty_graph_passes(self):
        h = self._load()
        with patch("handler.app_config"):
            result = h.handler({"graph_json": {"nodes": [], "edges": []}, "skip_security": False})
        assert result["security_review"]["passed"] is True

    def test_skip_security_bypasses_llm(self):
        h = self._load()
        with patch("handler.app_config"), patch("handler.Agent") as MockAgent:
            result = h.handler({
                "graph_json": {"nodes": [{"id": "api-1", "data": {"type": "api"}}]},
                "skip_security": True,
            })
        MockAgent.assert_not_called()
        assert result["security_review"]["passed"] is True

    def test_failed_review_blocks_code_gen(self):
        h = self._load()
        failed_review = json.dumps({
            "security_score": 30, "passed": False,
            "critical_issues": [{"service": "API", "issue": "No auth", "severity": "critical", "recommendation": "Add Cognito"}],
            "warnings": [], "recommendations": [], "compliant_services": [],
            "security_enhancements": {"nodes_to_add": [], "config_changes": []},
        })
        mock_agent = MagicMock()
        mock_agent.return_value = failed_review

        with patch("handler.Agent", return_value=mock_agent), \
             patch("handler.BedrockModel"), \
             patch("handler.app_config"):
            result = h.handler({
                "graph_json": {"nodes": [{"id": "api-1", "data": {"type": "api"}}]},
                "skip_security": False,
            })
        assert result["security_review"]["passed"] is False
        assert "FAILED" in result["response"]

    def test_passed_review_allows_code_gen(self):
        h = self._load()
        passed_review = json.dumps({
            "security_score": 90, "passed": True,
            "critical_issues": [], "warnings": [], "recommendations": [],
            "compliant_services": ["api-1"],
            "security_enhancements": {"nodes_to_add": [], "config_changes": []},
        })
        mock_agent = MagicMock()
        mock_agent.return_value = passed_review

        with patch("handler.Agent", return_value=mock_agent), \
             patch("handler.BedrockModel"), \
             patch("handler.app_config"):
            result = h.handler({
                "graph_json": {"nodes": [{"id": "api-1", "data": {"type": "api"}}]},
                "skip_security": False,
            })
        assert result["security_review"]["passed"] is True
        assert "PASSED" in result["response"]


# ── architect handler ──────────────────────────────────────────────────────────

class TestArchitectHandler:
    def _load(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "architect"))
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "shared"))
        import importlib
        import handler as h
        importlib.reload(h)
        return h

    def test_position_nodes_empty_existing(self):
        h = self._load()
        nodes = [{"id": "fn-1", "type": "lambda", "label": "Handler", "description": ""}]
        result = h._position_nodes(nodes, [])
        assert len(result) == 1
        assert "position" in result[0]

    def test_explain_empty_graph(self):
        h = self._load()
        with patch("handler.app_config"):
            result = h._explain({"graph_json": {"nodes": [], "edges": []}, "user_input": "explain"})
        assert "empty" in result["response"].lower()

    def test_json_parse_error_returns_friendly_message(self):
        h = self._load()
        mock_agent = MagicMock()
        mock_agent.return_value = "not valid json at all"

        with patch("handler.Agent", return_value=mock_agent), \
             patch("handler.BedrockModel"), \
             patch("handler.app_config"):
            result = h.handler({
                "user_input": "add a database",
                "graph_json": {"nodes": [], "edges": []},
                "intent": "new_feature",
            })
        assert "trouble" in result["response"].lower() or "error" in result["response"].lower()


# ── get_execution handler ──────────────────────────────────────────────────────

class TestGetExecutionHandler:
    def _load(self):
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "get_execution"))
        sys.path.insert(0, os.path.join(FUNCTIONS_ROOT, "shared"))
        import importlib
        import handler as h
        importlib.reload(h)
        return h

    def test_missing_arn_returns_400(self):
        h = self._load()
        with patch("handler.sfn"), patch("handler.app_config"):
            result = h.handler({})
        assert result["statusCode"] == 400

    def test_running_status(self):
        h = self._load()
        mock_sfn = MagicMock()
        mock_sfn.describe_execution.return_value = {"status": "RUNNING"}
        with patch("handler.sfn", mock_sfn), patch("handler.app_config"):
            result = h.handler({"executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"})
        body = json.loads(result["body"])
        assert body["status"] == "RUNNING"

    def test_succeeded_status_returns_output(self):
        h = self._load()
        output = {"response": "Done", "graph_json": {"nodes": []}, "generated_files": []}
        mock_sfn = MagicMock()
        mock_sfn.describe_execution.return_value = {"status": "SUCCEEDED", "output": json.dumps(output)}
        with patch("handler.sfn", mock_sfn), patch("handler.app_config"):
            result = h.handler({"executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"})
        body = json.loads(result["body"])
        assert body["status"] == "SUCCEEDED"
        assert body["message"] == "Done"

    def test_failed_status_returns_error(self):
        h = self._load()
        mock_sfn = MagicMock()
        mock_sfn.describe_execution.return_value = {"status": "FAILED", "cause": "Lambda error"}
        with patch("handler.sfn", mock_sfn), patch("handler.app_config"):
            result = h.handler({"executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"})
        body = json.loads(result["body"])
        assert body["status"] == "FAILED"
        assert "Lambda error" in body["error"]
