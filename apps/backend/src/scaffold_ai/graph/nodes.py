"""LangGraph node functions for the workflow."""

from .state import GraphState, Intent


async def interpret_intent(state: GraphState) -> GraphState:
    """
    Interpret the user's intent from their message.

    This node analyzes the user input and determines what action to take:
    - new_feature: User wants to add something new to the architecture
    - modify_graph: User wants to change existing nodes/edges
    - generate_code: User wants to generate CDK/React code
    - explain: User wants explanation of current architecture
    """
    user_input = state["user_input"].lower()

    # Simple keyword-based intent classification (replace with LLM in production)
    if any(word in user_input for word in ["add", "create", "new", "include"]):
        intent: Intent = "new_feature"
    elif any(word in user_input for word in ["change", "modify", "update", "edit", "remove", "delete"]):
        intent = "modify_graph"
    elif any(word in user_input for word in ["generate", "code", "deploy", "build", "cdk"]):
        intent = "generate_code"
    elif any(word in user_input for word in ["explain", "what", "how", "why", "describe"]):
        intent = "explain"
    else:
        intent = "new_feature"  # Default to adding features

    return {**state, "intent": intent}


async def architect_node(state: GraphState) -> GraphState:
    """
    Architect agent: designs high-level application structure.

    This agent:
    - Analyzes the user's requirements
    - Suggests appropriate AWS services and React components
    - Updates the graph JSON with new nodes and connections
    """
    intent = state["intent"]
    user_input = state["user_input"]
    graph = state["graph_json"]

    # Placeholder response generation (replace with LLM call to Claude via Bedrock)
    if intent == "new_feature":
        response = f"I understand you want to add a new feature. Based on your request '{user_input}', I suggest adding the appropriate components to your architecture. You can use the buttons on the canvas to add Database, Auth, or API nodes, then connect them to define the data flow."
    elif intent == "modify_graph":
        response = f"I'll help you modify the architecture. Currently you have {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} connections. Click on a node to select it, or describe what changes you'd like to make."
    elif intent == "explain":
        node_count = len(graph.get('nodes', []))
        edge_count = len(graph.get('edges', []))
        response = f"Your current architecture has {node_count} components with {edge_count} connections. Each node represents an AWS service or React component that will be generated as Infrastructure as Code (CDK) or frontend code."
    else:
        response = "I'm here to help you design your application architecture. You can add nodes to the canvas using the buttons, or describe what you want to build and I'll suggest an architecture."

    return {**state, "response": response}


async def cdk_specialist_node(state: GraphState) -> GraphState:
    """
    CDK Specialist agent: generates AWS CDK infrastructure code.

    This agent:
    - Converts graph nodes to CDK constructs
    - Generates TypeScript CDK stack code
    - Handles AWS service configurations
    """
    if state["intent"] != "generate_code":
        return state

    graph = state["graph_json"]
    nodes = graph.get("nodes", [])

    if not nodes:
        return {
            **state,
            "response": state["response"] + "\n\nNo nodes found in the graph. Add some components first before generating code.",
        }

    # Generate placeholder CDK code (replace with LLM generation)
    cdk_code = '''import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class ScaffoldAiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Generated infrastructure will go here
    // Based on your graph with ''' + str(len(nodes)) + ''' nodes
  }
}
'''

    generated_files = state.get("generated_files", [])
    generated_files.append({
        "path": "packages/generated/infrastructure/lib/scaffold-ai-stack.ts",
        "content": cdk_code,
    })

    return {
        **state,
        "generated_files": generated_files,
        "response": state["response"] + "\n\nI've prepared the CDK infrastructure code based on your architecture.",
    }


async def react_specialist_node(state: GraphState) -> GraphState:
    """
    React Specialist agent: generates React component code.

    This agent:
    - Converts graph nodes to React components
    - Generates Next.js pages and components
    - Handles state management setup
    """
    if state["intent"] != "generate_code":
        return state

    # Placeholder - would generate React code based on graph
    return state


def should_generate_code(state: GraphState) -> str:
    """Router function to determine if we should generate code."""
    if state["intent"] == "generate_code":
        return "generate"
    return "respond"
