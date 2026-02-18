"""Security auto-fix service for automatically improving architecture security."""

from typing import Dict, List, Tuple


class SecurityAutoFix:
    """Automatically add security improvements to architectures."""

    def analyze_and_fix(self, graph: Dict) -> Tuple[Dict, List[str]]:
        """
        Analyze architecture and automatically add security improvements.
        
        Returns:
            Tuple of (updated_graph, list_of_changes)
        """
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        changes = []

        if not nodes:
            return graph, changes

        # Check for missing auth
        has_auth = any(n.get("data", {}).get("type") == "auth" for n in nodes)
        has_api = any(n.get("data", {}).get("type") == "api" for n in nodes)
        
        if has_api and not has_auth:
            auth_node, auth_edges = self._add_auth_node(nodes, edges)
            nodes.append(auth_node)
            edges.extend(auth_edges)
            changes.append("✅ Added Cognito user pool for API authentication")

        # Check for missing monitoring
        has_lambda = any(n.get("data", {}).get("type") == "lambda" for n in nodes)
        
        # Check for DLQ on queues
        queue_nodes = [n for n in nodes if n.get("data", {}).get("type") == "queue"]
        for queue in queue_nodes:
            if not queue.get("data", {}).get("config", {}).get("has_dlq"):
                queue["data"]["config"] = queue["data"].get("config", {})
                queue["data"]["config"]["has_dlq"] = True
                changes.append(f"✅ Enabled DLQ for queue '{queue['data']['label']}'")

        # Check for encryption on storage
        storage_nodes = [n for n in nodes if n.get("data", {}).get("type") == "storage"]
        for storage in storage_nodes:
            config = storage.get("data", {}).get("config", {})
            if not config.get("encryption"):
                storage["data"]["config"] = config
                storage["data"]["config"]["encryption"] = "AES256"
                changes.append(f"✅ Enabled encryption for S3 bucket '{storage['data']['label']}'")

        # Check for encryption on databases
        db_nodes = [n for n in nodes if n.get("data", {}).get("type") == "database"]
        for db in db_nodes:
            config = db.get("data", {}).get("config", {})
            if not config.get("encryption"):
                db["data"]["config"] = config
                db["data"]["config"]["encryption"] = True
                changes.append(f"✅ Enabled encryption for DynamoDB table '{db['data']['label']}'")

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
                "config": {
                    "mfa": "OPTIONAL",
                    "password_policy": "STRONG"
                }
            }
        }

        # Connect auth to all APIs
        new_edges = []
        api_nodes = [n for n in nodes if n.get("data", {}).get("type") == "api"]
        for api in api_nodes:
            new_edges.append({
                "id": f"e-{auth_node['id']}-{api['id']}",
                "source": auth_node["id"],
                "target": api["id"],
                "label": "authenticates"
            })

        return auth_node, new_edges

    def get_security_score(self, graph: Dict) -> Dict:
        """Calculate security score for architecture."""
        nodes = graph.get("nodes", [])
        
        if not nodes:
            return {"score": 0, "max_score": 0, "percentage": 0}

        score = 0
        max_score = 0

        # Check for auth (25 points)
        max_score += 25
        has_auth = any(n.get("data", {}).get("type") == "auth" for n in nodes)
        has_api = any(n.get("data", {}).get("type") == "api" for n in nodes)
        if has_api and has_auth:
            score += 25
        elif not has_api:
            score += 25  # No API, so auth not needed

        # Check for encryption (25 points)
        max_score += 25
        storage_nodes = [n for n in nodes if n.get("data", {}).get("type") in ["storage", "database"]]
        if storage_nodes:
            encrypted = sum(1 for n in storage_nodes if n.get("data", {}).get("config", {}).get("encryption"))
            score += int((encrypted / len(storage_nodes)) * 25)
        else:
            score += 25

        # Check for DLQ on queues (15 points)
        max_score += 15
        queue_nodes = [n for n in nodes if n.get("data", {}).get("type") == "queue"]
        if queue_nodes:
            with_dlq = sum(1 for n in queue_nodes if n.get("data", {}).get("config", {}).get("has_dlq"))
            score += int((with_dlq / len(queue_nodes)) * 15)
        else:
            score += 15

        # Network security (15 points)
        max_score += 15
        vpc_nodes = [n for n in nodes if n.get("data", {}).get("config", {}).get("vpc_enabled")]
        if vpc_nodes:
            score += int((len(vpc_nodes) / len(nodes)) * 15)

        # Monitoring (20 points)
        max_score += 20
        monitored = [n for n in nodes if n.get("data", {}).get("config", {}).get("monitoring_enabled")]
        if monitored:
            score += int((len(monitored) / len(nodes)) * 20)

        percentage = int((score / max_score) * 100) if max_score > 0 else 0

        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage
        }
