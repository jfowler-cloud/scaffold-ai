"""Terraform Specialist agent for generating AWS infrastructure code."""

TERRAFORM_SYSTEM_PROMPT = """You are a Terraform expert. Convert architecture diagrams into Terraform HCL code.

## Best Practices

- Use AWS provider v5+
- Define variables for configurable values
- Use data sources for existing resources
- Add outputs for important values
- Use modules for reusable components

## Service Templates

### Lambda Function
```hcl
resource "aws_lambda_function" "main" {
  function_name = "my-function"
  runtime       = "nodejs20.x"
  handler       = "index.handler"
  filename      = "function.zip"
  role          = aws_iam_role.lambda.arn

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
    }
  }

  tracing_config {
    mode = "Active"
  }
}
```

### DynamoDB Table
```hcl
resource "aws_dynamodb_table" "main" {
  name         = "my-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }
}
```

Respond with valid Terraform HCL only."""


class TerraformSpecialistAgent:
    """Agent that generates Terraform configurations."""

    def __init__(self):
        """Initialize the Terraform specialist."""
        pass

    async def generate(self, graph: dict) -> str:
        """Generate Terraform configuration from graph."""
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        tf_code = []

        # Provider configuration
        tf_code.append(
            """terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
"""
        )

        # Generate resources
        for node in nodes:
            node_type = node.get("type")
            node_id = node.get("id", "").replace("-", "_")
            label = node.get("data", {}).get("label", node_type)

            slug = label.lower().replace(" ", "-")

            if node_type == "lambda":
                tf_code.append(
                    f"""
resource "aws_lambda_function" "{node_id}" {{
  function_name = "{slug}"
  runtime       = "nodejs20.x"
  handler       = "index.handler"
  filename      = "function.zip"
  role          = aws_iam_role.{node_id}_role.arn

  environment {{
    variables = {{
      POWERTOOLS_SERVICE_NAME = "{label}"
    }}
  }}

  tracing_config {{
    mode = "Active"
  }}
}}

resource "aws_iam_role" "{node_id}_role" {{
  name = "{slug}-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "lambda.amazonaws.com"
      }}
    }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "{node_id}_basic" {{
  role       = aws_iam_role.{node_id}_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}
"""
                )

            elif node_type == "database":
                tf_code.append(
                    f"""
resource "aws_dynamodb_table" "{node_id}" {{
  name         = "{slug}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {{
    name = "pk"
    type = "S"
  }}

  attribute {{
    name = "sk"
    type = "S"
  }}

  point_in_time_recovery {{
    enabled = true
  }}

  server_side_encryption {{
    enabled = true
  }}

  tags = {{
    Name = "{label}"
  }}
}}
"""
                )

            elif node_type == "api":
                tf_code.append(
                    f"""
resource "aws_apigatewayv2_api" "{node_id}" {{
  name          = "{slug}"
  protocol_type = "HTTP"
  description   = "{label}"
}}

resource "aws_apigatewayv2_stage" "{node_id}_stage" {{
  api_id      = aws_apigatewayv2_api.{node_id}.id
  name        = "prod"
  auto_deploy = true

  access_log_settings {{
    destination_arn = aws_cloudwatch_log_group.{node_id}_logs.arn
  }}
}}

resource "aws_cloudwatch_log_group" "{node_id}_logs" {{
  name              = "/aws/apigateway/{slug}"
  retention_in_days = 30
}}
"""
                )

            elif node_type == "auth":
                tf_code.append(
                    f"""
resource "aws_cognito_user_pool" "{node_id}" {{
  name = "{slug}"

  mfa_configuration = "OPTIONAL"

  password_policy {{
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }}

  account_recovery_setting {{
    recovery_mechanism {{
      name     = "verified_email"
      priority = 1
    }}
  }}
}}

resource "aws_cognito_user_pool_client" "{node_id}_client" {{
  name         = "{slug}-client"
  user_pool_id = aws_cognito_user_pool.{node_id}.id

  explicit_auth_flows = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
}}
"""
                )

            elif node_type == "storage":
                tf_code.append(
                    f"""
resource "aws_s3_bucket" "{node_id}" {{
  bucket = "{slug}"

  tags = {{
    Name = "{label}"
  }}
}}

resource "aws_s3_bucket_versioning" "{node_id}_versioning" {{
  bucket = aws_s3_bucket.{node_id}.id

  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "{node_id}_encryption" {{
  bucket = aws_s3_bucket.{node_id}.id

  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "{node_id}_public_access" {{
  bucket = aws_s3_bucket.{node_id}.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
"""
                )

            elif node_type == "queue":
                tf_code.append(
                    f"""
resource "aws_sqs_queue" "{node_id}_dlq" {{
  name                      = "{slug}-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled   = true
}}

resource "aws_sqs_queue" "{node_id}" {{
  name                    = "{slug}"
  sqs_managed_sse_enabled = true

  redrive_policy = jsonencode({{
    deadLetterTargetArn = aws_sqs_queue.{node_id}_dlq.arn
    maxReceiveCount     = 3
  }})

  tags = {{
    Name = "{label}"
  }}
}}
"""
                )

            elif node_type == "notification":
                tf_code.append(
                    f"""
resource "aws_sns_topic" "{node_id}" {{
  name         = "{slug}"
  display_name = "{label}"

  tags = {{
    Name = "{label}"
  }}
}}
"""
                )

            elif node_type == "events":
                tf_code.append(
                    f"""
resource "aws_cloudwatch_event_bus" "{node_id}" {{
  name = "{slug}-bus"

  tags = {{
    Name = "{label}"
  }}
}}
"""
                )

            elif node_type == "stream":
                tf_code.append(
                    f"""
resource "aws_kinesis_stream" "{node_id}" {{
  name             = "{slug}"
  stream_mode_details {{
    stream_mode = "ON_DEMAND"
  }}

  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"

  tags = {{
    Name = "{label}"
  }}
}}
"""
                )

            elif node_type == "workflow":
                tf_code.append(
                    f"""
resource "aws_sfn_state_machine" "{node_id}" {{
  name     = "{slug}"
  type     = "EXPRESS"
  role_arn = aws_iam_role.{node_id}_sfn_role.arn

  definition = jsonencode({{
    Comment = "{label}"
    StartAt = "Start"
    States = {{
      Start = {{
        Type = "Pass"
        End  = true
      }}
    }}
  }})

  logging_configuration {{
    log_destination        = "${{aws_cloudwatch_log_group.{node_id}_sfn_logs.arn}}:*"
    include_execution_data = true
    level                  = "ALL"
  }}

  tracing_configuration {{
    enabled = true
  }}
}}

resource "aws_cloudwatch_log_group" "{node_id}_sfn_logs" {{
  name              = "/aws/states/{slug}"
  retention_in_days = 30
}}

resource "aws_iam_role" "{node_id}_sfn_role" {{
  name = "{slug}-sfn-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "states.amazonaws.com"
      }}
    }}]
  }})
}}
"""
                )

        # Add outputs
        tf_code.append("\n# Outputs\n")
        for node in nodes:
            node_type = node.get("type")
            node_id = node.get("id", "").replace("-", "_")

            if node_type == "lambda":
                tf_code.append(
                    f"""
output "{node_id}_arn" {{
  value       = aws_lambda_function.{node_id}.arn
  description = "ARN of Lambda function"
}}
"""
                )
            elif node_type == "database":
                tf_code.append(
                    f"""
output "{node_id}_name" {{
  value       = aws_dynamodb_table.{node_id}.name
  description = "Name of DynamoDB table"
}}
"""
                )
            elif node_type == "api":
                tf_code.append(
                    f"""
output "{node_id}_endpoint" {{
  value       = aws_apigatewayv2_api.{node_id}.api_endpoint
  description = "API Gateway endpoint URL"
}}
"""
                )
            elif node_type == "storage":
                tf_code.append(
                    f"""
output "{node_id}_bucket" {{
  value       = aws_s3_bucket.{node_id}.bucket
  description = "S3 bucket name"
}}
"""
                )
            elif node_type == "auth":
                tf_code.append(
                    f"""
output "{node_id}_user_pool_id" {{
  value       = aws_cognito_user_pool.{node_id}.id
  description = "Cognito User Pool ID"
}}
"""
                )

        return "".join(tf_code)
