"""Tests for new service modules."""

import pytest
from scaffold_ai.services.cost_estimator import CostEstimator
from scaffold_ai.services.security_autofix import SecurityAutoFix
from scaffold_ai.services.templates import ArchitectureTemplates
from scaffold_ai.services.sharing import SharingService
from scaffold_ai.services.security_history import SecurityHistoryService
from scaffold_ai.services.stack_splitter import StackSplitter
from scaffold_ai.services.cdk_generator import CDKGenerator


class TestCostEstimator:
    def test_estimate_empty_graph(self):
        estimator = CostEstimator()
        result = estimator.estimate({"nodes": [], "edges": []})
        assert result["total_monthly"] == 0
        assert result["breakdown"] == []

    def test_estimate_with_lambda(self):
        estimator = CostEstimator()
        graph = {"nodes": [{"data": {"type": "lambda"}}], "edges": []}
        result = estimator.estimate(graph)
        assert result["total_monthly"] > 0
        assert any(item["service"] == "AWS Lambda" for item in result["breakdown"])


class TestSecurityAutoFix:
    def test_analyze_empty_graph(self):
        autofix = SecurityAutoFix()
        updated, changes = autofix.analyze_and_fix({"nodes": [], "edges": []})
        assert updated == {"nodes": [], "edges": []}
        assert changes == []

    def test_security_score_empty(self):
        autofix = SecurityAutoFix()
        result = autofix.get_security_score({"nodes": [], "edges": []})
        assert result["score"] == 0
        assert result["max_score"] == 0

    def test_adds_encryption_to_storage(self):
        autofix = SecurityAutoFix()
        graph = {"nodes": [{"id": "s1", "data": {"type": "storage"}}], "edges": []}
        updated, changes = autofix.analyze_and_fix(graph)
        assert len(changes) > 0


class TestTemplates:
    def test_list_templates(self):
        templates = ArchitectureTemplates()
        result = templates.list_templates()
        assert len(result) == 6
        assert any(t["id"] == "todo-app" for t in result)

    def test_get_template(self):
        templates = ArchitectureTemplates()
        result = templates.get_template("todo-app")
        assert result["name"] == "Todo App with Auth"
        assert len(result["nodes"]) > 0

    def test_get_invalid_template(self):
        templates = ArchitectureTemplates()
        with pytest.raises(ValueError):
            templates.get_template("invalid")


class TestSharing:
    def test_create_and_retrieve(self):
        service = SharingService()
        graph = {"nodes": [{"id": "1"}], "edges": []}
        share_id = service.create_share_link(graph, "Test")

        retrieved = service.get_shared_architecture(share_id)
        assert retrieved is not None
        assert retrieved["graph"] == graph
        assert retrieved["title"] == "Test"

    def test_get_nonexistent(self):
        service = SharingService()
        result = service.get_shared_architecture("nonexistent")
        assert result is None


class TestSecurityHistory:
    def test_record_and_retrieve(self):
        service = SecurityHistoryService()
        service.record_score("arch1", 75, [])

        history = service.get_history("arch1")
        assert len(history) == 1
        assert history[0]["score"] == 75

    def test_improvement_calculation(self):
        service = SecurityHistoryService()
        service.record_score("arch1", 60, [])
        service.record_score("arch1", 80, [])

        improvement = service.get_improvement("arch1")
        assert improvement["improvement"] == 20
        assert improvement["trend"] == "improving"


class TestStackSplitter:
    def test_should_not_split_small(self):
        splitter = StackSplitter()
        nodes = [{"id": str(i)} for i in range(10)]
        assert not splitter.should_split(nodes)

    def test_should_split_large(self):
        splitter = StackSplitter()
        nodes = [{"id": str(i)} for i in range(20)]
        assert splitter.should_split(nodes)

    def test_split_by_layer(self):
        splitter = StackSplitter()
        nodes = [
            {"id": "1", "data": {"type": "database"}},
            {"id": "2", "data": {"type": "lambda"}},
        ]
        result = splitter.split_by_layer(nodes, [])
        assert "data" in result
        assert "compute" in result


class TestCDKGenerator:
    def test_generate_empty(self):
        generator = CDKGenerator()
        result = generator.generate([], [])
        assert "export class ScaffoldAiStack" in result

    def test_generate_with_lambda(self):
        generator = CDKGenerator()
        nodes = [{"id": "fn1", "data": {"type": "lambda", "label": "MyFunction"}}]
        result = generator.generate(nodes, [])
        assert "lambda.Function" in result
        assert "fn1" in result  # Check for node ID in CDK construct

    def test_edge_wiring(self):
        generator = CDKGenerator()
        nodes = [
            {"id": "fn1", "data": {"type": "lambda", "label": "Fn"}},
            {"id": "db1", "data": {"type": "database", "label": "Table"}},
        ]
        edges = [{"source": "fn1", "target": "db1"}]
        result = generator.generate(nodes, edges)
        assert "grantReadWriteData" in result
