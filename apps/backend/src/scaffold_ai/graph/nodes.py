"""LangGraph node functions for the workflow."""

import os
import json
import uuid
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

from .state import GraphState, Intent

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


def generate_node_positions(nodes: list, existing_nodes: list) -> list:
    """Generate x,y positions for nodes in a left-to-right flow layout."""
    # Define column positions by node type (left to right flow)
    # Organized by typical data flow: frontend -> api -> compute -> data/events
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

    # Spacing configuration - wide spacing to avoid overlaps
    COLUMN_WIDTH = 320  # Horizontal spacing between columns
    ROW_HEIGHT = 200    # Vertical spacing between rows
    START_X = 50
    START_Y = 50

    # Track how many nodes are in each column
    column_counts = {i: 0 for i in range(7)}

    # Count existing nodes per column
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

        # Map response to valid intent
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

    # For explain intent, just describe the current architecture
    if intent == "explain":
        return await explain_architecture(state)

    # For new_feature or modify_graph, generate nodes
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

        # Parse JSON response
        # Handle potential markdown wrapping
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text)

        # Get existing nodes and edges
        existing_nodes = current_graph.get("nodes", [])
        existing_edges = current_graph.get("edges", [])
        existing_node_ids = {n["id"] for n in existing_nodes}

        # Process new nodes with positions
        new_nodes = result.get("nodes", [])
        positioned_new_nodes = generate_node_positions(new_nodes, existing_nodes)

        # Filter out nodes that already exist (by ID)
        positioned_new_nodes = [n for n in positioned_new_nodes if n["id"] not in existing_node_ids]

        # Combine with existing nodes
        all_nodes = existing_nodes + positioned_new_nodes

        # Process edges
        new_edges = []
        for edge in result.get("edges", []):
            edge_id = f"e-{edge['source']}-{edge['target']}"
            new_edges.append({
                "id": edge_id,
                "source": edge["source"],
                "target": edge["target"],
                "label": edge.get("label", ""),
            })

        # Combine edges (avoid duplicates)
        existing_edge_ids = {e["id"] for e in existing_edges}
        new_edges = [e for e in new_edges if e["id"] not in existing_edge_ids]
        all_edges = existing_edges + new_edges

        # Update graph
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
        print(f"Response was: {response_text[:500] if 'response_text' in dir() else 'N/A'}")
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
            "response": "Your canvas is empty. Describe what you want to build and I'll create an architecture for you. For example: 'Build a todo app with user authentication' or 'Create a file upload service with S3'.",
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
            SystemMessage(content="You are a helpful AWS solutions architect explaining architectures to developers."),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)

        return {**state, "response": response.content}

    except Exception as e:
        print(f"Explain failed: {e}")
        node_list = ", ".join([n.get("data", {}).get("label", "Unknown") for n in nodes])
        return {
            **state,
            "response": f"Your architecture has {len(nodes)} components: {node_list}. There are {len(edges)} connections between them.",
        }


CDK_GENERATOR_PROMPT = """You are an AWS CDK expert. Generate TypeScript CDK code for this architecture.

Architecture:
{graph_json}

Generate a complete CDK stack that includes:
1. Proper imports for all AWS services used
2. L2 constructs for each node
3. Connections/permissions based on the edges
4. Appropriate IAM policies

Output ONLY valid TypeScript CDK code, no markdown or explanations."""


async def cdk_specialist_node(state: GraphState) -> GraphState:
    """Generate CDK code using Claude."""
    if state["intent"] != "generate_code":
        return state

    graph = state["graph_json"]
    nodes = graph.get("nodes", [])

    if not nodes:
        return {
            **state,
            "response": "No components in your architecture yet. Describe what you want to build first, then ask me to generate the code.",
        }

    try:
        llm = get_llm()

        prompt = CDK_GENERATOR_PROMPT.format(
            graph_json=json.dumps(graph, indent=2),
        )

        messages = [
            SystemMessage(content="You are an AWS CDK expert. Output only valid TypeScript code."),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)
        cdk_code = response.content

        # Clean up code if wrapped in markdown
        if "```typescript" in cdk_code:
            cdk_code = cdk_code.split("```typescript")[1].split("```")[0]
        elif "```" in cdk_code:
            cdk_code = cdk_code.split("```")[1].split("```")[0]

    except Exception as e:
        print(f"LLM CDK generation failed: {e}")
        cdk_code = generate_cdk_template(nodes)

    generated_files = state.get("generated_files", [])
    generated_files.append({
        "path": "packages/generated/infrastructure/lib/scaffold-ai-stack.ts",
        "content": cdk_code.strip(),
    })

    return {
        **state,
        "generated_files": generated_files,
        "response": "I've generated the AWS CDK infrastructure code for your architecture. The code is ready for deployment.",
    }


def generate_cdk_template(nodes: list) -> str:
    """Generate basic CDK code from nodes (fallback)."""
    imports = ["import * as cdk from 'aws-cdk-lib';", "import { Construct } from 'constructs';"]
    constructs = []

    for node in nodes:
        node_type = node.get("data", {}).get("type", "")
        label = node.get("data", {}).get("label", "Resource").replace(" ", "").replace("-", "")

        if node_type == "database":
            imports.append("import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';")
            constructs.append(f'''
    // {label} - DynamoDB (Serverless, pay-per-request)
    new dynamodb.Table(this, '{label}Table', {{
      partitionKey: {{ name: 'id', type: dynamodb.AttributeType.STRING }},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    }});''')

        elif node_type == "auth":
            imports.append("import * as cognito from 'aws-cdk-lib/aws-cognito';")
            constructs.append(f'''
    // {label} - Cognito (Serverless auth)
    new cognito.UserPool(this, '{label}UserPool', {{
      selfSignUpEnabled: true,
      signInAliases: {{ email: true }},
      autoVerify: {{ email: true }},
    }});''')

        elif node_type == "api":
            imports.append("import * as apigateway from 'aws-cdk-lib/aws-apigateway';")
            constructs.append(f'''
    // {label} - API Gateway (Serverless)
    new apigateway.RestApi(this, '{label}Api', {{
      restApiName: '{label}',
      deployOptions: {{ stageName: 'prod' }},
    }});''')

        elif node_type == "lambda":
            imports.append("import * as lambda from 'aws-cdk-lib/aws-lambda';")
            constructs.append(f'''
    // {label} - Lambda (Serverless compute)
    new lambda.Function(this, '{label}Function', {{
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline('exports.handler = async () => {{ return {{ statusCode: 200 }}; }}'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    }});''')

        elif node_type == "storage":
            imports.append("import * as s3 from 'aws-cdk-lib/aws-s3';")
            constructs.append(f'''
    // {label} - S3 (Serverless storage)
    new s3.Bucket(this, '{label}Bucket', {{
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    }});''')

        elif node_type == "queue":
            imports.append("import * as sqs from 'aws-cdk-lib/aws-sqs';")
            constructs.append(f'''
    // {label} - SQS Queue (Serverless messaging)
    new sqs.Queue(this, '{label}Queue', {{
      visibilityTimeout: cdk.Duration.seconds(300),
    }});''')

        elif node_type == "events":
            imports.append("import * as events from 'aws-cdk-lib/aws-events';")
            constructs.append(f'''
    // {label} - EventBridge (Serverless event bus)
    new events.EventBus(this, '{label}EventBus', {{
      eventBusName: '{label.lower()}-bus',
    }});''')

        elif node_type == "notification":
            imports.append("import * as sns from 'aws-cdk-lib/aws-sns';")
            constructs.append(f'''
    // {label} - SNS Topic (Serverless notifications)
    new sns.Topic(this, '{label}Topic', {{
      displayName: '{label}',
    }});''')

        elif node_type == "workflow":
            imports.append("import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';")
            constructs.append(f'''
    // {label} - Step Functions (Serverless workflow)
    new stepfunctions.StateMachine(this, '{label}StateMachine', {{
      definition: new stepfunctions.Pass(this, '{label}StartState'),
    }});''')

        elif node_type == "cdn":
            imports.append("import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';")
            imports.append("import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';")
            constructs.append(f'''
    // {label} - CloudFront CDN (Serverless content delivery)
    // Note: Requires an origin (S3 bucket or API Gateway)''')

        elif node_type == "stream":
            imports.append("import * as kinesis from 'aws-cdk-lib/aws-kinesis';")
            constructs.append(f'''
    // {label} - Kinesis Stream (Serverless streaming)
    new kinesis.Stream(this, '{label}Stream', {{
      streamMode: kinesis.StreamMode.ON_DEMAND,
    }});''')

        elif node_type == "frontend":
            constructs.append(f'''
    // {label} - Frontend (Deploy to S3 + CloudFront or Amplify)
    // Use 'amplify init' or deploy static assets to S3''')

    unique_imports = list(dict.fromkeys(imports))

    return f'''{chr(10).join(unique_imports)}

export class ScaffoldAiStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);
{"".join(constructs)}
  }}
}}
'''


async def react_specialist_node(state: GraphState) -> GraphState:
    """React Specialist - generates React component code."""
    if state["intent"] != "generate_code":
        return state
    return state


def should_generate_code(state: GraphState) -> str:
    """Router function to determine if we should generate code."""
    if state["intent"] == "generate_code":
        return "generate"
    return "respond"
