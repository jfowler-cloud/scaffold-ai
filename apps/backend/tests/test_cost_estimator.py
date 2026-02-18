"""Tests for cost estimator service."""

import pytest
from scaffold_ai.services.cost_estimator import CostEstimator


class TestCostEstimator:
    """Test cost estimation functionality."""

    @pytest.fixture
    def estimator(self):
        return CostEstimator()

    def test_estimate_empty_graph(self, estimator):
        """Test cost estimation with empty graph."""
        result = estimator.estimate({"nodes": [], "edges": []})

        assert result["total_monthly"] == 0
        assert result["breakdown"] == []

    def test_estimate_lambda_cost(self, estimator):
        """Test Lambda cost estimation."""
        graph = {
            "nodes": [{"id": "fn-1", "data": {"type": "lambda", "label": "Function"}}],
            "edges": [],
        }

        result = estimator.estimate(graph)

        assert result["total_monthly"] > 0
        assert any("Lambda" in item["service"] for item in result["breakdown"])

    def test_estimate_database_cost(self, estimator):
        """Test DynamoDB cost estimation."""
        graph = {
            "nodes": [{"id": "db-1", "data": {"type": "database", "label": "Table"}}],
            "edges": [],
        }

        result = estimator.estimate(graph)

        assert result["total_monthly"] > 0
        assert any(item["service"] == "DynamoDB" for item in result["breakdown"])

    def test_estimate_multiple_services(self, estimator):
        """Test cost estimation with multiple services."""
        graph = {
            "nodes": [
                {"id": "fn-1", "data": {"type": "lambda", "label": "Function"}},
                {"id": "db-1", "data": {"type": "database", "label": "Table"}},
                {"id": "api-1", "data": {"type": "api", "label": "API"}},
            ],
            "edges": [],
        }

        result = estimator.estimate(graph)

        assert result["total_monthly"] > 0
        assert len(result["breakdown"]) >= 3
