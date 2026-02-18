"""Tests for CDK generator service."""

import pytest
from scaffold_ai.services.cdk_generator import CDKGenerator


class TestCDKGenerator:
    """Test CDK code generation."""

    @pytest.fixture
    def generator(self):
        return CDKGenerator()

    def test_generate_empty_stack(self, generator):
        """Test generating stack with no nodes."""
        code = generator.generate([])
        
        assert "ScaffoldAiStack" in code
        assert "import * as cdk" in code

    def test_generate_lambda(self, generator):
        """Test Lambda function generation."""
        nodes = [{"id": "fn-1", "data": {"type": "lambda", "label": "MyFunction"}}]
        
        code = generator.generate(nodes)
        
        assert "lambda.Function" in code
        assert "myfunction" in code

    def test_generate_api_gateway(self, generator):
        """Test API Gateway generation."""
        nodes = [{"id": "api-1", "data": {"type": "api", "label": "MyAPI"}}]
        
        code = generator.generate(nodes)
        
        assert "apigateway.RestApi" in code
        assert "ALL_ORIGINS" in code

    def test_generate_dynamodb(self, generator):
        """Test DynamoDB table generation."""
        nodes = [{"id": "db-1", "data": {"type": "database", "label": "MyTable"}}]
        
        code = generator.generate(nodes)
        
        assert "dynamodb.Table" in code
        assert "PAY_PER_REQUEST" in code

    def test_generate_s3_bucket(self, generator):
        """Test S3 bucket generation."""
        nodes = [{"id": "s3-1", "data": {"type": "storage", "label": "MyBucket"}}]
        
        code = generator.generate(nodes)
        
        assert "s3.Bucket" in code
        assert "S3_MANAGED" in code

    def test_imports_based_on_nodes(self, generator):
        """Test that imports are generated based on node types."""
        nodes = [
            {"id": "fn-1", "data": {"type": "lambda", "label": "Fn"}},
            {"id": "db-1", "data": {"type": "database", "label": "DB"}}
        ]
        
        code = generator.generate(nodes)
        
        assert "aws-lambda" in code
        assert "aws-dynamodb" in code
