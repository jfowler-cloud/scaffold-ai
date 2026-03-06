"""Shared pytest fixtures for scaffold-ai function tests."""
import os
import sys
from unittest.mock import MagicMock, patch

os.environ.setdefault("DEPLOYMENT_TIER", "testing")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
os.environ.setdefault("SCAFFOLD_SESSIONS_TABLE", "scaffold-ai-sessions")
os.environ.setdefault("SCAFFOLD_EXECUTIONS_TABLE", "scaffold-ai-executions")

# Add shared config to path
_base = os.path.dirname(__file__)
_shared = os.path.abspath(os.path.join(_base, "..", "..", "agents", "shared"))
sys.path.insert(0, _shared)

import pytest  # noqa: E402

_mock_boto3_client = MagicMock()
_mock_boto3_resource = MagicMock()
patch("boto3.client", return_value=_mock_boto3_client).start()
patch("boto3.resource", return_value=_mock_boto3_resource).start()

_FUNCTION_DIRS = [
    os.path.abspath(os.path.join(_base, "..", d))
    for d in ("interpret", "architect", "security_review", "cdk_specialist", "react_specialist", "get_execution")
]
_HANDLER_MODULES = ("handler", "config", "db")


@pytest.fixture(autouse=True)
def _isolate_handler_module():
    for mod in _HANDLER_MODULES:
        sys.modules.pop(mod, None)
    for d in _FUNCTION_DIRS:
        while d in sys.path:
            sys.path.remove(d)
    yield
    for mod in _HANDLER_MODULES:
        sys.modules.pop(mod, None)
