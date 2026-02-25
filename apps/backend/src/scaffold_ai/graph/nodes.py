"""LangGraph node functions for the workflow."""

import os
import json
import pathlib
import logging
from functools import lru_cache
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

from .state import GraphState, Intent
from ..agents.security_specialist import SecuritySpecialistAgent

logger = logging.getLogger(__name__)


# Initialize Bedrock client (singleton)
@lru_cache(maxsize=1)
def get_llm():
    """Get the Bedrock LLM client (cached singleton)."""
    return ChatBedrock(
        model_id=os.getenv(
            "BEDROCK_MODEL_ID", "us.anthropic.claude-opus-4-5-20251101-v1:0"
        ),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"temperature": 0.7, "max_tokens": 16384},
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

IMPORTANT: Each node may have a "config" object inside "data". Treat these config flags as already applied:
- config.encryption = "KMS" → KMS encryption is enabled
- config.block_public_access = true → S3 public access is blocked
- config.versioning = true → S3 versioning is enabled
- config.https_only = true → HTTPS-only bucket policy is applied
- config.pitr = true → DynamoDB PITR is enabled
- config.vpc_enabled = true → Lambda is deployed in a VPC
- config.tracing = "Active" → X-Ray tracing is enabled
- config.waf_enabled = true → WAF is attached
- config.has_dlq = true → Dead Letter Queue is configured
- config.mfa = "REQUIRED" → MFA is enforced
- config.advanced_security = "ENFORCED" → Cognito advanced security is on
- config.security_headers = true → CloudFront security headers are configured
- config.throttling = true → API Gateway throttling is enabled
- config.access_logging = true → API Gateway access logging is enabled
- config.resource_policy = "restricted" → EventBridge resource policy is set
- config.access_policy = "restricted" → SNS access policy is set
- config.access_control = "restricted" → Glue access control is configured

Do NOT flag issues for config properties that are already set as above.

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

        positioned_nodes.append(
            {
                "id": node["id"],
                "type": node_type,
                "position": {
                    "x": START_X + col * COLUMN_WIDTH,
                    "y": START_Y + row * ROW_HEIGHT,
                },
                "data": {
                    "label": node.get("label", "Component"),
                    "type": node_type,
                    "description": node.get("description", ""),
                },
            }
        )

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
        logger.warning(f"LLM intent classification failed: {e}")
        user_input = state["user_input"].lower()
        if any(
            word in user_input
            for word in ["generate", "code", "deploy", "build", "cdk"]
        ):
            intent = "generate_code"
        elif any(
            word in user_input
            for word in ["explain", "what is", "how does", "describe"]
        ):
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
            current_nodes_summary = json.dumps(
                [
                    {
                        "id": n["id"],
                        "type": n.get("data", {}).get("type"),
                        "label": n.get("data", {}).get("label"),
                    }
                    for n in current_graph["nodes"]
                ],
                indent=2,
            )

        prompt = ARCHITECT_PROMPT.format(
            current_graph=current_nodes_summary,
            user_input=state["user_input"],
        )

        messages = [
            SystemMessage(
                content="You are an AWS solutions architect. Always respond with valid JSON only."
            ),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        from scaffold_ai.utils.llm_utils import strip_code_fences

        response_text = strip_code_fences(response_text)

        result = json.loads(response_text)

        existing_nodes = current_graph.get("nodes", [])
        existing_edges = current_graph.get("edges", [])
        existing_node_ids = {n["id"] for n in existing_nodes}

        new_nodes = result.get("nodes", [])
        positioned_new_nodes = generate_node_positions(new_nodes, existing_nodes)
        positioned_new_nodes = [
            n for n in positioned_new_nodes if n["id"] not in existing_node_ids
        ]

        all_nodes = existing_nodes + positioned_new_nodes

        new_edges = []
        for edge in result.get("edges", []):
            edge_id = f"e-{edge['source']}-{edge['target']}"
            new_edges.append(
                {
                    "id": edge_id,
                    "source": edge["source"],
                    "target": edge["target"],
                    "label": edge.get("label", ""),
                }
            )

        existing_edge_ids = {e["id"] for e in existing_edges}
        new_edges = [e for e in new_edges if e["id"] not in existing_edge_ids]
        all_edges = existing_edges + new_edges

        updated_graph = {
            "nodes": all_nodes,
            "edges": all_edges,
        }

        explanation = result.get(
            "explanation", "I've updated your architecture based on your requirements."
        )

        return {
            **state,
            "graph_json": updated_graph,
            "response": explanation,
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {
            **state,
            "response": "I understood your request but had trouble generating the architecture. Could you try rephrasing it?",
        }
    except Exception as e:
        logger.exception(f"LLM architect call failed: {e}")
        return {
            **state,
            "response": "I encountered an error while designing the architecture. Please try again.",
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
        logger.exception(f"Explain failed: {e}")
        node_list = ", ".join(
            [n.get("data", {}).get("label", "Unknown") for n in nodes]
        )
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
            SystemMessage(
                content="You are an AWS security specialist. Respond with JSON only."
            ),
            HumanMessage(content=prompt),
        ]
        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        from scaffold_ai.utils.llm_utils import strip_code_fences

        response_text = strip_code_fences(response_text)

        review_result = json.loads(response_text)

    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(
            f"Security review LLM failed, using fallback: {e}"
        )
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
                response_parts.append(
                    f"- {w.get('service', 'Unknown')}: {w.get('issue', 'Unknown issue')}"
                )
        if recommendations:
            response_parts.append("")
            response_parts.append("**Recommendations:**")
            for r in recommendations[:3]:
                response_parts.append(
                    f"- {r.get('service', 'Unknown')}: {r.get('recommendation', 'Unknown')}"
                )
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
                response_parts.append(
                    f"- {c.get('service', 'Unknown')}: {c.get('issue', 'Unknown issue')}"
                )
                response_parts.append(f"  Fix: {c.get('recommendation', 'Unknown')}")
        if warnings:
            response_parts.append("")
            response_parts.append("**Warnings:**")
            for w in warnings[:5]:
                response_parts.append(
                    f"- {w.get('service', 'Unknown')}: {w.get('issue', 'Unknown issue')}"
                )
        response_parts.append("")
        response_parts.append("Please address these issues and try again.")

    return {
        **state,
        "security_review": review_result,
        "response": "\n".join(response_parts),
    }


def security_gate(state: GraphState) -> str:
    """Router function to determine if security review passed."""
    if state.get("skip_security"):
        return "passed"
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
    edges = graph.get("edges", [])
    security_review = state.get("security_review", {})
    iac_format = state.get("iac_format", "cdk")

    if not nodes:
        return {
            **state,
            "response": "No components in your architecture yet.",
        }

    # Build security requirements from review
    security_requirements = []
    for change in security_review.get("security_enhancements", {}).get(
        "config_changes", []
    ):
        security_requirements.append(
            f"Node {change['node_id']}: Apply {change['changes']}"
        )
    for rec in security_review.get("recommendations", []):
        security_requirements.append(
            f"{rec.get('service', 'General')}: {rec.get('recommendation', '')}"
        )

    # Check if we should split into multiple stacks
    from scaffold_ai.services.stack_splitter import StackSplitter

    splitter = StackSplitter()
    use_nested_stacks = splitter.should_split(nodes)

    try:
        if iac_format == "cloudformation":
            from scaffold_ai.agents.cloudformation_specialist import (
                CloudFormationSpecialistAgent,
            )

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
        elif iac_format == "python-cdk":
            from scaffold_ai.agents.python_cdk_specialist import PythonCDKSpecialist

            specialist = PythonCDKSpecialist()
            code = specialist.generate_stack(nodes, graph.get("edges", []))
            file_path = "packages/generated/infrastructure/mystack_stack.py"
            format_name = "Python CDK"

            # Also generate app.py and requirements.txt
            app_file = {
                "path": "packages/generated/infrastructure/app.py",
                "content": specialist.generate_app(),
            }
            req_file = {
                "path": "packages/generated/infrastructure/requirements.txt",
                "content": specialist.generate_requirements(),
            }
            generated_files = list(state.get("generated_files", []))
            generated_files.extend([app_file, req_file])
            _write_generated_file(app_file)
            _write_generated_file(req_file)
        else:  # cdk (default)
            # Check if we should use nested stacks
            if use_nested_stacks and iac_format == "cdk":
                stacks = splitter.split_by_layer(nodes, edges)
                nested_files = splitter.generate_nested_stack_code(stacks, "cdk")

                generated_files = list(state.get("generated_files", []))
                generated_files.extend(nested_files)

                for file in nested_files:
                    _write_generated_file(file)

                final_response = f"**Multi-Stack CDK Code Generated!**\n\nYour architecture has been split into {len(stacks)} nested stacks: {', '.join(stacks.keys())}. This improves organization and deployment speed."

                return {
                    **state,
                    "generated_files": generated_files,
                    "response": final_response,
                }

            llm = get_llm()
            prompt = CDK_GENERATOR_PROMPT.format(
                graph_json=json.dumps(graph, indent=2),
                security_requirements="\n".join(security_requirements)
                if security_requirements
                else "Standard security best practices",
            )
            messages = [
                SystemMessage(
                    content="You are an AWS CDK expert. Output only valid TypeScript code with security best practices."
                ),
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
        logger.exception(f"IaC generation failed: {e}")
        code = generate_secure_cdk_template(nodes, security_review)
        file_path = "packages/generated/infrastructure/lib/scaffold-ai-stack.ts"
        format_name = "CDK"

    generated_files = list(state.get("generated_files", []))
    new_file = {"path": file_path, "content": code.strip()}
    generated_files.append(new_file)

    # Persist to disk relative to the repo root (best-effort)
    _write_generated_file(new_file)

    security_response = state.get("response", "")
    final_response = f"{security_response}\n\n**{format_name} Code Generated!**\n\nThe AWS infrastructure code has been generated with security best practices applied. The code is saved to `{file_path}`."

    return {
        **state,
        "generated_files": generated_files,
        "response": final_response,
    }


def _write_generated_file(file: dict) -> None:
    """Write a generated file to disk under the repo root (best-effort)."""
    try:
        # Resolve repo root once using a known anchor: apps/backend is 2 levels below repo root
        repo_root = pathlib.Path(__file__).resolve().parents[4]  # src/scaffold_ai -> src -> backend -> apps -> repo root
        # Validate the anchor exists to catch unexpected working directories
        if not (repo_root / "apps").exists():
            logger.warning("Repo root anchor not found at %s, skipping file write", repo_root)
            return

        dest = repo_root / file["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(file["content"], encoding="utf-8")
        logger.info(f"Generated file written to {dest}")
    except Exception as e:
        logger.error(f"Could not write generated file to disk: {e}")


def generate_secure_cdk_template(nodes: list, security_review: dict) -> str:
    """Generate secure CDK code from nodes (fallback using unified generator)."""
    from scaffold_ai.services.cdk_generator import CDKGenerator

    generator = CDKGenerator()
    return generator.generate(nodes, [])


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
        logger.exception(f"React specialist failed: {e}")

    return state


def should_generate_code(state: GraphState) -> str:
    """Router function to determine if we should generate code."""
    if state["intent"] == "generate_code":
        return "generate"
    return "respond"
