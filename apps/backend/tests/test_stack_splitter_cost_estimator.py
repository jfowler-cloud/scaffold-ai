"""Tests for StackSplitter and CostEstimator services."""
import pytest
from scaffold_ai.services.stack_splitter import StackSplitter
from scaffold_ai.services.cost_estimator import CostEstimator


def make_node(id: str, type: str) -> dict:
    return {"id": id, "data": {"type": type, "label": id}}


def make_edge(source: str, target: str) -> dict:
    return {"id": f"{source}-{target}", "source": source, "target": target}


# ── StackSplitter ──────────────────────────────────────────────────────────────

class TestStackSplitter:
    def setup_method(self):
        self.splitter = StackSplitter()

    def test_should_split_false_for_small_arch(self):
        nodes = [make_node(f"n{i}", "lambda") for i in range(5)]
        assert self.splitter.should_split(nodes) is False

    def test_should_split_true_for_large_arch(self):
        nodes = [make_node(f"n{i}", "lambda") for i in range(16)]
        assert self.splitter.should_split(nodes) is True

    def test_split_by_layer_categorizes_network(self):
        nodes = [make_node("vpc-1", "vpc")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "network" in result
        assert result["network"]["nodes"][0]["id"] == "vpc-1"

    def test_split_by_layer_categorizes_data(self):
        nodes = [make_node("db-1", "database"), make_node("s3-1", "storage")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "data" in result
        assert len(result["data"]["nodes"]) == 2

    def test_split_by_layer_categorizes_compute(self):
        nodes = [make_node("fn-1", "lambda")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "compute" in result

    def test_split_by_layer_categorizes_frontend(self):
        nodes = [make_node("cdn-1", "cdn"), make_node("api-1", "api")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "frontend" in result
        assert len(result["frontend"]["nodes"]) == 2

    def test_split_by_layer_unknown_type_goes_to_compute(self):
        nodes = [make_node("mystery-1", "unknown-type")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "compute" in result

    def test_split_by_layer_removes_empty_stacks(self):
        nodes = [make_node("fn-1", "lambda")]
        result = self.splitter.split_by_layer(nodes, [])
        assert "network" not in result
        assert "data" not in result

    def test_split_by_layer_distributes_edges(self):
        nodes = [make_node("fn-1", "lambda"), make_node("db-1", "database")]
        edges = [make_edge("fn-1", "db-1")]
        result = self.splitter.split_by_layer(nodes, edges)
        # Edge should appear in compute (source) and data (target)
        assert len(result["compute"]["edges"]) == 1
        assert len(result["data"]["edges"]) == 1

    def test_split_by_layer_same_stack_edge_not_duplicated(self):
        nodes = [make_node("fn-1", "lambda"), make_node("fn-2", "lambda")]
        edges = [make_edge("fn-1", "fn-2")]
        result = self.splitter.split_by_layer(nodes, edges)
        # Both in compute — edge added once to source stack only
        assert len(result["compute"]["edges"]) == 1

    def test_generate_nested_stack_code_returns_files(self):
        stacks = {
            "compute": {"nodes": [make_node("fn-1", "lambda")], "edges": []},
        }
        files = self.splitter.generate_nested_stack_code(stacks, format="cdk")
        paths = [f["path"] for f in files]
        assert any("main-stack.ts" in p for p in paths)
        assert any("compute-stack.ts" in p for p in paths)

    def test_generate_nested_stack_code_main_stack_content(self):
        stacks = {"data": {"nodes": [make_node("db-1", "database")], "edges": []}}
        files = self.splitter.generate_nested_stack_code(stacks, format="cdk")
        main = next(f for f in files if "main-stack.ts" in f["path"])
        assert "DataStack" in main["content"]
        assert "MainStack" in main["content"]

    def test_generate_nested_stack_code_unknown_format_returns_empty(self):
        stacks = {"compute": {"nodes": [make_node("fn-1", "lambda")], "edges": []}}
        files = self.splitter.generate_nested_stack_code(stacks, format="terraform")
        assert files == []


# ── CostEstimator ──────────────────────────────────────────────────────────────

class TestCostEstimator:
    def setup_method(self):
        self.estimator = CostEstimator()

    def test_estimate_empty_graph(self):
        result = self.estimator.estimate({"nodes": [], "edges": []})
        assert result["total_monthly"] == 0
        assert result["breakdown"] == []

    def test_estimate_single_lambda(self):
        graph = {"nodes": [make_node("fn-1", "lambda")], "edges": []}
        result = self.estimator.estimate(graph)
        assert result["total_monthly"] > 0
        assert any(b["service"] == "AWS Lambda" for b in result["breakdown"])

    def test_estimate_includes_data_transfer_for_large_arch(self):
        nodes = [make_node(f"n{i}", "lambda") for i in range(4)]
        result = self.estimator.estimate({"nodes": nodes, "edges": []})
        assert any(b["service"] == "Data Transfer" for b in result["breakdown"])

    def test_estimate_no_data_transfer_for_small_arch(self):
        nodes = [make_node("fn-1", "lambda"), make_node("fn-2", "lambda")]
        result = self.estimator.estimate({"nodes": nodes, "edges": []})
        assert not any(b["service"] == "Data Transfer" for b in result["breakdown"])

    def test_estimate_multiple_services(self):
        nodes = [
            make_node("fn-1", "lambda"),
            make_node("api-1", "api"),
            make_node("db-1", "database"),
        ]
        result = self.estimator.estimate({"nodes": nodes, "edges": []})
        assert len(result["breakdown"]) == 3
        assert result["total_monthly"] > 0

    def test_estimate_unknown_type_not_in_breakdown(self):
        graph = {"nodes": [make_node("x-1", "unknown-type")], "edges": []}
        result = self.estimator.estimate(graph)
        assert result["breakdown"] == []

    def test_estimate_has_disclaimer(self):
        result = self.estimator.estimate({"nodes": [make_node("fn-1", "lambda")], "edges": []})
        assert "disclaimer" in result

    def test_estimate_has_assumptions(self):
        result = self.estimator.estimate({"nodes": [make_node("fn-1", "lambda")], "edges": []})
        assert len(result["assumptions"]) > 0

    def test_get_optimization_tips_lambda(self):
        graph = {"nodes": [make_node("fn-1", "lambda")], "edges": []}
        tips = self.estimator.get_optimization_tips(graph)
        assert any("Lambda" in t for t in tips)

    def test_get_optimization_tips_database(self):
        graph = {"nodes": [make_node("db-1", "database")], "edges": []}
        tips = self.estimator.get_optimization_tips(graph)
        assert any("DynamoDB" in t for t in tips)

    def test_get_optimization_tips_storage(self):
        graph = {"nodes": [make_node("s3-1", "storage")], "edges": []}
        tips = self.estimator.get_optimization_tips(graph)
        assert any("S3" in t for t in tips)

    def test_get_optimization_tips_large_arch(self):
        nodes = [make_node(f"n{i}", "lambda") for i in range(6)]
        tips = self.estimator.get_optimization_tips({"nodes": nodes, "edges": []})
        assert any("Cost Explorer" in t for t in tips)

    def test_get_optimization_tips_empty(self):
        tips = self.estimator.get_optimization_tips({"nodes": [], "edges": []})
        assert isinstance(tips, list)
