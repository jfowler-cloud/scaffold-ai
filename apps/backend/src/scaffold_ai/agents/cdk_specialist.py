"""CDK Specialist agent for generating AWS infrastructure code."""

CDK_SYSTEM_PROMPT = """You are an AWS CDK expert for Scaffold AI. Your role is to convert visual architecture diagrams into working AWS CDK TypeScript code.

Given a graph of nodes and edges representing an architecture, generate:
1. CDK Stack definitions
2. Construct configurations for each service
3. IAM policies and roles
4. Environment-specific configurations

Follow AWS best practices:
- Use L2 constructs when available
- Implement least-privilege IAM policies
- Add appropriate tags for resource management
- Include outputs for important resource ARNs

The graph nodes contain:
- type: The AWS service type (database, auth, api, storage)
- label: Human-readable name
- config: Optional service-specific configuration

Generate clean, well-documented TypeScript CDK code."""


class CDKSpecialistAgent:
    """Agent that generates AWS CDK infrastructure code."""

    def __init__(self):
        self.system_prompt = CDK_SYSTEM_PROMPT

    async def generate(self, graph: dict) -> list[dict]:
        """
        Generate CDK code from the architecture graph.

        In production, this would call Claude via AWS Bedrock.
        Returns a list of generated files.
        """
        nodes = graph.get("nodes", [])

        if not nodes:
            return []

        # Generate placeholder stack
        stack_code = self._generate_stack(nodes)

        return [
            {
                "path": "packages/generated/infrastructure/lib/scaffold-ai-stack.ts",
                "content": stack_code,
            }
        ]

    def _generate_stack(self, nodes: list) -> str:
        """Generate a basic CDK stack from nodes."""
        imports = ["import * as cdk from 'aws-cdk-lib';", "import { Construct } from 'constructs';"]
        constructs = []

        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            label = node.get("data", {}).get("label", "Resource")

            if node_type == "database":
                imports.append("import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';")
                constructs.append(f'''
    // {label}
    const table = new dynamodb.Table(this, '{label.replace(" ", "")}Table', {{
      partitionKey: {{ name: 'id', type: dynamodb.AttributeType.STRING }},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    }});''')

            elif node_type == "auth":
                imports.append("import * as cognito from 'aws-cdk-lib/aws-cognito';")
                constructs.append(f'''
    // {label}
    const userPool = new cognito.UserPool(this, '{label.replace(" ", "")}UserPool', {{
      selfSignUpEnabled: true,
      signInAliases: {{ email: true }},
      autoVerify: {{ email: true }},
    }});''')

            elif node_type == "api":
                imports.append("import * as apigateway from 'aws-cdk-lib/aws-apigateway';")
                constructs.append(f'''
    // {label}
    const api = new apigateway.RestApi(this, '{label.replace(" ", "")}Api', {{
      restApiName: '{label}',
      deployOptions: {{ stageName: 'prod' }},
    }});''')

        unique_imports = list(dict.fromkeys(imports))

        return f'''{chr(10).join(unique_imports)}

export class ScaffoldAiStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);
{"".join(constructs)}
  }}
}}
'''
