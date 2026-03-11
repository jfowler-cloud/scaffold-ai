"""Tests for SynthesizerTool, PythonCDKSpecialist, and agent prompt constants."""
import subprocess
from unittest.mock import patch, MagicMock
import pytest

from scaffold_ai.tools.synthesizer import SynthesizerTool
from scaffold_ai.agents.python_cdk_specialist import PythonCDKSpecialist
from scaffold_ai.agents.architect import ARCHITECT_SYSTEM_PROMPT
from scaffold_ai.agents.interpreter import INTERPRETER_SYSTEM_PROMPT


def make_node(id: str, type: str, label: str = "") -> dict:
    return {"id": id, "data": {"type": type, "label": label or id}}


# ── Agent prompt constants ─────────────────────────────────────────────────────

class TestAgentPrompts:
    def test_architect_prompt_is_string(self):
        assert isinstance(ARCHITECT_SYSTEM_PROMPT, str)
        assert len(ARCHITECT_SYSTEM_PROMPT) > 0

    def test_interpreter_prompt_is_string(self):
        assert isinstance(INTERPRETER_SYSTEM_PROMPT, str)
        assert len(INTERPRETER_SYSTEM_PROMPT) > 0

    def test_interpreter_prompt_contains_intent_categories(self):
        assert "new_feature" in INTERPRETER_SYSTEM_PROMPT
        assert "modify_graph" in INTERPRETER_SYSTEM_PROMPT
        assert "generate_code" in INTERPRETER_SYSTEM_PROMPT



class TestCDKSpecialistAgent:
    @pytest.mark.asyncio
    async def test_generate_empty_graph_returns_empty(self):
        from scaffold_ai.agents.cdk_specialist import CDKSpecialistAgent
        agent = CDKSpecialistAgent()
        result = await agent.generate({"nodes": [], "edges": []})
        assert result == []

    @pytest.mark.asyncio
    async def test_generate_returns_files(self):
        from scaffold_ai.agents.cdk_specialist import CDKSpecialistAgent
        agent = CDKSpecialistAgent()
        nodes = [{"id": "fn-1", "data": {"type": "lambda", "label": "Handler"}}]
        result = await agent.generate({"nodes": nodes, "edges": []})
        assert len(result) == 1
        assert "scaffold-ai-stack.ts" in result[0]["path"]
        assert len(result[0]["content"]) > 0


# ── SynthesizerTool ────────────────────────────────────────────────────────────

class TestSynthesizerTool:
    def setup_method(self):
        self.tool = SynthesizerTool("/tmp/test-infra")

    @pytest.mark.asyncio
    async def test_synth_success(self):
        mock_result = MagicMock(returncode=0, stdout="Successfully synthesized", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            result = await self.tool.synth()
        assert result["success"] is True
        assert "Successfully synthesized" in result["output"]

    @pytest.mark.asyncio
    async def test_synth_failure(self):
        mock_result = MagicMock(returncode=1, stdout="", stderr="Error: missing construct")
        with patch("subprocess.run", return_value=mock_result):
            result = await self.tool.synth()
        assert result["success"] is False
        assert "missing construct" in result["error"]

    @pytest.mark.asyncio
    async def test_synth_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cdk", 60)):
            result = await self.tool.synth()
        assert result["success"] is False
        assert "timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_synth_cdk_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            result = await self.tool.synth()
        assert result["success"] is False
        assert "CDK CLI not found" in result["error"]

    @pytest.mark.asyncio
    async def test_synth_os_error(self):
        with patch("subprocess.run", side_effect=OSError("permission denied")):
            result = await self.tool.synth()
        assert result["success"] is False
        assert "permission denied" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_typescript_success(self):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            result = await self.tool.validate_typescript("const x = 1;")
        assert result["valid"] is True
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_validate_typescript_failure(self):
        mock_result = MagicMock(returncode=1, stdout="", stderr="error TS2304: Cannot find name")
        with patch("subprocess.run", return_value=mock_result):
            result = await self.tool.validate_typescript("const x: Foo = 1;")
        assert result["valid"] is False
        assert any("TS2304" in e for e in result["errors"])

    @pytest.mark.asyncio
    async def test_validate_typescript_exception(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("tsc not found")):
            result = await self.tool.validate_typescript("const x = 1;")
        assert result["valid"] is False
        assert len(result["errors"]) > 0


# ── PythonCDKSpecialist ────────────────────────────────────────────────────────

class TestPythonCDKSpecialist:
    def setup_method(self):
        self.specialist = PythonCDKSpecialist()

    def test_generate_stack_returns_string(self):
        nodes = [make_node("fn-1", "lambda", "My Function")]
        result = self.specialist.generate_stack(nodes, [])
        assert isinstance(result, str)
        assert "class MyStack(Stack)" in result

    def test_generate_stack_custom_name(self):
        result = self.specialist.generate_stack([], [], stack_name="AppStack")
        assert "class AppStack(Stack)" in result

    def test_generate_stack_lambda_construct(self):
        nodes = [make_node("fn-1", "lambda", "Handler")]
        result = self.specialist.generate_stack(nodes, [])
        assert "_lambda.Function" in result
        assert "fn-1" in result

    def test_generate_stack_api_construct(self):
        nodes = [make_node("api-1", "api", "My API")]
        result = self.specialist.generate_stack(nodes, [])
        assert "apigw.RestApi" in result

    def test_generate_stack_database_construct(self):
        nodes = [make_node("db-1", "database", "Users Table")]
        result = self.specialist.generate_stack(nodes, [])
        assert "dynamodb.Table" in result
        assert "point_in_time_recovery=True" in result

    def test_generate_stack_storage_construct(self):
        nodes = [make_node("s3-1", "storage", "Assets")]
        result = self.specialist.generate_stack(nodes, [])
        assert "s3.Bucket" in result
        assert "BLOCK_ALL" in result

    def test_generate_stack_queue_construct(self):
        nodes = [make_node("q-1", "queue", "Job Queue")]
        result = self.specialist.generate_stack(nodes, [])
        assert "sqs.Queue" in result
        assert "dead_letter_queue" in result

    def test_generate_stack_auth_construct(self):
        nodes = [make_node("auth-1", "auth", "User Pool")]
        result = self.specialist.generate_stack(nodes, [])
        assert "cognito.UserPool" in result
        assert "ENFORCED" in result

    def test_generate_app(self):
        result = self.specialist.generate_app("AppStack")
        assert "AppStack" in result
        assert "app.synth()" in result

    def test_generate_requirements(self):
        result = self.specialist.generate_requirements()
        assert "aws-cdk-lib" in result
        assert "constructs" in result

    def test_get_imports_includes_relevant_modules(self):
        nodes = [
            make_node("fn-1", "lambda"),
            make_node("db-1", "database"),
            make_node("s3-1", "storage"),
            make_node("q-1", "queue"),
            make_node("auth-1", "auth"),
            make_node("cdn-1", "cdn"),
            make_node("eb-1", "events"),
        ]
        result = self.specialist.generate_stack(nodes, [])
        assert "aws_lambda" in result
        assert "aws_dynamodb" in result
        assert "aws_s3" in result
        assert "aws_sqs" in result
        assert "aws_cognito" in result
        assert "aws_cloudfront" in result
        assert "aws_events" in result

    def test_to_var_name_converts_spaces_and_dashes(self):
        assert self.specialist._to_var_name("My Lambda") == "my_lambda"
        assert self.specialist._to_var_name("api-gateway") == "api_gateway"
