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


def test_get_execution_failed_status():
    """Cover FAILED/TIMED_OUT/ABORTED branch (lines 38-39)."""
    _set_path()
    mock_sfn = MagicMock()
    mock_sfn.describe_execution.return_value = {
        "status": "FAILED",
        "cause": "Something went wrong",
    }
    with patch("handler.sfn", mock_sfn):
        from handler import handler

        result = handler({"executionArn": "arn:aws:states:us-east-1:123:execution:fail"}, None)

    assert result["statusCode"] == 200
    import json

    body = json.loads(result["body"])
    assert body["status"] == "FAILED"
    assert body["error"] == "Something went wrong"


def test_get_execution_timed_out_no_cause():
    """Cover TIMED_OUT with missing cause — falls back to default message."""
    _set_path()
    mock_sfn = MagicMock()
    mock_sfn.describe_execution.return_value = {
        "status": "TIMED_OUT",
    }
    with patch("handler.sfn", mock_sfn):
        from handler import handler

        result = handler({"executionArn": "arn:aws:states:us-east-1:123:execution:timeout"}, None)

    import json

    body = json.loads(result["body"])
    assert body["status"] == "TIMED_OUT"
    assert body["error"] == "Execution failed"


def test_get_execution_exception():
    """Cover exception handler branch (lines 42-44)."""
    _set_path()
    mock_sfn = MagicMock()
    mock_sfn.describe_execution.side_effect = Exception("SFN blew up")
    with patch("handler.sfn", mock_sfn):
        from handler import handler

        result = handler({"executionArn": "arn:aws:states:us-east-1:123:execution:err"}, None)

    assert result["statusCode"] == 500
    import json

    body = json.loads(result["body"])
    assert "SFN blew up" in body["error"]


def test_get_execution_arn_from_path_parameters():
    """Cover executionArn from pathParameters fallback (line 23)."""
    _set_path()
    mock_sfn = MagicMock()
    mock_sfn.describe_execution.return_value = {
        "status": "RUNNING",
    }
    with patch("handler.sfn", mock_sfn):
        from handler import handler

        result = handler({"pathParameters": {"executionArn": "arn:aws:states:us-east-1:123:execution:path"}}, None)

    assert result["statusCode"] == 200
    import json

    body = json.loads(result["body"])
    assert body["status"] == "RUNNING"
