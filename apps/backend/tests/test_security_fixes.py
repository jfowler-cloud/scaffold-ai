"""Tests for security fixes applied in Round 3."""

import pytest
from scaffold_ai.tools.git_operator import GitOperatorTool
from scaffold_ai.services.cdk_deployment import CDKDeploymentService


class TestGitOperatorSecurity:
    """Test git operator security fixes."""

    @pytest.mark.asyncio
    async def test_commit_requires_files(self, tmp_path):
        """Test that commit_changes requires explicit file list."""
        git_tool = GitOperatorTool(str(tmp_path))
        git_tool.repo  # Initialize repo
        
        result = await git_tool.commit_changes("test commit", [])
        
        assert result["success"] is False
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_commit_with_explicit_files(self, tmp_path):
        """Test that commit works with explicit file list."""
        git_tool = GitOperatorTool(str(tmp_path))
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        git_tool.repo.index.add([str(test_file)])
        result = await git_tool.commit_changes("test commit", [str(test_file)])
        
        assert result["success"] is True
        assert "commit" in result


class TestDeploymentApproval:
    """Test deployment approval gate."""

    def test_approval_default_true(self):
        """Test that require_approval defaults to True."""
        from scaffold_ai.main import DeployRequest
        
        request = DeployRequest(
            stack_name="TestStack",
            cdk_code="test",
            app_code="test"
        )
        
        assert request.require_approval is True

    def test_approval_can_be_disabled(self):
        """Test that require_approval can be set to False."""
        from scaffold_ai.main import DeployRequest
        
        request = DeployRequest(
            stack_name="TestStack",
            cdk_code="test",
            app_code="test",
            require_approval=False
        )
        
        assert request.require_approval is False


class TestCDKGenerator:
    """Test CDK generator security fixes."""

    def test_no_hardcoded_domains(self):
        """Test that generated code doesn't contain hardcoded example.com."""
        from scaffold_ai.services.cdk_generator import CDKGenerator
        
        generator = CDKGenerator()
        nodes = [
            {"id": "api-1", "data": {"type": "api", "label": "API"}},
            {"id": "cdn-1", "data": {"type": "cdn", "label": "CDN"}}
        ]
        
        code = generator.generate(nodes)
        
        assert "example.com" not in code
        assert "ALL_ORIGINS" in code or "Configure origin" in code

    def test_no_hardcoded_emails(self):
        """Test that generated code doesn't contain hardcoded emails."""
        from scaffold_ai.services.cdk_generator import CDKGenerator
        
        generator = CDKGenerator()
        nodes = [{"id": "notif-1", "data": {"type": "notification", "label": "Notifications"}}]
        
        code = generator.generate(nodes)
        
        assert "user@example.com" not in code
