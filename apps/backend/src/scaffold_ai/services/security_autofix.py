"""Security auto-fix service for automatically improving architecture security."""

from typing import Dict, List, Tuple


class SecurityAutoFix:
    """Automatically add security improvements to architectures."""

"""Security auto-fix service for automatically improving architecture security."""

from typing import Dict, List, Tuple


# Keywords to match node types by ID or label when data.type is missing/generic
_TYPE_HINTS = {
    "queue": ["queue", "sqs", "fifo"],
    "dlq": ["dlq", "dead-letter", "deadletter", "dead_letter"],
    "storage": ["bucket", "s3", "storage"],
    "database": ["db", "database", "dynamo", "table", "rds", "aurora"],
    "lambda": ["lambda", "function", "fn", "handler", "processor", "detector", "athena"],
    "api": ["api", "gateway", "apigw", "rest", "http"],
    "auth": ["auth", "cognito", "identity", "login"],
    "cdn": ["cdn", "cloudfront", "distribution"],
    "sns": ["sns", "topic", "notification", "alert"],
    "events": ["eventbridge", "event-bus", "events", "eventbus"],
    "glue": ["glue", "catalog", "etl", "crawler"],
    "stream": ["kinesis", "stream", "firehose"],
}


def _resolve_type(node: dict) -> str:
    """Resolve the effective type of a node using data.type, id, and label.

    Priority order:
    1. data.type if it's a known type (most reliable)
    2. Keyword matching on id + label — lambda beats dlq when both match
       (e.g. 'dlq-processor-lambda' is a Lambda, not a queue)
    """
    data_type = node.get("data", {}).get("type", "")
    known_types = {"queue", "storage", "database", "lambda", "api", "auth",
                   "cdn", "sns", "events", "glue", "stream", "notification", "frontend"}

    if data_type in known_types:
        return data_type

    node_id = node.get("id", "").lower()
    label = node.get("data", {}).get("label", "").lower()
    combined = f"{node_id} {label}"

    # Lambda takes priority — check before dlq so 'dlq-processor-lambda' → lambda
    if any(k in combined for k in _TYPE_HINTS["lambda"]):
        return "lambda"
    # Then dlq/queue
    if any(k in combined for k in _TYPE_HINTS["dlq"]):
        return "queue"
    # Rest of types
    for t, keywords in _TYPE_HINTS.items():
        if t in ("lambda", "dlq"):
            continue
        if any(k in combined for k in keywords):
            return t
    return data_type or "unknown"


class SecurityAutoFix:
    """Automatically add security improvements to architectures."""

    def analyze_and_fix(self, graph: Dict) -> Tuple[Dict, List[str]]:
        """
        Analyze architecture and automatically add security improvements.
        """
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        changes = []

        if not nodes:
            return graph, changes

        # Check for missing auth
        has_auth = any(_resolve_type(n) == "auth" for n in nodes)
        has_api = any(_resolve_type(n) == "api" for n in nodes)
        if has_api and not has_auth:
            auth_node, auth_edges = self._add_auth_node(nodes, edges)
            nodes.append(auth_node)
            edges.extend(auth_edges)
            changes.append("✅ Added Cognito user pool for API authentication")

        for node in nodes:
            t = _resolve_type(node)
            config = node.setdefault("data", {}).setdefault("config", {})
            label = node.get("data", {}).get("label", node.get("id", "unknown"))

            if t == "storage":
                if config.get("encryption") in (None, "AES256", "SSE-S3"):
                    config["encryption"] = "KMS"
                    config["kms_key_rotation"] = True
                    changes.append(f"✅ Upgraded S3 '{label}' to KMS encryption with key rotation")
                if not config.get("block_public_access"):
                    config["block_public_access"] = True
                    changes.append(f"✅ Enabled Block Public Access on S3 '{label}'")
                if not config.get("versioning"):
                    config["versioning"] = True
                    changes.append(f"✅ Enabled versioning on S3 '{label}'")
                if not config.get("https_only"):
                    config["https_only"] = True
                    changes.append(f"✅ Enforced HTTPS-only access on S3 '{label}'")

            elif t == "database":
                if not config.get("encryption"):
                    config["encryption"] = "KMS"
                    config["kms_encryption"] = True
                    changes.append(f"✅ Enabled KMS encryption for DynamoDB '{label}'")
                if not config.get("pitr"):
                    config["pitr"] = True
                    changes.append(f"✅ Enabled Point-in-Time Recovery for DynamoDB '{label}'")

            elif t == "lambda":
                if not config.get("vpc_enabled"):
                    config["vpc_enabled"] = True
                    config["vpc_subnets"] = "private"
                    changes.append(f"✅ Added VPC configuration for Lambda '{label}'")
                if not config.get("tracing"):
                    config["tracing"] = "Active"
                    changes.append(f"✅ Enabled X-Ray tracing for Lambda '{label}'")

            elif t == "api":
                if config.get("cors_origins") in (None, "*", "ALL_ORIGINS"):
                    config["cors_origins"] = "cloudfront-only"
                    changes.append(f"✅ Restricted CORS to CloudFront domain on API Gateway '{label}'")
                if not config.get("waf_enabled"):
                    config["waf_enabled"] = True
                    changes.append(f"✅ Attached WAF WebACL to API Gateway '{label}'")
                if not config.get("throttling"):
                    config["throttling"] = True
                    changes.append(f"✅ Enabled throttling on API Gateway '{label}'")
                if not config.get("access_logging"):
                    config["access_logging"] = True
                    changes.append(f"✅ Enabled access logging on API Gateway '{label}'")

            elif t == "queue":
                if not config.get("has_dlq"):
                    config["has_dlq"] = True
                    changes.append(f"✅ Enabled DLQ for queue '{label}'")
                if not config.get("encryption"):
                    config["encryption"] = "KMS"
                    changes.append(f"✅ Enabled KMS encryption for SQS queue '{label}'")

            elif t == "sns":
                if not config.get("encryption"):
                    config["encryption"] = "KMS"
                    changes.append(f"✅ Enabled KMS encryption for SNS topic '{label}'")
                if not config.get("access_policy"):
                    config["access_policy"] = "restricted"
                    changes.append(f"✅ Added restricted access policy for SNS topic '{label}'")

            elif t == "cdn":
                if not config.get("security_headers"):
                    config["security_headers"] = True
                    config["security_headers_policy"] = "CORS-and-SecurityHeadersPolicy"
                    changes.append(f"✅ Added security headers (CSP, HSTS, X-Frame-Options) to CloudFront '{label}'")
                if not config.get("waf_enabled"):
                    config["waf_enabled"] = True
                    changes.append(f"✅ Attached WAF to CloudFront '{label}'")

            elif t == "auth":
                if config.get("mfa") != "REQUIRED":
                    config["mfa"] = "REQUIRED"
                    config["advanced_security"] = "ENFORCED"
                    changes.append(f"✅ Enforced MFA and advanced security on Cognito '{label}'")

            elif t == "glue":
                if not config.get("encryption"):
                    config["encryption"] = True
                    changes.append(f"✅ Enabled encryption for Glue Data Catalog '{label}'")
                if not config.get("access_control"):
                    config["access_control"] = "restricted"
                    changes.append(f"✅ Added resource-based access policy for Glue '{label}'")

            elif t == "events":
                if not config.get("resource_policy"):
                    config["resource_policy"] = "restricted"
                    changes.append(f"✅ Added resource policy for EventBridge '{label}'")

        return {"nodes": nodes, "edges": edges}, changes

    def _add_auth_node(self, nodes: List, edges: List) -> Tuple[Dict, List[Dict]]:
        """Add Cognito auth node and connect to APIs."""
        # Find next available position
        max_x = max((n.get("position", {}).get("x", 0) for n in nodes), default=0)

        auth_node = {
            "id": f"auth-{len(nodes) + 1}",
            "type": "auth",
            "position": {"x": 50, "y": 50},
            "data": {
                "type": "auth",
                "label": "Cognito Auth",
                "config": {"mfa": "OPTIONAL", "password_policy": "STRONG"},
            },
        }

        # Connect auth to all APIs
        new_edges = []
        api_nodes = [n for n in nodes if n.get("data", {}).get("type") == "api"]
        for api in api_nodes:
            new_edges.append(
                {
                    "id": f"e-{auth_node['id']}-{api['id']}",
                    "source": auth_node["id"],
                    "target": api["id"],
                    "label": "authenticates",
                }
            )

        return auth_node, new_edges

    def get_security_score(self, graph: Dict) -> Dict:
        """Calculate security score for architecture."""
        nodes = graph.get("nodes", [])

        if not nodes:
            return {"score": 0, "max_score": 0, "percentage": 0}

        score = 0
        max_score = 0

        # Auth (20 points)
        max_score += 20
        has_auth = any(_resolve_type(n) == "auth" for n in nodes)
        has_api = any(_resolve_type(n) == "api" for n in nodes)
        if has_api and has_auth:
            score += 20
        elif not has_api:
            score += 20

        # KMS encryption on storage/db (20 points)
        max_score += 20
        storage_db = [n for n in nodes if _resolve_type(n) in ["storage", "database"]]
        if storage_db:
            kms = sum(1 for n in storage_db if n.get("data", {}).get("config", {}).get("encryption") in (True, "KMS"))
            score += int((kms / len(storage_db)) * 20)
        else:
            score += 20

        # Block public access on S3 (15 points)
        max_score += 15
        storage_nodes = [n for n in nodes if _resolve_type(n) == "storage"]
        if storage_nodes:
            secured = sum(1 for n in storage_nodes if n.get("data", {}).get("config", {}).get("block_public_access"))
            score += int((secured / len(storage_nodes)) * 15)
        else:
            score += 15

        # Lambda VPC (15 points)
        max_score += 15
        lambda_nodes = [n for n in nodes if _resolve_type(n) == "lambda"]
        if lambda_nodes:
            in_vpc = sum(1 for n in lambda_nodes if n.get("data", {}).get("config", {}).get("vpc_enabled"))
            score += int((in_vpc / len(lambda_nodes)) * 15)
        else:
            score += 15

        # DLQ on queues (10 points)
        max_score += 10
        queue_nodes = [n for n in nodes if _resolve_type(n) == "queue"]
        if queue_nodes:
            with_dlq = sum(1 for n in queue_nodes if n.get("data", {}).get("config", {}).get("has_dlq"))
            score += int((with_dlq / len(queue_nodes)) * 10)
        else:
            score += 10

        # WAF on API Gateway (10 points)
        max_score += 10
        api_nodes = [n for n in nodes if _resolve_type(n) == "api"]
        if api_nodes:
            with_waf = sum(1 for n in api_nodes if n.get("data", {}).get("config", {}).get("waf_enabled"))
            score += int((with_waf / len(api_nodes)) * 10)
        else:
            score += 10

        # PITR on DynamoDB (10 points)
        max_score += 10
        db_nodes = [n for n in nodes if _resolve_type(n) == "database"]
        if db_nodes:
            with_pitr = sum(1 for n in db_nodes if n.get("data", {}).get("config", {}).get("pitr"))
            score += int((with_pitr / len(db_nodes)) * 10)
        else:
            score += 10

        percentage = int((score / max_score) * 100) if max_score > 0 else 0

        return {"score": score, "max_score": max_score, "percentage": percentage}
