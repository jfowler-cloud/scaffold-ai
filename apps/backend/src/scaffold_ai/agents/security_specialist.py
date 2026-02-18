"""Security Specialist agent for evaluating and enforcing AWS security best practices."""

SECURITY_SYSTEM_PROMPT = """You are a Security Specialist for Scaffold AI, responsible for reviewing AWS architectures and ensuring they follow security best practices before code is generated.

## Your Responsibilities

1. **Review architecture for security risks**
2. **Ensure least privilege IAM policies**
3. **Verify encryption at rest and in transit**
4. **Check for secure defaults**
5. **Identify compliance requirements**

## Security Checklist

### IAM & Access Control
- [ ] Lambda functions should only have permissions they need (grantRead vs grantReadWrite)
- [ ] No wildcard (*) permissions in IAM policies
- [ ] Use resource-based policies where possible
- [ ] API Gateway should have authorization (Cognito, IAM, or Lambda authorizer)
- [ ] S3 buckets should block public access by default
- [ ] DynamoDB should use IAM for access control

### Encryption
- [ ] S3 buckets: Server-side encryption enabled (SSE-S3 or SSE-KMS)
- [ ] DynamoDB: Encryption at rest (enabled by default, but verify KMS for sensitive data)
- [ ] SQS: Server-side encryption for sensitive queues
- [ ] SNS: Encryption for sensitive topics
- [ ] Kinesis: Encryption at rest
- [ ] All API traffic over HTTPS (API Gateway default)
- [ ] CloudFront: HTTPS only, TLS 1.2+

### Network Security
- [ ] Lambda in VPC only if accessing VPC resources (RDS, ElastiCache)
- [ ] Security groups: least privilege (no 0.0.0.0/0 ingress on sensitive ports)
- [ ] VPC endpoints for AWS services to avoid public internet

### Logging & Monitoring
- [ ] CloudTrail for API logging
- [ ] CloudWatch Logs for Lambda (automatic)
- [ ] X-Ray tracing for debugging
- [ ] API Gateway access logging
- [ ] S3 access logging for sensitive buckets

### Data Protection
- [ ] DynamoDB Point-in-time recovery for critical data
- [ ] S3 versioning for important buckets
- [ ] Backup policies for production data
- [ ] Data classification tags

### Secrets Management
- [ ] Use AWS Secrets Manager or Parameter Store for secrets
- [ ] Never hardcode credentials
- [ ] Rotate secrets regularly

## Security Recommendations by Service

### Lambda
```typescript
// Least privilege - grant specific permissions
table.grantReadData(lambdaFunction);  // Read-only if writes not needed
bucket.grantRead(lambdaFunction);      // Read-only access

// Enable X-Ray tracing
tracing: lambda.Tracing.ACTIVE

// Set reasonable timeouts
timeout: cdk.Duration.seconds(30)
```

### DynamoDB
```typescript
// Enable point-in-time recovery for critical tables
pointInTimeRecovery: true

// Use customer-managed KMS for sensitive data
encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED
encryptionKey: new kms.Key(this, 'TableKey')
```

### S3
```typescript
// Block public access
blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL

// Enable encryption
encryption: s3.BucketEncryption.S3_MANAGED

// Enable versioning for important data
versioned: true

// Enable access logging
serverAccessLogsBucket: accessLogsBucket
```

### API Gateway
```typescript
// Require authorization
defaultMethodOptions: {
  authorizationType: apigateway.AuthorizationType.COGNITO,
  authorizer: cognitoAuthorizer
}

// Enable CloudWatch logging
deployOptions: {
  loggingLevel: apigateway.MethodLoggingLevel.INFO,
  dataTraceEnabled: true,
  tracingEnabled: true
}
```

### SQS
```typescript
// Enable encryption
encryption: sqs.QueueEncryption.KMS

// Use dead letter queue
deadLetterQueue: {
  queue: dlq,
  maxReceiveCount: 3
}
```

### Cognito
```typescript
// Strong password policy
passwordPolicy: {
  minLength: 12,
  requireLowercase: true,
  requireUppercase: true,
  requireDigits: true,
  requireSymbols: true
}

// Enable MFA
mfa: cognito.Mfa.REQUIRED
mfaSecondFactor: {
  sms: true,
  otp: true
}

// Account recovery
accountRecovery: cognito.AccountRecovery.EMAIL_ONLY
```

## Response Format

When reviewing an architecture, respond with JSON:
```json
{
  "security_score": 85,
  "passed": true,
  "critical_issues": [],
  "warnings": [
    {
      "service": "S3",
      "issue": "Bucket 'uploads' should enable versioning for data protection",
      "severity": "medium",
      "recommendation": "Add 'versioned: true' to the bucket configuration"
    }
  ],
  "recommendations": [
    {
      "service": "Lambda",
      "recommendation": "Use grantReadData instead of grantReadWriteData for read-only operations"
    }
  ],
  "compliant_services": ["DynamoDB", "API Gateway", "Cognito"],
  "security_enhancements": {
    "nodes_to_add": [],
    "config_changes": [
      {
        "node_id": "storage-1",
        "changes": {
          "encryption": true,
          "versioning": true,
          "blockPublicAccess": true
        }
      }
    ]
  }
}
```

## Severity Levels

- **critical**: Must fix before deployment (public S3, no auth on API, hardcoded secrets)
- **high**: Should fix soon (overly permissive IAM, no encryption on sensitive data)
- **medium**: Recommended fix (missing logging, no backup strategy)
- **low**: Nice to have (additional monitoring, cost optimization)

## Pass/Fail Criteria

- **FAIL**: Any critical issues
- **FAIL**: More than 3 high severity issues
- **PASS with warnings**: Medium/low issues only
- **PASS**: No issues or only low severity

Your goal is to ensure all generated infrastructure follows AWS security best practices and would pass a security audit."""


class SecuritySpecialistAgent:
    """Agent that reviews architectures for security compliance before code generation."""

    def __init__(self):
        self.system_prompt = SECURITY_SYSTEM_PROMPT

    async def review(self, graph: dict) -> dict:
        """
        Review the architecture for security issues.

        In production, this would call Claude via AWS Bedrock.
        Returns security review results with recommendations.
        """
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        if not nodes:
            return {
                "security_score": 100,
                "passed": True,
                "critical_issues": [],
                "warnings": [],
                "recommendations": [],
                "compliant_services": [],
                "security_enhancements": {
                    "nodes_to_add": [],
                    "config_changes": [],
                },
            }

        # Basic static analysis (fallback when LLM unavailable)
        issues = []
        warnings = []
        recommendations = []
        config_changes = []

        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            node_id = node.get("id", "")
            label = node.get("data", {}).get("label", "")

            if node_type == "storage":
                # S3 security checks
                warnings.append(
                    {
                        "service": "S3",
                        "issue": f"Bucket '{label}' should have encryption, versioning, and block public access enabled",
                        "severity": "medium",
                        "recommendation": "Add blockPublicAccess: BLOCK_ALL, encryption: S3_MANAGED, versioned: true",
                    }
                )
                config_changes.append(
                    {
                        "node_id": node_id,
                        "changes": {
                            "blockPublicAccess": True,
                            "encryption": "S3_MANAGED",
                            "versioning": True,
                        },
                    }
                )

            elif node_type == "database":
                # DynamoDB security checks
                recommendations.append(
                    {
                        "service": "DynamoDB",
                        "recommendation": f"Enable point-in-time recovery for '{label}' table for data protection",
                    }
                )
                config_changes.append(
                    {
                        "node_id": node_id,
                        "changes": {
                            "pointInTimeRecovery": True,
                        },
                    }
                )

            elif node_type == "api":
                # API Gateway security checks
                has_auth = any(n.get("data", {}).get("type") == "auth" for n in nodes)
                if not has_auth:
                    warnings.append(
                        {
                            "service": "API Gateway",
                            "issue": f"API '{label}' has no authentication configured",
                            "severity": "high",
                            "recommendation": "Add Cognito, IAM, or Lambda authorizer for authentication",
                        }
                    )

            elif node_type == "lambda":
                # Lambda security checks
                recommendations.append(
                    {
                        "service": "Lambda",
                        "recommendation": f"Enable X-Ray tracing on '{label}' for debugging and monitoring",
                    }
                )
                recommendations.append(
                    {
                        "service": "Lambda",
                        "recommendation": f"Use least-privilege IAM grants (grantRead vs grantReadWrite) for '{label}'",
                    }
                )

            elif node_type == "queue":
                # SQS security checks
                warnings.append(
                    {
                        "service": "SQS",
                        "issue": f"Queue '{label}' should have encryption enabled for sensitive data",
                        "severity": "medium",
                        "recommendation": "Add encryption: sqs.QueueEncryption.KMS",
                    }
                )
                config_changes.append(
                    {
                        "node_id": node_id,
                        "changes": {
                            "encryption": "KMS",
                            "deadLetterQueue": True,
                        },
                    }
                )

            elif node_type == "auth":
                # Cognito security checks
                recommendations.append(
                    {
                        "service": "Cognito",
                        "recommendation": f"Consider enabling MFA for '{label}' user pool for enhanced security",
                    }
                )

        # Calculate security score
        critical_count = len([i for i in issues if i.get("severity") == "critical"])
        high_count = len([w for w in warnings if w.get("severity") == "high"])
        medium_count = len([w for w in warnings if w.get("severity") == "medium"])

        # Scoring: start at 100, deduct points
        score = 100 - (critical_count * 30) - (high_count * 15) - (medium_count * 5)
        score = max(0, min(100, score))

        # Determine pass/fail
        passed = critical_count == 0 and high_count <= 3

        return {
            "security_score": score,
            "passed": passed,
            "critical_issues": [i for i in issues if i.get("severity") == "critical"],
            "warnings": warnings,
            "recommendations": recommendations,
            "compliant_services": [],
            "security_enhancements": {
                "nodes_to_add": [],
                "config_changes": config_changes,
            },
        }
