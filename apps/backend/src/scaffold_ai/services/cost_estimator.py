"""Cost estimation service for AWS architectures."""

from typing import Dict, List


class CostEstimator:
    """Estimate monthly costs for AWS architectures."""

    # Monthly cost estimates (USD) - conservative estimates for typical usage
    BASE_COSTS = {
        "lambda": {
            "base": 0.20,  # Per million requests
            "compute": 0.0000166667,  # Per GB-second
            "typical_monthly": 5.00,  # Typical small app
        },
        "api": {
            "base": 3.50,  # API Gateway per million requests
            "typical_monthly": 10.00,
        },
        "database": {
            "base": 1.25,  # DynamoDB on-demand per million read/write
            "storage": 0.25,  # Per GB/month
            "typical_monthly": 15.00,
        },
        "storage": {
            "storage": 0.023,  # S3 Standard per GB/month
            "requests": 0.005,  # Per 1000 PUT requests
            "typical_monthly": 5.00,
        },
        "auth": {
            "mau": 0.0055,  # Cognito per MAU (Monthly Active User)
            "typical_monthly": 10.00,  # ~1800 MAU
        },
        "queue": {
            "requests": 0.40,  # SQS per million requests
            "typical_monthly": 2.00,
        },
        "notification": {
            "requests": 0.50,  # SNS per million requests
            "typical_monthly": 2.00,
        },
        "events": {
            "requests": 1.00,  # EventBridge per million events
            "typical_monthly": 3.00,
        },
        "workflow": {
            "transitions": 0.025,  # Step Functions per 1000 transitions
            "typical_monthly": 10.00,
        },
        "stream": {
            "shard_hour": 0.015,  # Kinesis per shard-hour
            "typical_monthly": 11.00,  # 1 shard
        },
        "cdn": {
            "data_transfer": 0.085,  # CloudFront per GB
            "requests": 0.0075,  # Per 10,000 requests
            "typical_monthly": 15.00,
        },
        "frontend": {
            "hosting": 0.50,  # S3 + CloudFront
            "typical_monthly": 5.00,
        },
    }

    def estimate(self, graph: Dict) -> Dict:
        """
        Estimate monthly cost for an architecture.
        
        Args:
            graph: Architecture graph with nodes and edges
            
        Returns:
            Dict with cost breakdown and total
        """
        nodes = graph.get("nodes", [])
        
        if not nodes:
            return {
                "total_monthly": 0,
                "breakdown": [],
                "assumptions": [],
                "disclaimer": "No services to estimate"
            }

        breakdown = []
        total = 0
        assumptions = [
            "Estimates based on typical small-to-medium application usage",
            "Actual costs vary based on traffic, data volume, and usage patterns",
            "Free tier benefits not included",
            "Costs are approximate and for planning purposes only"
        ]

        # Count service types
        service_counts = {}
        for node in nodes:
            service_type = node.get("data", {}).get("type")
            if service_type:
                service_counts[service_type] = service_counts.get(service_type, 0) + 1

        # Calculate costs
        for service_type, count in service_counts.items():
            if service_type in self.BASE_COSTS:
                cost_info = self.BASE_COSTS[service_type]
                monthly_cost = cost_info["typical_monthly"] * count
                
                breakdown.append({
                    "service": self._service_name(service_type),
                    "count": count,
                    "monthly_cost": monthly_cost,
                    "details": self._get_cost_details(service_type, count)
                })
                
                total += monthly_cost

        # Add data transfer costs (rough estimate)
        if len(nodes) > 3:
            data_transfer = 5.00  # Base data transfer between services
            breakdown.append({
                "service": "Data Transfer",
                "count": 1,
                "monthly_cost": data_transfer,
                "details": "Inter-service data transfer (estimated)"
            })
            total += data_transfer

        return {
            "total_monthly": round(total, 2),
            "breakdown": breakdown,
            "assumptions": assumptions,
            "disclaimer": "These are estimates only. Actual AWS costs may vary significantly based on usage patterns, data volume, and region. Always use AWS Pricing Calculator for detailed estimates."
        }

    def _service_name(self, service_type: str) -> str:
        """Get friendly service name."""
        names = {
            "lambda": "AWS Lambda",
            "api": "API Gateway",
            "database": "DynamoDB",
            "storage": "S3",
            "auth": "Cognito",
            "queue": "SQS",
            "notification": "SNS",
            "events": "EventBridge",
            "workflow": "Step Functions",
            "stream": "Kinesis",
            "cdn": "CloudFront",
            "frontend": "S3 + CloudFront"
        }
        return names.get(service_type, service_type.title())

    def _get_cost_details(self, service_type: str, count: int) -> str:
        """Get cost breakdown details."""
        details = {
            "lambda": f"{count} function(s) with typical invocation patterns",
            "api": f"{count} API(s) with ~100K requests/month each",
            "database": f"{count} table(s) with on-demand billing",
            "storage": f"{count} bucket(s) with ~100GB storage each",
            "auth": f"{count} user pool(s) with ~1800 MAU each",
            "queue": f"{count} queue(s) with typical message volume",
            "notification": f"{count} topic(s) with typical notification volume",
            "events": f"{count} event bus(es) with typical event volume",
            "workflow": f"{count} state machine(s) with typical executions",
            "stream": f"{count} stream(s) with 1 shard each",
            "cdn": f"{count} distribution(s) with typical traffic",
            "frontend": f"{count} frontend(s) with static hosting"
        }
        return details.get(service_type, f"{count} instance(s)")

    def get_optimization_tips(self, graph: Dict) -> List[str]:
        """Get cost optimization recommendations."""
        nodes = graph.get("nodes", [])
        tips = []

        service_types = {node.get("data", {}).get("type") for node in nodes}

        if "lambda" in service_types:
            tips.append("💡 Use Lambda reserved concurrency to control costs")
            tips.append("💡 Optimize Lambda memory settings for cost/performance balance")

        if "database" in service_types:
            tips.append("💡 Consider DynamoDB reserved capacity for predictable workloads")
            tips.append("💡 Use DynamoDB TTL to automatically delete old data")

        if "storage" in service_types:
            tips.append("💡 Use S3 Intelligent-Tiering for automatic cost optimization")
            tips.append("💡 Set lifecycle policies to move old data to cheaper storage classes")

        if "api" in service_types:
            tips.append("💡 Enable API Gateway caching to reduce backend calls")

        if "stream" in service_types:
            tips.append("💡 Right-size Kinesis shards based on actual throughput")

        if len(nodes) > 5:
            tips.append("💡 Use AWS Cost Explorer to track actual spending")
            tips.append("💡 Set up AWS Budgets alerts for cost monitoring")

        return tips
