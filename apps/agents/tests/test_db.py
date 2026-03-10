"""Tests for shared/db.py DynamoDB helpers."""
import os
import sys

import boto3
import pytest
from moto import mock_aws

# shared/db.py does `from config import app_config` (bare import),
# so the shared/ directory must be on sys.path for that to resolve.
_shared_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shared")
if _shared_dir not in sys.path:
    sys.path.insert(0, _shared_dir)

# Set dummy AWS credentials so boto3 doesn't try SSO/CRT at import time
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from shared.config import app_config  # noqa: E402

TABLE_NAME = app_config.scaffold_executions_table


@pytest.fixture
def dynamodb_env():
    """Provide a moto DynamoDB environment and reimport shared.db so it binds to moto."""
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="us-east-1")
        ddb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "executionId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "executionId", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        # Force reimport of shared.db so module-level boto3.resource uses moto
        sys.modules.pop("shared.db", None)
        sys.modules.pop("db", None)
        import shared.db as db_mod

        db_mod.dynamodb = ddb
        yield db_mod, ddb.Table(TABLE_NAME)


class TestGetTable:
    def test_returns_table_object(self, dynamodb_env):
        db_mod, table = dynamodb_env
        result = db_mod.get_table(TABLE_NAME)
        assert result.table_name == TABLE_NAME


class TestGetExecution:
    def test_returns_item_when_exists(self, dynamodb_env):
        db_mod, table = dynamodb_env
        table.put_item(Item={"executionId": "exec-1", "status": "RUNNING"})
        result = db_mod.get_execution("exec-1")
        assert result is not None
        assert result["executionId"] == "exec-1"
        assert result["status"] == "RUNNING"

    def test_returns_none_when_not_found(self, dynamodb_env):
        db_mod, table = dynamodb_env
        result = db_mod.get_execution("nonexistent")
        assert result is None


class TestPutItem:
    def test_puts_and_retrieves_item(self, dynamodb_env):
        db_mod, table = dynamodb_env
        db_mod.put_item(TABLE_NAME, {"executionId": "exec-2", "data": "hello"})
        resp = table.get_item(Key={"executionId": "exec-2"})
        assert resp["Item"]["data"] == "hello"


class TestUpdateItem:
    def test_updates_single_field(self, dynamodb_env):
        db_mod, table = dynamodb_env
        table.put_item(Item={"executionId": "exec-3", "status": "RUNNING"})
        result = db_mod.update_item(
            TABLE_NAME,
            {"executionId": "exec-3"},
            {"status": "SUCCEEDED"},
        )
        assert result["status"] == "SUCCEEDED"
        assert result["executionId"] == "exec-3"

    def test_updates_multiple_fields(self, dynamodb_env):
        db_mod, table = dynamodb_env
        table.put_item(
            Item={"executionId": "exec-4", "status": "RUNNING", "output": ""}
        )
        result = db_mod.update_item(
            TABLE_NAME,
            {"executionId": "exec-4"},
            {"status": "SUCCEEDED", "output": "done"},
        )
        assert result["status"] == "SUCCEEDED"
        assert result["output"] == "done"

    def test_adds_new_field_via_update(self, dynamodb_env):
        db_mod, table = dynamodb_env
        table.put_item(Item={"executionId": "exec-5"})
        result = db_mod.update_item(
            TABLE_NAME,
            {"executionId": "exec-5"},
            {"newField": "value"},
        )
        assert result["newField"] == "value"
