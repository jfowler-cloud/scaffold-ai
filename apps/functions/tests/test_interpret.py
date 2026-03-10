"""Tests for interpret Lambda handler."""
import sys
import os
from unittest.mock import MagicMock, patch

_HANDLER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "interpret"))


def _set_path():
    sys.path.insert(0, _HANDLER_DIR)


def test_keyword_classify_generate_code():
    _set_path()
    from handler import _keyword_classify

    assert _keyword_classify("generate the CDK code") == "generate_code"


def test_keyword_classify_new_feature():
    _set_path()
    from handler import _keyword_classify

    assert _keyword_classify("add a database") == "new_feature"


def test_handler_returns_intent():
    _set_path()
    mock_agent = MagicMock()
    mock_agent.return_value = "new_feature"
    mock_agent.__call__ = lambda self, x: "new_feature"

    with patch("handler.Agent") as MockAgent, patch("handler.BedrockModel"), patch("handler.app_config"):
        MockAgent.return_value = mock_agent
        from handler import handler

        result = handler({"user_input": "add a queue", "graph_json": {}, "iac_format": "cdk"})

    assert "intent" in result


def test_handler_falls_back_to_keyword_on_exception():
    """Cover LLM exception fallback branch (lines 56-58)."""
    _set_path()

    with patch("handler.BedrockModel", side_effect=Exception("Bedrock unavailable")), patch(
        "handler.app_config"
    ) as mock_config:
        mock_config.model_id = "some-model"
        from handler import handler

        result = handler({"user_input": "generate the CDK code", "graph_json": {}, "iac_format": "cdk"})

    assert result["intent"] == "generate_code"


def test_keyword_classify_explain():
    _set_path()
    from handler import _keyword_classify

    assert _keyword_classify("what is this service?") == "explain"


def test_keyword_classify_modify_graph():
    _set_path()
    from handler import _keyword_classify

    assert _keyword_classify("remove the database") == "modify_graph"
