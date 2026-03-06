"""Tests for SecurityAutoFix service."""
import pytest
from scaffold_ai.services.security_autofix import SecurityAutoFix, _resolve_type


def node(id: str, type: str = "", label: str = "") -> dict:
    return {"id": id, "data": {"type": type, "label": label or id}}


def api_node():
    return node("api-1", "api", "API Gateway")


def auth_node():
    return node("auth-1", "auth", "Cognito")


def storage_node(label="S3 Bucket"):
    return node("s3-1", "storage", label)


def db_node(label="DynamoDB"):
    return node("db-1", "database", label)


def lambda_node(label="Lambda"):
    return node("fn-1", "lambda", label)


def queue_node(label="SQS Queue"):
    return node("q-1", "queue", label)


def cdn_node(label="CloudFront"):
    return node("cdn-1", "cdn", label)


class TestResolveType:
    def test_resolves_known_type(self):
        assert _resolve_type({"id": "x", "data": {"type": "lambda"}}) == "lambda"

    def test_falls_back_to_id_keyword(self):
        assert _resolve_type({"id": "my-sqs-queue", "data": {}}) == "queue"

    def test_lambda_beats_dlq_in_id(self):
        # 'dlq-processor-lambda' should resolve to lambda, not dlq
        assert _resolve_type({"id": "dlq-processor-lambda", "data": {}}) == "lambda"

    def test_unknown_type_returns_unknown(self):
        assert _resolve_type({"id": "mystery-node", "data": {}}) == "unknown"

    def test_storage_keyword_in_id(self):
        assert _resolve_type({"id": "my-s3-bucket", "data": {}}) == "storage"


class TestSecurityAutoFix:
    def setup_method(self):
        self.fixer = SecurityAutoFix()

    def test_empty_graph_returns_unchanged(self):
        graph = {"nodes": [], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert changes == []

    def test_adds_auth_when_api_present_without_auth(self):
        graph = {"nodes": [api_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert any("Cognito" in c for c in changes)
        types = [n["data"]["type"] for n in result["nodes"]]
        assert "auth" in types

    def test_no_auth_added_when_auth_already_present(self):
        graph = {"nodes": [api_node(), auth_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        # Auth node already present — no new auth node added, only 2 nodes remain
        assert len(result["nodes"]) == 2

    def test_no_auth_added_when_no_api(self):
        graph = {"nodes": [lambda_node()], "edges": []}
        _, changes = self.fixer.analyze_and_fix(graph)
        assert not any("Cognito" in c for c in changes)

    def test_storage_gets_kms_encryption(self):
        graph = {"nodes": [storage_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        s3 = result["nodes"][0]
        assert s3["data"]["config"]["encryption"] == "KMS"
        assert s3["data"]["config"]["kms_key_rotation"] is True
        assert any("KMS" in c for c in changes)

    def test_storage_gets_block_public_access(self):
        graph = {"nodes": [storage_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["block_public_access"] is True

    def test_storage_gets_versioning(self):
        graph = {"nodes": [storage_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["versioning"] is True

    def test_storage_gets_https_only(self):
        graph = {"nodes": [storage_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["https_only"] is True

    def test_storage_already_kms_not_changed(self):
        n = storage_node()
        n["data"]["config"] = {"encryption": "KMS", "kms_key_rotation": True,
                                "block_public_access": True, "versioning": True, "https_only": True}
        graph = {"nodes": [n], "edges": []}
        _, changes = self.fixer.analyze_and_fix(graph)
        assert not any("KMS" in c for c in changes)

    def test_database_gets_encryption(self):
        graph = {"nodes": [db_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["encryption"] == "KMS"

    def test_database_gets_pitr(self):
        graph = {"nodes": [db_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["pitr"] is True

    def test_lambda_gets_tracing(self):
        graph = {"nodes": [lambda_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["tracing"] == "Active"

    def test_queue_gets_encryption(self):
        graph = {"nodes": [queue_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["encryption"] == "KMS"

    def test_cdn_gets_security_headers(self):
        graph = {"nodes": [cdn_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["security_headers"] is True

    def test_api_gets_waf_and_throttling(self):
        graph = {"nodes": [node("api-1", "api", "API Gateway")], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        cfg = result["nodes"][0]["data"]["config"]
        assert cfg["waf_enabled"] is True
        assert cfg["throttling"] is True

    def test_sns_gets_encryption(self):
        n = node("sns-1", "sns", "Alerts")
        graph = {"nodes": [n], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["encryption"] == "KMS"

    def test_auth_node_gets_mfa_enforced(self):
        graph = {"nodes": [auth_node()], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["mfa"] == "REQUIRED"

    def test_glue_gets_encryption(self):
        n = node("glue-1", "glue", "Glue Catalog")
        graph = {"nodes": [n], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["encryption"] is True

    def test_events_gets_resource_policy(self):
        n = node("eb-1", "events", "Event Bus")
        graph = {"nodes": [n], "edges": []}
        result, changes = self.fixer.analyze_and_fix(graph)
        assert result["nodes"][0]["data"]["config"]["resource_policy"] == "restricted"

    def test_get_security_score_no_api_no_auth_full_auth_score(self):
        # No API → auth score is full (20 pts)
        graph = {"nodes": [lambda_node()], "edges": []}
        score = self.fixer.get_security_score(graph)
        assert score["score"] > 0

    def test_get_security_score_api_without_auth_penalized(self):
        graph_with = {"nodes": [api_node(), auth_node()], "edges": []}
        graph_without = {"nodes": [api_node()], "edges": []}
        score_with = self.fixer.get_security_score(graph_with)
        score_without = self.fixer.get_security_score(graph_without)
        assert score_with["score"] > score_without["score"]

    def test_get_security_score_percentage_in_range(self):
        graph = {"nodes": [api_node(), auth_node(), storage_node(), db_node()], "edges": []}
        score = self.fixer.get_security_score(graph)
        assert 0 <= score["percentage"] <= 100

    def test_get_security_score_empty_returns_zero(self):
        score = self.fixer.get_security_score({"nodes": [], "edges": []})
        assert score["score"] == 0
        assert score["percentage"] == 0
