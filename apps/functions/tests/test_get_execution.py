"""Tests for get_execution Lambda handler."""
import sys
import os
from unittest.mock import MagicMock, patch

_HANDLER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "get_execution"))


def _set_path():
    sys.path.insert(0, _HANDLER_DIR)


def test_get_execution_success():
    _set_path()
    mock_sfn = MagicMock()
    mock_sfn.describe_execution.return_value = {
        "status": "SUCCEEDED",
        "output": '{"result": "ok"}',
    }
    with patch("handler.sfn", mock_sfn):
        from handler import handler

        result = handler({"executionArn": "arn:aws:states:us-east-1:123:execution:test"}, None)

    assert result["statusCode"] == 200
    import json
    body = json.loads(result["body"])
    assert body["status"] == "SUCCEEDED"


def test_get_execution_missing_arn():
    _set_path()
    from handler import handler

    result = handler({}, None)
    assert result.get("error") or result.get("statusCode", 200) >= 400
