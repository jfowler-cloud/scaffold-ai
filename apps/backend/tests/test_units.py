"""
Unit tests for pure / offline-safe functions.

These tests do NOT require AWS credentials or a running Bedrock endpoint.
LLM-dependent node functions are tested via keyword-fallback paths only.
"""

import pytest
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# generate_node_positions
# ---------------------------------------------------------------------------

from scaffold_ai.graph.nodes import generate_node_positions


def _make_node(node_id: str, node_type: str) -> dict:
    return {"id": node_id, "type": node_type, "label": node_type.capitalize()}


class TestGenerateNodePositions:
    def test_empty_input(self):
        result = generate_node_positions([], [])
        assert result == []

    def test_single_node_has_position(self):
        nodes = [_make_node("n1", "lambda")]
        result = generate_node_positions(nodes, [])
        assert len(result) == 1
        assert "position" in result[0]
        assert "x" in result[0]["position"]
        assert "y" in result[0]["position"]

    def test_node_type_preserved_in_data(self):
        nodes = [_make_node("n1", "database")]
        result = generate_node_positions(nodes, [])
        assert result[0]["data"]["type"] == "database"
        assert result[0]["type"] == "database"

    def test_column_ordering_frontend_before_lambda(self):
        nodes = [_make_node("a", "lambda"), _make_node("b", "frontend")]
        result = generate_node_positions(nodes, [])
        pos = {r["id"]: r["position"]["x"] for r in result}
        # frontend column (0) should be left of lambda column (3)
        assert pos["b"] < pos["a"]

    def test_column_ordering_database_after_lambda(self):
        nodes = [_make_node("a", "lambda"), _make_node("b", "database")]
        result = generate_node_positions(nodes, [])
        pos = {r["id"]: r["position"]["x"] for r in result}
        assert pos["b"] > pos["a"]

    def test_same_type_stacks_vertically(self):
        nodes = [_make_node("n1", "lambda"), _make_node("n2", "lambda")]
        result = generate_node_positions(nodes, [])
        pos = {r["id"]: r["position"] for r in result}
        # Same column (same x), different row (different y)
        assert pos["n1"]["x"] == pos["n2"]["x"]
        assert pos["n1"]["y"] != pos["n2"]["y"]

    def test_existing_nodes_offset_row_count(self):
        existing = [
            {
                "id": "old",
                "type": "lambda",
                "position": {"x": 0, "y": 0},
                "data": {"label": "Old", "type": "lambda"},
            }
        ]
        new_nodes = [_make_node("new", "lambda")]
        result = generate_node_positions(new_nodes, existing)
        # New lambda should be in row 1 (below the existing one)
        assert result[0]["position"]["y"] > existing[0]["position"]["y"]

    def test_unknown_type_defaults_to_api_column(self):
        nodes = [_make_node("n1", "unknown_type")]
        result = generate_node_positions(nodes, [])
        # Should not raise; defaults to column 2 (api column)
        assert len(result) == 1

    def test_all_twelve_node_types_produce_positions(self):
        all_types = [
            "frontend", "cdn", "auth", "api", "lambda", "workflow",
            "queue", "events", "notification", "stream", "database", "storage",
        ]
        nodes = [_make_node(f"n{i}", t) for i, t in enumerate(all_types)]
        result = generate_node_positions(nodes, [])
        assert len(result) == 12
        for r in result:
            assert "position" in r


# ---------------------------------------------------------------------------
# security_gate router
# ---------------------------------------------------------------------------

from scaffold_ai.graph.nodes import security_gate


def _make_state(passed: bool, score: int = 80) -> dict:
    return {
        "security_review": {"passed": passed, "security_score": score},
        "user_input": "",
        "intent": "generate_code",
        "graph_json": {},
        "iac_format": "cdk",
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "response": "",
    }


class TestSecurityGate:
    def test_passed_review_returns_passed(self):
        assert security_gate(_make_state(passed=True)) == "passed"

    def test_failed_review_returns_failed(self):
        assert security_gate(_make_state(passed=False)) == "failed"

    def test_missing_review_returns_failed(self):
        state = _make_state(passed=True)
        state["security_review"] = None
        assert security_gate(state) == "failed"

    def test_empty_review_dict_returns_failed(self):
        state = _make_state(passed=True)
        state["security_review"] = {}
        assert security_gate(state) == "failed"


# ---------------------------------------------------------------------------
# should_generate_code router
# ---------------------------------------------------------------------------

from scaffold_ai.graph.nodes import should_generate_code


class TestShouldGenerateCode:
    def test_generate_code_intent(self):
        state = _make_state(passed=True)
        state["intent"] = "generate_code"
        assert should_generate_code(state) == "generate"

    def test_new_feature_intent(self):
        state = _make_state(passed=True)
        state["intent"] = "new_feature"
        assert should_generate_code(state) == "respond"

    def test_explain_intent(self):
        state = _make_state(passed=True)
        state["intent"] = "explain"
        assert should_generate_code(state) == "respond"

    def test_modify_graph_intent(self):
        state = _make_state(passed=True)
        state["intent"] = "modify_graph"
        assert should_generate_code(state) == "respond"


# ---------------------------------------------------------------------------
# interpret_intent — keyword fallback (no LLM)
# ---------------------------------------------------------------------------

from scaffold_ai.graph.nodes import interpret_intent


def _intent_state(user_input: str) -> dict:
    return {
        "user_input": user_input,
        "intent": "unknown",
        "graph_json": {},
        "iac_format": "cdk",
        "security_review": None,
        "generated_files": [],
        "errors": [],
        "retry_count": 0,
        "response": "",
    }


class TestInterpretIntentFallback:
    """Tests the keyword-based fallback when the LLM is unavailable."""

    async def _run(self, text: str) -> str:
        with patch(
            "scaffold_ai.graph.nodes.get_llm",
            side_effect=Exception("no llm"),
        ):
            result = await interpret_intent(_intent_state(text))
        return result["intent"]

    @pytest.mark.asyncio
    async def test_generate_keyword(self):
        assert await self._run("generate the cdk code") == "generate_code"

    @pytest.mark.asyncio
    async def test_code_keyword(self):
        assert await self._run("create the code now") == "generate_code"

    @pytest.mark.asyncio
    async def test_deploy_keyword(self):
        assert await self._run("deploy my architecture") == "generate_code"

    @pytest.mark.asyncio
    async def test_build_keyword(self):
        assert await self._run("build it") == "generate_code"

    @pytest.mark.asyncio
    async def test_explain_keyword(self):
        assert await self._run("explain what this does") == "explain"

    @pytest.mark.asyncio
    async def test_what_is_keyword(self):
        assert await self._run("what is DynamoDB") == "explain"

    @pytest.mark.asyncio
    async def test_remove_keyword(self):
        assert await self._run("remove the database node") == "modify_graph"

    @pytest.mark.asyncio
    async def test_delete_keyword(self):
        assert await self._run("delete the lambda") == "modify_graph"

    @pytest.mark.asyncio
    async def test_unknown_defaults_to_new_feature(self):
        assert await self._run("I want a todo app") == "new_feature"


# ---------------------------------------------------------------------------
# CloudFormationSpecialistAgent.generate
# ---------------------------------------------------------------------------

from scaffold_ai.agents.cloudformation_specialist import CloudFormationSpecialistAgent


def _graph(*node_types) -> dict:
    return {
        "nodes": [
            {
                "id": f"{t}-1",
                "type": t,
                "data": {"label": t.capitalize(), "type": t},
            }
            for t in node_types
        ],
        "edges": [],
    }


class TestCloudFormationSpecialist:
    @pytest.fixture
    def agent(self):
        return CloudFormationSpecialistAgent()

    @pytest.mark.asyncio
    async def test_empty_graph_returns_yaml(self, agent):
        result = await agent.generate({"nodes": [], "edges": []})
        assert "AWSTemplateFormatVersion" in result

    @pytest.mark.asyncio
    async def test_lambda_node_produces_serverless_function(self, agent):
        result = await agent.generate(_graph("lambda"))
        assert "AWS::Serverless::Function" in result

    @pytest.mark.asyncio
    async def test_database_node_produces_dynamodb_table(self, agent):
        result = await agent.generate(_graph("database"))
        assert "AWS::DynamoDB::Table" in result
        assert "PointInTimeRecoveryEnabled" in result

    @pytest.mark.asyncio
    async def test_api_node_produces_serverless_api(self, agent):
        result = await agent.generate(_graph("api"))
        assert "AWS::Serverless::Api" in result
        assert "TracingEnabled" in result

    @pytest.mark.asyncio
    async def test_auth_node_produces_user_pool_and_client(self, agent):
        result = await agent.generate(_graph("auth"))
        assert "AWS::Cognito::UserPool" in result
        assert "AWS::Cognito::UserPoolClient" in result

    @pytest.mark.asyncio
    async def test_storage_node_produces_encrypted_bucket(self, agent):
        result = await agent.generate(_graph("storage"))
        assert "AWS::S3::Bucket" in result
        assert "BlockPublicAcls" in result
        assert "SSEAlgorithm" in result

    @pytest.mark.asyncio
    async def test_queue_node_produces_queue_and_dlq(self, agent):
        result = await agent.generate(_graph("queue"))
        assert result.count("AWS::SQS::Queue") == 2  # main + DLQ

    @pytest.mark.asyncio
    async def test_notification_node_produces_sns_topic(self, agent):
        result = await agent.generate(_graph("notification"))
        assert "AWS::SNS::Topic" in result

    @pytest.mark.asyncio
    async def test_events_node_produces_event_bus(self, agent):
        result = await agent.generate(_graph("events"))
        assert "AWS::Events::EventBus" in result

    @pytest.mark.asyncio
    async def test_stream_node_produces_kinesis_stream(self, agent):
        result = await agent.generate(_graph("stream"))
        assert "AWS::Kinesis::Stream" in result

    @pytest.mark.asyncio
    async def test_workflow_node_produces_state_machine(self, agent):
        result = await agent.generate(_graph("workflow"))
        assert "AWS::StepFunctions::StateMachine" in result

    @pytest.mark.asyncio
    async def test_outputs_do_not_include_cognito_client(self, agent):
        """UserPoolClient does not expose Arn — verify it is excluded from Outputs."""
        result = await agent.generate(_graph("auth"))
        # Outputs section should reference UserPool Arn but not client
        lines = result.split("\n")
        output_section = "\n".join(lines[lines.index("Outputs:"):]) if "Outputs:" in lines else ""
        assert "UserPoolClientArn" not in output_section

    @pytest.mark.asyncio
    async def test_all_node_types_no_error(self, agent):
        all_types = [
            "lambda", "database", "api", "auth", "storage", "queue",
            "notification", "events", "stream", "workflow",
        ]
        result = await agent.generate(_graph(*all_types))
        assert "AWSTemplateFormatVersion" in result
        assert "Resources" in result


# ---------------------------------------------------------------------------
# TerraformSpecialistAgent.generate
# ---------------------------------------------------------------------------

from scaffold_ai.agents.terraform_specialist import TerraformSpecialistAgent


class TestTerraformSpecialist:
    @pytest.fixture
    def agent(self):
        return TerraformSpecialistAgent()

    @pytest.mark.asyncio
    async def test_empty_graph_returns_provider_block(self, agent):
        result = await agent.generate({"nodes": [], "edges": []})
        assert 'required_providers' in result
        assert 'provider "aws"' in result

    @pytest.mark.asyncio
    async def test_lambda_node(self, agent):
        result = await agent.generate(_graph("lambda"))
        assert 'resource "aws_lambda_function"' in result
        assert 'resource "aws_iam_role"' in result
        assert 'tracing_config' in result

    @pytest.mark.asyncio
    async def test_database_node(self, agent):
        result = await agent.generate(_graph("database"))
        assert 'resource "aws_dynamodb_table"' in result
        assert 'point_in_time_recovery' in result
        assert 'server_side_encryption' in result

    @pytest.mark.asyncio
    async def test_api_node(self, agent):
        result = await agent.generate(_graph("api"))
        assert 'resource "aws_apigatewayv2_api"' in result
        assert 'resource "aws_cloudwatch_log_group"' in result

    @pytest.mark.asyncio
    async def test_auth_node(self, agent):
        result = await agent.generate(_graph("auth"))
        assert 'resource "aws_cognito_user_pool"' in result
        assert 'resource "aws_cognito_user_pool_client"' in result

    @pytest.mark.asyncio
    async def test_storage_node(self, agent):
        result = await agent.generate(_graph("storage"))
        assert 'resource "aws_s3_bucket"' in result
        assert 'resource "aws_s3_bucket_versioning"' in result
        assert 'resource "aws_s3_bucket_public_access_block"' in result

    @pytest.mark.asyncio
    async def test_queue_node_produces_dlq(self, agent):
        result = await agent.generate(_graph("queue"))
        assert result.count('resource "aws_sqs_queue"') == 2  # main + DLQ

    @pytest.mark.asyncio
    async def test_notification_node(self, agent):
        result = await agent.generate(_graph("notification"))
        assert 'resource "aws_sns_topic"' in result

    @pytest.mark.asyncio
    async def test_events_node(self, agent):
        result = await agent.generate(_graph("events"))
        assert 'resource "aws_cloudwatch_event_bus"' in result

    @pytest.mark.asyncio
    async def test_stream_node(self, agent):
        result = await agent.generate(_graph("stream"))
        assert 'resource "aws_kinesis_stream"' in result
        assert '"KMS"' in result

    @pytest.mark.asyncio
    async def test_workflow_node(self, agent):
        result = await agent.generate(_graph("workflow"))
        assert 'resource "aws_sfn_state_machine"' in result
        assert 'resource "aws_iam_role"' in result
        assert 'tracing_configuration' in result

    @pytest.mark.asyncio
    async def test_slug_in_resource_name(self, agent):
        graph = {
            "nodes": [
                {
                    "id": "db-1",
                    "type": "database",
                    "data": {"label": "My User Table", "type": "database"},
                }
            ],
            "edges": [],
        }
        result = await agent.generate(graph)
        assert "my-user-table" in result

    @pytest.mark.asyncio
    async def test_outputs_contain_lambda_arn(self, agent):
        result = await agent.generate(_graph("lambda"))
        assert "output" in result
        assert "_arn" in result

    @pytest.mark.asyncio
    async def test_all_node_types_no_error(self, agent):
        all_types = [
            "lambda", "database", "api", "auth", "storage", "queue",
            "notification", "events", "stream", "workflow",
        ]
        result = await agent.generate(_graph(*all_types))
        assert 'provider "aws"' in result


# ---------------------------------------------------------------------------
# react_specialist_node — skips when intent != generate_code
# ---------------------------------------------------------------------------

from scaffold_ai.graph.nodes import react_specialist_node


class TestReactSpecialistNode:
    def _state(self, intent: str, nodes=None) -> dict:
        return {
            "user_input": "",
            "intent": intent,
            "graph_json": {"nodes": nodes or [], "edges": []},
            "iac_format": "cdk",
            "security_review": None,
            "generated_files": [],
            "errors": [],
            "retry_count": 0,
            "response": "",
        }

    @pytest.mark.asyncio
    async def test_non_generate_intent_returns_state_unchanged(self):
        state = self._state("new_feature")
        result = await react_specialist_node(state)
        assert result is state

    @pytest.mark.asyncio
    async def test_no_nodes_returns_state_unchanged(self):
        state = self._state("generate_code", nodes=[])
        result = await react_specialist_node(state)
        assert result["generated_files"] == []

    @pytest.mark.asyncio
    async def test_frontend_node_adds_files(self):
        nodes = [
            {
                "id": "fe-1",
                "type": "frontend",
                "data": {"label": "Frontend", "type": "frontend"},
            }
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        paths = [f["path"] for f in result["generated_files"]]
        assert any("layout.tsx" in p for p in paths)
        assert any("page.tsx" in p for p in paths)

    @pytest.mark.asyncio
    async def test_frontend_with_auth_adds_auth_provider(self):
        nodes = [
            {"id": "fe-1", "type": "frontend", "data": {"label": "Frontend", "type": "frontend"}},
            {"id": "auth-1", "type": "auth", "data": {"label": "Auth", "type": "auth"}},
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        paths = [f["path"] for f in result["generated_files"]]
        assert any("AuthProvider.tsx" in p for p in paths)

    @pytest.mark.asyncio
    async def test_frontend_with_api_adds_api_hooks(self):
        nodes = [
            {"id": "fe-1", "type": "frontend", "data": {"label": "Frontend", "type": "frontend"}},
            {"id": "api-1", "type": "api", "data": {"label": "API", "type": "api"}},
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        paths = [f["path"] for f in result["generated_files"]]
        assert any("api.ts" in p for p in paths)

    @pytest.mark.asyncio
    async def test_frontend_with_database_adds_data_table(self):
        nodes = [
            {"id": "fe-1", "type": "frontend", "data": {"label": "Frontend", "type": "frontend"}},
            {"id": "db-1", "type": "database", "data": {"label": "DB", "type": "database"}},
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        paths = [f["path"] for f in result["generated_files"]]
        assert any("DataTable.tsx" in p for p in paths)

    @pytest.mark.asyncio
    async def test_frontend_with_storage_adds_file_upload(self):
        nodes = [
            {"id": "fe-1", "type": "frontend", "data": {"label": "Frontend", "type": "frontend"}},
            {"id": "s3-1", "type": "storage", "data": {"label": "S3", "type": "storage"}},
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        paths = [f["path"] for f in result["generated_files"]]
        assert any("FileUpload.tsx" in p for p in paths)

    @pytest.mark.asyncio
    async def test_non_frontend_nodes_add_no_files(self):
        nodes = [
            {
                "id": "db-1",
                "type": "database",
                "data": {"label": "DB", "type": "database"},
            }
        ]
        state = self._state("generate_code", nodes=nodes)
        result = await react_specialist_node(state)
        assert result["generated_files"] == []


# ---------------------------------------------------------------------------
# SecuritySpecialistAgent.review — static fallback
# ---------------------------------------------------------------------------

from scaffold_ai.agents.security_specialist import SecuritySpecialistAgent


def _node(node_id: str, node_type: str, label: str | None = None) -> dict:
    return {
        "id": node_id,
        "type": node_type,
        "data": {"label": label or node_type.capitalize(), "type": node_type},
    }


class TestSecuritySpecialistAgent:
    @pytest.fixture
    def agent(self):
        return SecuritySpecialistAgent()

    # ------------------------------------------------------------------
    # Empty graph
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_empty_graph_passes_with_100(self, agent):
        result = await agent.review({"nodes": [], "edges": []})
        assert result["passed"] is True
        assert result["security_score"] == 100
        assert result["critical_issues"] == []
        assert result["warnings"] == []

    # ------------------------------------------------------------------
    # Return shape
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_result_has_required_keys(self, agent):
        result = await agent.review({"nodes": [_node("n1", "lambda")], "edges": []})
        for key in ("security_score", "passed", "critical_issues", "warnings",
                    "recommendations", "compliant_services", "security_enhancements"):
            assert key in result

    @pytest.mark.asyncio
    async def test_score_within_bounds(self, agent):
        nodes = [_node(f"n{i}", t) for i, t in enumerate(
            ["storage", "api", "queue", "lambda", "database", "auth"]
        )]
        result = await agent.review({"nodes": nodes, "edges": []})
        assert 0 <= result["security_score"] <= 100

    # ------------------------------------------------------------------
    # storage node
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_storage_node_produces_medium_warning(self, agent):
        result = await agent.review({"nodes": [_node("s1", "storage", "Uploads")], "edges": []})
        services = [w["service"] for w in result["warnings"]]
        assert "S3" in services

    @pytest.mark.asyncio
    async def test_storage_node_warning_is_medium_severity(self, agent):
        result = await agent.review({"nodes": [_node("s1", "storage")], "edges": []})
        s3_warnings = [w for w in result["warnings"] if w["service"] == "S3"]
        assert all(w["severity"] == "medium" for w in s3_warnings)

    @pytest.mark.asyncio
    async def test_storage_node_adds_config_change(self, agent):
        result = await agent.review({"nodes": [_node("s1", "storage")], "edges": []})
        changes = result["security_enhancements"]["config_changes"]
        node_ids = [c["node_id"] for c in changes]
        assert "s1" in node_ids

    # ------------------------------------------------------------------
    # database node
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_database_node_produces_recommendation(self, agent):
        result = await agent.review({"nodes": [_node("db1", "database", "UserTable")], "edges": []})
        services = [r["service"] for r in result["recommendations"]]
        assert "DynamoDB" in services

    @pytest.mark.asyncio
    async def test_database_node_no_critical_or_high_warning(self, agent):
        result = await agent.review({"nodes": [_node("db1", "database")], "edges": []})
        high_or_critical = [
            w for w in result["warnings"]
            if w.get("severity") in ("high", "critical")
        ]
        assert high_or_critical == []

    # ------------------------------------------------------------------
    # api node without auth — high severity warning
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_api_without_auth_produces_high_warning(self, agent):
        result = await agent.review({"nodes": [_node("api1", "api", "REST API")], "edges": []})
        high_warnings = [w for w in result["warnings"] if w.get("severity") == "high"]
        assert len(high_warnings) >= 1
        assert any("API Gateway" in w["service"] for w in high_warnings)

    @pytest.mark.asyncio
    async def test_api_with_auth_no_high_warning(self, agent):
        nodes = [_node("api1", "api"), _node("auth1", "auth")]
        result = await agent.review({"nodes": nodes, "edges": []})
        api_high = [
            w for w in result["warnings"]
            if w.get("severity") == "high" and "API" in w.get("service", "")
        ]
        assert api_high == []

    # ------------------------------------------------------------------
    # lambda node
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_lambda_node_produces_recommendations(self, agent):
        result = await agent.review({"nodes": [_node("fn1", "lambda", "ProcessOrder")], "edges": []})
        lambda_recs = [r for r in result["recommendations"] if r["service"] == "Lambda"]
        assert len(lambda_recs) >= 2  # X-Ray + least-privilege

    # ------------------------------------------------------------------
    # queue node
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_queue_node_produces_medium_warning(self, agent):
        result = await agent.review({"nodes": [_node("q1", "queue", "OrderQueue")], "edges": []})
        sqs_warnings = [w for w in result["warnings"] if w["service"] == "SQS"]
        assert len(sqs_warnings) >= 1
        assert sqs_warnings[0]["severity"] == "medium"

    # ------------------------------------------------------------------
    # auth node
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_auth_node_produces_recommendation(self, agent):
        result = await agent.review({"nodes": [_node("au1", "auth", "UserPool")], "edges": []})
        cognito_recs = [r for r in result["recommendations"] if r["service"] == "Cognito"]
        assert len(cognito_recs) >= 1

    # ------------------------------------------------------------------
    # Scoring arithmetic
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_high_warning_deducts_15_points(self, agent):
        # A lone api node without auth adds exactly one high warning
        result = await agent.review({"nodes": [_node("api1", "api")], "edges": []})
        high_count = len([w for w in result["warnings"] if w.get("severity") == "high"])
        medium_count = len([w for w in result["warnings"] if w.get("severity") == "medium"])
        expected = max(0, 100 - (high_count * 15) - (medium_count * 5))
        assert result["security_score"] == expected

    @pytest.mark.asyncio
    async def test_medium_warning_deducts_5_points(self, agent):
        # storage alone adds medium warnings only
        result = await agent.review({"nodes": [_node("s1", "storage")], "edges": []})
        medium_count = len([w for w in result["warnings"] if w.get("severity") == "medium"])
        high_count = len([w for w in result["warnings"] if w.get("severity") == "high"])
        expected = max(0, 100 - (high_count * 15) - (medium_count * 5))
        assert result["security_score"] == expected

    @pytest.mark.asyncio
    async def test_score_does_not_go_below_zero(self, agent):
        # Many nodes with issues should not produce negative score
        many_nodes = [_node(f"s{i}", "storage") for i in range(10)]
        many_nodes += [_node(f"api{i}", "api") for i in range(10)]
        result = await agent.review({"nodes": many_nodes, "edges": []})
        assert result["security_score"] >= 0

    # ------------------------------------------------------------------
    # pass/fail thresholds
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_passes_with_only_medium_warnings(self, agent):
        # storage → medium warnings only → should pass
        result = await agent.review({"nodes": [_node("s1", "storage")], "edges": []})
        assert result["passed"] is True

    @pytest.mark.asyncio
    async def test_passes_with_up_to_3_high_warnings(self, agent):
        # 3 api nodes without auth = 3 high warnings → still passes
        nodes = [_node(f"api{i}", "api") for i in range(3)]
        result = await agent.review({"nodes": nodes, "edges": []})
        high_count = len([w for w in result["warnings"] if w.get("severity") == "high"])
        assert high_count == 3
        assert result["passed"] is True

    @pytest.mark.asyncio
    async def test_fails_with_more_than_3_high_warnings(self, agent):
        # 4 api nodes without auth = 4 high warnings → fails
        nodes = [_node(f"api{i}", "api") for i in range(4)]
        result = await agent.review({"nodes": nodes, "edges": []})
        assert result["passed"] is False
