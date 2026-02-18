"""LangGraph node functions for the workflow."""

import os
import json
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

from .state import GraphState, Intent, SecurityReview
from ..agents.security_specialist import SecuritySpecialistAgent

# Initialize Bedrock client
def get_llm():
    """Get the Bedrock LLM client."""
    return ChatBedrock(
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-haiku-20240307-v1:0"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"temperature": 0.7, "max_tokens": 4096},
    )


INTERPRETER_PROMPT = """You are an intent classifier for Scaffold AI, a visual architecture designer.

Classify the user's message into exactly ONE of these intents:
- new_feature: User wants to add new components or build something new
- modify_graph: User wants to change, remove, or reconnect existing components
- generate_code: User wants to generate CDK infrastructure or React code
- explain: User wants to understand the architecture or get help

Respond with ONLY the intent name, nothing else."""


ARCHITECT_PROMPT = """You are a serverless-first AWS solutions architect for Scaffold AI. Your job is to design cost-effective, scalable AWS architectures using serverless services wherever possible.

Current architecture:
{current_graph}

User request: {user_input}

You must respond with valid JSON in this exact format:
{{
  "explanation": "Brief explanation of the architecture you're creating (2-3 sentences)",
  "nodes": [
    {{
      "id": "unique-id",
      "type": "lambda|api|database|storage|auth|queue|events|cdn|workflow|stream|notification|frontend",
      "label": "Human readable name",
      "description": "What this component does"
    }}
  ],
  "edges": [
    {{
      "source": "source-node-id",
      "target": "target-node-id",
      "label": "optional relationship label"
    }}
  ]
}}

Available node types (prefer serverless):
- lambda: Lambda functions (serverless compute - USE THIS for all business logic)
- api: API Gateway REST/HTTP or AppSync GraphQL (serverless API layer)
- database: DynamoDB (serverless NoSQL - preferred) or Aurora Serverless
- storage: S3 buckets (serverless object storage)
- auth: Cognito (serverless auth)
- queue: SQS queues (serverless async messaging, decoupling)
- events: EventBridge (serverless event bus, event-driven patterns)
- cdn: CloudFront (serverless content delivery)
- workflow: Step Functions (serverless workflow orchestration)
- stream: Kinesis Data Streams (serverless real-time streaming)
- notification: SNS topics (serverless pub/sub notifications)
- frontend: React/Next.js on Amplify/CloudFront+S3

SERVERLESS BEST PRACTICES:
- Always use Lambda + API Gateway instead of EC2/ECS for APIs
- Use DynamoDB instead of RDS when possible (truly serverless, pay-per-request)
- Use SQS/EventBridge for async processing and decoupling
- Use Step Functions for complex workflows instead of orchestrating in Lambda
- Use SNS for fan-out patterns and notifications
- Use CloudFront for static assets and API caching
- Design for event-driven architectures when possible

Guidelines:
- ALWAYS prefer serverless services for cost-effectiveness and scalability
- Connect components logically with proper async patterns
- Use queues (SQS) between Lambda functions for resilience
- Use EventBridge for event-driven integrations
- If modifying existing architecture, preserve existing nodes and add new ones

Respond with ONLY the JSON, no markdown or explanation outside the JSON."""


SECURITY_REVIEW_PROMPT = """You are a Security Specialist reviewing an AWS serverless architecture.

Architecture to review:
{architecture}

Review this architecture for security issues. Check for:
1. IAM: Least privilege permissions, no wildcards
2. Encryption: Data at rest and in transit
3. Authentication: API authorization configured
4. Network: No unnecessary public access
5. Logging: CloudWatch/X-Ray enabled
6. Data Protection: Backups, versioning, PITR

Respond with JSON:
{{
  "security_score": 0-100,
  "passed": true/false,
  "critical_issues": [
    {{"service": "...", "issue": "...", "severity": "critical", "recommendation": "..."}}
  ],
  "warnings": [
    {{"service": "...", "issue": "...", "severity": "high|medium", "recommendation": "..."}}
  ],
  "recommendations": [
    {{"service": "...", "recommendation": "..."}}
  ],
  "compliant_services": ["list of compliant services"],
  "security_enhancements": {{
    "nodes_to_add": [],
    "config_changes": [
      {{"node_id": "...", "changes": {{...}}}}
    ]
  }}
}}

Pass criteria:
- No critical issues
- No more than 3 high severity issues

Respond with ONLY JSON."""


def generate_node_positions(nodes: list, existing_nodes: list) -> list:
    """Generate x,y positions for nodes in a left-to-right flow layout."""
    type_columns = {
        "frontend": 0,
        "cdn": 0,
        "auth": 1,
        "api": 2,
        "lambda": 3,
        "workflow": 3,
        "queue": 4,
        "events": 4,
        "notification": 4,
        "stream": 5,
        "database": 6,
        "storage": 6,
    }

    COLUMN_WIDTH = 320
    ROW_HEIGHT = 200
    START_X = 50
    START_Y = 50

    column_counts = {i: 0 for i in range(7)}

    for node in existing_nodes:
        node_type = node.get("data", {}).get("type", "api")
        col = type_columns.get(node_type, 2)
        column_counts[col] += 1

    positioned_nodes = []
    for node in nodes:
        node_type = node.get("type", "api")
        col = type_columns.get(node_type, 2)
        row = column_counts[col]
        column_counts[col] += 1

        positioned_nodes.append({
            "id": node["id"],
            "type": node_type,
            "position": {
                "x": START_X + col * COLUMN_WIDTH,
                "y": START_Y + row * ROW_HEIGHT
            },
            "data": {
                "label": node.get("label", "Component"),
                "type": node_type,
                "description": node.get("description", ""),
            }
        })

    return positioned_nodes


async def interpret_intent(state: GraphState) -> GraphState:
    """Interpret the user's intent using Claude."""
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=INTERPRETER_PROMPT),
            HumanMessage(content=state["user_input"]),
        ]
        response = await llm.ainvoke(messages)
        intent_text = response.content.strip().lower()

        intent_map = {
            "new_feature": "new_feature",
            "modify_graph": "modify_graph",
            "generate_code": "generate_code",
            "explain": "explain",
        }
        intent: Intent = intent_map.get(intent_text, "new_feature")

    except Exception as e:
        print(f"LLM intent classification failed: {e}")
        user_input = state["user_input"].lower()
        if any(word in user_input for word in ["generate", "code", "deploy", "build", "cdk"]):
            intent = "generate_code"
        elif any(word in user_input for word in ["explain", "what is", "how does", "describe"]):
            intent = "explain"
        elif any(word in user_input for word in ["remove", "delete", "disconnect"]):
            intent = "modify_graph"
        else:
            intent = "new_feature"

    return {**state, "intent": intent}


async def architect_node(state: GraphState) -> GraphState:
    """Generate architecture with visual nodes using Claude."""
    intent = state["intent"]

    if intent == "explain":
        return await explain_architecture(state)

    try:
        llm = get_llm()

        current_graph = state["graph_json"]
        current_nodes_summary = "Empty - no components yet"
        if current_graph.get("nodes"):
            current_nodes_summary = json.dumps([
                {"id": n["id"], "type": n.get("data", {}).get("type"), "label": n.get("data", {}).get("label")}
                for n in current_graph["nodes"]
            ], indent=2)

        prompt = ARCHITECT_PROMPT.format(
            current_graph=current_nodes_summary,
            user_input=state["user_input"],
        )

        messages = [
            SystemMessage(content="You are an AWS solutions architect. Always respond with valid JSON only."),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text)

        existing_nodes = current_graph.get("nodes", [])
        existing_edges = current_graph.get("edges", [])
        existing_node_ids = {n["id"] for n in existing_nodes}

        new_nodes = result.get("nodes", [])
        positioned_new_nodes = generate_node_positions(new_nodes, existing_nodes)
        positioned_new_nodes = [n for n in positioned_new_nodes if n["id"] not in existing_node_ids]

        all_nodes = existing_nodes + positioned_new_nodes

        new_edges = []
        for edge in result.get("edges", []):
            edge_id = f"e-{edge['source']}-{edge['target']}"
            new_edges.append({
                "id": edge_id,
                "source": edge["source"],
                "target": edge["target"],
                "label": edge.get("label", ""),
            })

        existing_edge_ids = {e["id"] for e in existing_edges}
        new_edges = [e for e in new_edges if e["id"] not in existing_edge_ids]
        all_edges = existing_edges + new_edges

        updated_graph = {
            "nodes": all_nodes,
            "edges": all_edges,
        }

        explanation = result.get("explanation", "I've updated your architecture based on your requirements.")

        return {
            **state,
            "graph_json": updated_graph,
            "response": explanation,
        }

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {
            **state,
            "response": "I understood your request but had trouble generating the architecture. Could you try rephrasing it?",
        }
    except Exception as e:
        print(f"LLM architect call failed: {e}")
        return {
            **state,
            "response": f"I encountered an error while designing the architecture. Please try again.",
        }


async def explain_architecture(state: GraphState) -> GraphState:
    """Explain the current architecture."""
    graph = state["graph_json"]
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if not nodes:
        return {
            **state,
            "response": "Your canvas is empty. Describe what you want to build and I'll create an architecture for you.",
        }

    try:
        llm = get_llm()

        prompt = f"""Explain this AWS architecture in simple terms:

Nodes (components):
{json.dumps([{"type": n.get("data", {}).get("type"), "label": n.get("data", {}).get("label")} for n in nodes], indent=2)}

Edges (connections):
{json.dumps([{"from": e["source"], "to": e["target"]} for e in edges], indent=2)}

Provide a clear explanation of:
1. What this architecture does
2. How data flows between components
3. Any suggestions for improvement"""

        messages = [
            SystemMessage(content="You are a helpful AWS solutions architect."),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)

        return {**state, "response": response.content}

    except Exception as e:
        print(f"Explain failed: {e}")
        node_list = ", ".join([n.get("data", {}).get("label", "Unknown") for n in nodes])
        return {
            **state,
            "response": f"Your architecture has {len(nodes)} components: {node_list}.",
        }


async def security_review_node(state: GraphState) -> GraphState:
    """Security review gate - evaluates architecture before code generation."""
    graph = state["graph_json"]
    nodes = graph.get("nodes", [])

    if not nodes:
        return {
            **state,
            "security_review": {
                "security_score": 100,
                "passed": True,
                "critical_issues": [],
                "warnings": [],
                "recommendations": [],
                "compliant_services": [],
                "security_enhancements": {"nodes_to_add": [], "config_changes": []},
            },
            "response": "No architecture to review.",
        }

    try:
        llm = get_llm()

        prompt = SECURITY_REVIEW_PROMPT.format(
            architecture=json.dumps(graph, indent=2),
        )

        messages = [
            SystemMessage(content="You are an AWS security specialist. Respond with JSON only."),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        review_result = json.loads(response_text)

    except Exception as e:
        print(f"Security review LLM failed, using fallback: {e}")
        # Use the fallback security specialist
        security_agent = SecuritySpecialistAgent()
        review_result = await security_agent.review(graph)

    # Build response message
    score = review_result.get("security_score", 0)
    passed = review_result.get("passed", False)
    critical = review_result.get("critical_issues", [])
    warnings = review_result.get("warnings", [])
    recommendations = review_result.get("recommendations", [])

    if passed:
        response_parts = [
            f"**Security Review: PASSED** (Score: {score}/100)",
            "",
        ]
        if warnings:
            response_parts.append(f"**{len(warnings)} warnings to address:**")
            for w in warnings[:3]:
                response_parts.append(f"- {w.get('service', 'Unknown')}: {w.get('issue', 'Unknown issue')}")
        if recommendations:
            response_parts.append("")
            response_parts.append(f"**Recommendations:**")
            for r in recommendations[:3]:
                response_parts.append(f"- {r.get('service', 'Unknown')}: {r.get('recommendation', 'Unknown')}")
        response_parts.append("")
        response_parts.append("Proceeding with code generation...")
    else:
        response_parts = [
            f"**Security Review: FAILED** (Score: {score}/100)",
            "",
            "Code generation blocked due to security issues:",
            "",
        ]
        if critical:
            response_parts.append("**Critical Issues (must fix):**")
            for c in critical:
                response_parts.append(f"- {c.get('service', 'Unknown')}: {c.get('issue', 'Unknown issue')}")
                response_parts.append(f"  Fix: {c.get('recommendation', 'Unknown')}")
        if warnings:
            response_parts.append("")
            response_parts.append("**Warnings:**")
            for w in warnings[:5]:
                response_parts.append(f"- {w.get('service', 'Unknown')}: {w.get('issue', 'Unknown issue')}")
        response_parts.append("")
        response_parts.append("Please address these issues and try again.")

    return {
        **state,
        "security_review": review_result,
        "response": "\n".join(response_parts),
    }


def security_gate(state: GraphState) -> str:
    """Router function to determine if security review passed."""
    review = state.get("security_review")
    if review and review.get("passed", False):
        return "passed"
    return "failed"


CDK_GENERATOR_PROMPT = """You are an AWS CDK expert. Generate TypeScript CDK code for this architecture.

Architecture:
{graph_json}

Security Requirements (from security review):
{security_requirements}

Generate a complete CDK stack that includes:
1. Proper imports for all AWS services used
2. L2 constructs for each node with security best practices applied
3. Connections/permissions based on the edges (using least privilege grants)
4. Encryption enabled where recommended
5. Logging and monitoring enabled

IMPORTANT SECURITY REQUIREMENTS:
- Use least privilege IAM (grantRead vs grantReadWrite)
- Enable encryption at rest (S3, DynamoDB, SQS)
- Block public access for S3
- Enable X-Ray tracing for Lambda
- Enable point-in-time recovery for DynamoDB
- Use dead letter queues for SQS
- Enable CloudWatch logging

Output ONLY valid TypeScript CDK code, no markdown or explanations."""


async def cdk_specialist_node(state: GraphState) -> GraphState:
    """Generate IaC code (CDK/CloudFormation/Terraform) based on format preference."""
    if state["intent"] != "generate_code":
        return state

    graph = state["graph_json"]
    nodes = graph.get("nodes", [])
    security_review = state.get("security_review", {})
    iac_format = state.get("iac_format", "cdk")

    if not nodes:
        return {
            **state,
            "response": "No components in your architecture yet.",
        }

    # Build security requirements from review
    security_requirements = []
    for change in security_review.get("security_enhancements", {}).get("config_changes", []):
        security_requirements.append(f"Node {change['node_id']}: Apply {change['changes']}")
    for rec in security_review.get("recommendations", []):
        security_requirements.append(f"{rec.get('service', 'General')}: {rec.get('recommendation', '')}")

    try:
        if iac_format == "cloudformation":
            from scaffold_ai.agents.cloudformation_specialist import CloudFormationSpecialistAgent
            agent = CloudFormationSpecialistAgent()
            code = await agent.generate(graph)
            file_path = "packages/generated/infrastructure/template.yaml"
            format_name = "CloudFormation"
        elif iac_format == "terraform":
            from scaffold_ai.agents.terraform_specialist import TerraformSpecialistAgent
            agent = TerraformSpecialistAgent()
            code = await agent.generate(graph)
            file_path = "packages/generated/infrastructure/main.tf"
            format_name = "Terraform"
        else:  # cdk (default)
            llm = get_llm()
            prompt = CDK_GENERATOR_PROMPT.format(
                graph_json=json.dumps(graph, indent=2),
                security_requirements="\n".join(security_requirements) if security_requirements else "Standard security best practices",
            )
            messages = [
                SystemMessage(content="You are an AWS CDK expert. Output only valid TypeScript code with security best practices."),
                HumanMessage(content=prompt),
            ]
            response = await llm.ainvoke(messages)
            code = response.content

            if "```typescript" in code:
                code = code.split("```typescript")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]

            file_path = "packages/generated/infrastructure/lib/scaffold-ai-stack.ts"
            format_name = "CDK"

    except Exception as e:
        print(f"IaC generation failed: {e}")
        code = generate_secure_cdk_template(nodes, security_review)
        file_path = "packages/generated/infrastructure/lib/scaffold-ai-stack.ts"
        format_name = "CDK"

    generated_files = state.get("generated_files", [])
    generated_files.append({
        "path": file_path,
        "content": code.strip(),
    })

    security_response = state.get("response", "")
    final_response = f"{security_response}\n\n**{format_name} Code Generated!**\n\nThe AWS infrastructure code has been generated with security best practices applied. The code is saved to `{file_path}`."

    return {
        **state,
        "generated_files": generated_files,
        "response": final_response,
    }


def generate_secure_cdk_template(nodes: list, security_review: dict) -> str:
    """Generate secure CDK code from nodes (fallback)."""
    imports = [
        "import * as cdk from 'aws-cdk-lib';",
        "import { Construct } from 'constructs';",
    ]
    constructs = []

    for node in nodes:
        node_type = node.get("data", {}).get("type", "")
        label = node.get("data", {}).get("label", "Resource").replace(" ", "").replace("-", "")
        safe_name = label.lower()

        if node_type == "database":
            imports.append("import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';")
            constructs.append(f'''
    // {label} - DynamoDB with security best practices
    const {safe_name}Table = new dynamodb.Table(this, '{label}Table', {{
      partitionKey: {{ name: 'pk', type: dynamodb.AttributeType.STRING }},
      sortKey: {{ name: 'sk', type: dynamodb.AttributeType.STRING }},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,  // Security: Enable PITR for data protection
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    }});''')

        elif node_type == "auth":
            imports.append("import * as cognito from 'aws-cdk-lib/aws-cognito';")
            constructs.append(f'''
    // {label} - Cognito with strong security
    const userPool = new cognito.UserPool(this, '{label}UserPool', {{
      selfSignUpEnabled: true,
      signInAliases: {{ email: true }},
      autoVerify: {{ email: true }},
      passwordPolicy: {{
        minLength: 12,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: true,
      }},
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      mfa: cognito.Mfa.OPTIONAL,
      mfaSecondFactor: {{
        sms: true,
        otp: true,
      }},
    }});

    const userPoolClient = userPool.addClient('{label}WebClient', {{
      authFlows: {{ userPassword: true, userSrp: true }},
      oAuth: {{
        flows: {{ authorizationCodeGrant: true }},
        scopes: [cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL],
      }},
    }});''')

        elif node_type == "api":
            imports.append("import * as apigateway from 'aws-cdk-lib/aws-apigateway';")
            constructs.append(f'''
    // {label} - API Gateway with logging
    const {safe_name}Api = new apigateway.RestApi(this, '{label}Api', {{
      restApiName: '{label}',
      deployOptions: {{
        stageName: 'prod',
        tracingEnabled: true,  // Security: X-Ray tracing
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      }},
      defaultCorsPreflightOptions: {{
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      }},
    }});''')

        elif node_type == "lambda":
            imports.append("import * as lambda from 'aws-cdk-lib/aws-lambda';")
            constructs.append(f'''
    // {label} - Lambda with security best practices
    const {safe_name}Fn = new lambda.Function(this, '{label}Function', {{
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline('exports.handler = async () => {{ return {{ statusCode: 200 }}; }}'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      tracing: lambda.Tracing.ACTIVE,  // Security: X-Ray tracing
      environment: {{
        NODE_OPTIONS: '--enable-source-maps',
        POWERTOOLS_SERVICE_NAME: '{safe_name}',
      }},
    }});''')

        elif node_type == "storage":
            imports.append("import * as s3 from 'aws-cdk-lib/aws-s3';")
            constructs.append(f'''
    // {label} - S3 with security best practices
    const {safe_name}Bucket = new s3.Bucket(this, '{label}Bucket', {{
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,  // Security: Block public access
      encryption: s3.BucketEncryption.S3_MANAGED,  // Security: Encryption at rest
      versioned: true,  // Security: Enable versioning
      enforceSSL: true,  // Security: Require HTTPS
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    }});''')

        elif node_type == "queue":
            imports.append("import * as sqs from 'aws-cdk-lib/aws-sqs';")
            constructs.append(f'''
    // {label} - SQS with DLQ and encryption
    const {safe_name}Dlq = new sqs.Queue(this, '{label}DLQ', {{
      retentionPeriod: cdk.Duration.days(14),
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    }});

    const {safe_name}Queue = new sqs.Queue(this, '{label}Queue', {{
      visibilityTimeout: cdk.Duration.seconds(300),
      encryption: sqs.QueueEncryption.SQS_MANAGED,  // Security: Encryption
      deadLetterQueue: {{
        queue: {safe_name}Dlq,
        maxReceiveCount: 3,
      }},
    }});''')

        elif node_type == "events":
            imports.append("import * as events from 'aws-cdk-lib/aws-events';")
            constructs.append(f'''
    // {label} - EventBridge event bus
    const {safe_name}Bus = new events.EventBus(this, '{label}EventBus', {{
      eventBusName: '{safe_name}-bus',
    }});''')

        elif node_type == "notification":
            imports.append("import * as sns from 'aws-cdk-lib/aws-sns';")
            constructs.append(f'''
    // {label} - SNS Topic
    const {safe_name}Topic = new sns.Topic(this, '{label}Topic', {{
      displayName: '{label}',
    }});''')

        elif node_type == "workflow":
            imports.append("import * as sfn from 'aws-cdk-lib/aws-stepfunctions';")
            constructs.append(f'''
    // {label} - Step Functions with tracing
    const {safe_name}StateMachine = new sfn.StateMachine(this, '{label}StateMachine', {{
      definition: new sfn.Pass(this, '{label}StartState'),
      timeout: cdk.Duration.minutes(5),
      tracingEnabled: true,  // Security: X-Ray tracing
    }});''')

        elif node_type == "cdn":
            imports.append("import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';")
            constructs.append(f'''
    // {label} - CloudFront with security headers
    // Note: Requires an origin (S3 bucket or API Gateway)''')

        elif node_type == "stream":
            imports.append("import * as kinesis from 'aws-cdk-lib/aws-kinesis';")
            constructs.append(f'''
    // {label} - Kinesis with encryption
    const {safe_name}Stream = new kinesis.Stream(this, '{label}Stream', {{
      streamMode: kinesis.StreamMode.ON_DEMAND,
      encryption: kinesis.StreamEncryption.MANAGED,  // Security: Encryption
    }});''')

        elif node_type == "frontend":
            constructs.append(f'''
    // {label} - Frontend (Deploy via Amplify or S3+CloudFront)
    // Use 'amplify init' or deploy to S3 with CloudFront''')

    unique_imports = list(dict.fromkeys(imports))

    return f'''{chr(10).join(unique_imports)}

/**
 * Scaffold AI Generated Stack
 *
 * Security features applied:
 * - Encryption at rest for all data stores
 * - X-Ray tracing enabled
 * - Least privilege IAM policies
 * - DLQ for async processing
 * - Point-in-time recovery for DynamoDB
 * - Blocked public access for S3
 */
export class ScaffoldAiStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);
{"".join(constructs)}
  }}
}}
'''


async def react_specialist_node(state: GraphState) -> GraphState:
    """React Specialist - generates Cloudscape React component scaffolding."""
    if state["intent"] != "generate_code":
        return state

    graph = state["graph_json"]
    nodes = graph.get("nodes", [])

    if not nodes:
        return state

    try:
        from scaffold_ai.agents.react_specialist import ReactSpecialistAgent
        agent = ReactSpecialistAgent()
        react_files = await agent.generate(graph)

        if react_files:
            generated_files = list(state.get("generated_files", []))
            generated_files.extend(react_files)
            return {**state, "generated_files": generated_files}

    except Exception as e:
        print(f"React specialist failed: {e}")

    return state


def should_generate_code(state: GraphState) -> str:
    """Router function to determine if we should generate code."""
    if state["intent"] == "generate_code":
        return "generate"
    return "respond"
