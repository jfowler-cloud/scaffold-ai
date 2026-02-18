"""Architecture templates library with pre-built patterns."""

from typing import Dict, List


class ArchitectureTemplates:
    """Pre-built architecture templates for common patterns."""

    TEMPLATES = {
        "todo-app": {
            "name": "Todo App with Auth",
            "description": "Full-stack todo application with user authentication",
            "nodes": [
                {"id": "frontend-1", "data": {"type": "frontend", "label": "Web App"}},
                {"id": "auth-1", "data": {"type": "auth", "label": "User Auth"}},
                {"id": "api-1", "data": {"type": "api", "label": "REST API"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "API Handler"}},
                {"id": "db-1", "data": {"type": "database", "label": "Todos Table"}},
            ],
            "edges": [
                {"source": "frontend-1", "target": "api-1"},
                {"source": "auth-1", "target": "api-1"},
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "db-1"},
            ]
        },
        "file-upload": {
            "name": "File Upload Service",
            "description": "Secure file upload with S3 and processing pipeline",
            "nodes": [
                {"id": "frontend-1", "data": {"type": "frontend", "label": "Upload UI"}},
                {"id": "api-1", "data": {"type": "api", "label": "Upload API"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "Presigned URL"}},
                {"id": "storage-1", "data": {"type": "storage", "label": "Files Bucket"}},
                {"id": "lambda-2", "data": {"type": "lambda", "label": "Process File"}},
                {"id": "db-1", "data": {"type": "database", "label": "Metadata"}},
            ],
            "edges": [
                {"source": "frontend-1", "target": "api-1"},
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "storage-1"},
                {"source": "storage-1", "target": "lambda-2"},
                {"source": "lambda-2", "target": "db-1"},
            ]
        },
        "rest-api": {
            "name": "REST API with Database",
            "description": "Simple REST API backed by DynamoDB",
            "nodes": [
                {"id": "api-1", "data": {"type": "api", "label": "REST API"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "Handler"}},
                {"id": "db-1", "data": {"type": "database", "label": "Data Table"}},
            ],
            "edges": [
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "db-1"},
            ]
        },
        "event-driven": {
            "name": "Event-Driven Architecture",
            "description": "Microservices with EventBridge and async processing",
            "nodes": [
                {"id": "api-1", "data": {"type": "api", "label": "API"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "Publisher"}},
                {"id": "events-1", "data": {"type": "events", "label": "Event Bus"}},
                {"id": "lambda-2", "data": {"type": "lambda", "label": "Processor 1"}},
                {"id": "lambda-3", "data": {"type": "lambda", "label": "Processor 2"}},
                {"id": "db-1", "data": {"type": "database", "label": "Data Store"}},
            ],
            "edges": [
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "events-1"},
                {"source": "events-1", "target": "lambda-2"},
                {"source": "events-1", "target": "lambda-3"},
                {"source": "lambda-2", "target": "db-1"},
                {"source": "lambda-3", "target": "db-1"},
            ]
        },
        "queue-worker": {
            "name": "Queue-Based Worker",
            "description": "Async job processing with SQS and Lambda",
            "nodes": [
                {"id": "api-1", "data": {"type": "api", "label": "Job API"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "Enqueue"}},
                {"id": "queue-1", "data": {"type": "queue", "label": "Job Queue"}},
                {"id": "lambda-2", "data": {"type": "lambda", "label": "Worker"}},
                {"id": "db-1", "data": {"type": "database", "label": "Results"}},
            ],
            "edges": [
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "queue-1"},
                {"source": "queue-1", "target": "lambda-2"},
                {"source": "lambda-2", "target": "db-1"},
            ]
        },
        "saas-app": {
            "name": "Multi-Tenant SaaS",
            "description": "Complete SaaS application with auth and multi-tenancy",
            "nodes": [
                {"id": "frontend-1", "data": {"type": "frontend", "label": "SaaS UI"}},
                {"id": "cdn-1", "data": {"type": "cdn", "label": "CloudFront"}},
                {"id": "auth-1", "data": {"type": "auth", "label": "User Auth"}},
                {"id": "api-1", "data": {"type": "api", "label": "API Gateway"}},
                {"id": "lambda-1", "data": {"type": "lambda", "label": "Authorizer"}},
                {"id": "lambda-2", "data": {"type": "lambda", "label": "Business Logic"}},
                {"id": "db-1", "data": {"type": "database", "label": "Tenant Data"}},
                {"id": "storage-1", "data": {"type": "storage", "label": "Assets"}},
            ],
            "edges": [
                {"source": "frontend-1", "target": "cdn-1"},
                {"source": "cdn-1", "target": "api-1"},
                {"source": "auth-1", "target": "lambda-1"},
                {"source": "api-1", "target": "lambda-1"},
                {"source": "lambda-1", "target": "lambda-2"},
                {"source": "lambda-2", "target": "db-1"},
                {"source": "lambda-2", "target": "storage-1"},
            ]
        },
    }

    def list_templates(self) -> List[Dict]:
        """List all available templates."""
        return [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "node_count": len(template["nodes"]),
            }
            for template_id, template in self.TEMPLATES.items()
        ]

    def get_template(self, template_id: str) -> Dict:
        """Get a specific template by ID."""
        if template_id not in self.TEMPLATES:
            raise ValueError(f"Template '{template_id}' not found")

        template = self.TEMPLATES[template_id]
        
        # Add positions to nodes
        from ..graph.nodes import generate_node_positions
        nodes_with_positions = generate_node_positions(template["nodes"], [])

        return {
            "name": template["name"],
            "description": template["description"],
            "nodes": nodes_with_positions,
            "edges": [
                {
                    "id": f"e-{edge['source']}-{edge['target']}",
                    **edge
                }
                for edge in template["edges"]
            ]
        }
