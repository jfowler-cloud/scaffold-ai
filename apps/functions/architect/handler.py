"""Lambda: design/modify the architecture graph using Claude."""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from strands import Agent
from strands.models.bedrock import BedrockModel
from config import app_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a serverless-first AWS solutions architect for Scaffold AI.

You must respond with valid JSON in this exact format:
{
  "explanation": "Brief explanation (2-3 sentences)",
  "nodes": [{"id": "unique-id", "type": "lambda|api|database|storage|auth|queue|events|cdn|workflow|stream|notification|frontend", "label": "Human readable name", "description": "What this does"}],
  "edges": [{"source": "source-id", "target": "target-id", "label": "optional"}]
}

Prefer serverless: Lambda over EC2, DynamoDB over RDS, SQS/EventBridge for async.
If modifying existing architecture, preserve existing nodes and add new ones.
Respond with ONLY the JSON."""

_TYPE_COLUMNS = {
    "frontend": 0, "cdn": 0, "auth": 1, "api": 2,
    "lambda": 3, "workflow": 3, "queue": 4, "events": 4,
    "notification": 4, "stream": 5, "database": 6, "storage": 6,
}


def _position_nodes(new_nodes: list, existing_nodes: list) -> list:
    col_counts = {i: 0 for i in range(7)}
    for n in existing_nodes:
        col_counts[_TYPE_COLUMNS.get(n.get("data", {}).get("type", "api"), 2)] += 1

    result = []
    for n in new_nodes:
        col = _TYPE_COLUMNS.get(n.get("type", "api"), 2)
        result.append({
            "id": n["id"],
            "type": n.get("type", "api"),
            "position": {"x": 50 + col * 320, "y": 50 + col_counts[col] * 200},
            "data": {"label": n.get("label", "Component"), "type": n.get("type", "api"), "description": n.get("description", "")},
        })
        col_counts[col] += 1
    return result


def _explain(event: dict) -> dict:
    graph = event.get("graph_json", {})
    nodes = graph.get("nodes", [])
    if not nodes:
        return {**event, "response": "Your canvas is empty. Describe what you want to build and I'll create an architecture for you."}

    try:
        model = BedrockModel(model_id=app_config.model_id, max_tokens=1024, temperature=0.5)
        agent = Agent(model=model, system_prompt="You are a helpful AWS solutions architect.")
        node_summary = [{"type": n.get("data", {}).get("type"), "label": n.get("data", {}).get("label")} for n in nodes]
        result = str(agent(f"Explain this AWS architecture:\n{json.dumps(node_summary, indent=2)}"))
        return {**event, "response": result}
    except Exception as e:
        logger.exception("Explain failed: %s", e)
        labels = ", ".join(n.get("data", {}).get("label", "?") for n in nodes)
        return {**event, "response": f"Your architecture has {len(nodes)} components: {labels}."}


def handler(event: dict, context=None) -> dict:
    """
    Input:  {user_input, graph_json, iac_format, skip_security, intent}
    Output: same dict + {graph_json (updated), response}
    """
    if event.get("intent") == "explain":
        return _explain(event)

    graph = event.get("graph_json", {"nodes": [], "edges": []})
    existing_nodes = graph.get("nodes", [])
    existing_edges = graph.get("edges", [])
    existing_ids = {n["id"] for n in existing_nodes}

    nodes_summary = json.dumps(
        [{"id": n["id"], "type": n.get("data", {}).get("type"), "label": n.get("data", {}).get("label")} for n in existing_nodes],
        indent=2,
    ) if existing_nodes else "Empty - no components yet"

    prompt = (
        f"Current architecture:\n{nodes_summary}\n\n"
        f"User request: {event['user_input']}"
    )

    try:
        model = BedrockModel(model_id=app_config.model_id, max_tokens=app_config.bedrock_max_tokens, temperature=app_config.bedrock_temperature)
        agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)
        raw = str(agent(prompt)).strip()

        # Strip code fences if present
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
            if "```" in raw:
                raw = raw.split("```")[0]

        result = json.loads(raw)

        new_nodes = _position_nodes(result.get("nodes", []), existing_nodes)
        new_nodes = [n for n in new_nodes if n["id"] not in existing_ids]

        new_edges = [
            {"id": f"e-{e['source']}-{e['target']}", "source": e["source"], "target": e["target"], "label": e.get("label", "")}
            for e in result.get("edges", [])
        ]
        existing_edge_ids = {e["id"] for e in existing_edges}
        new_edges = [e for e in new_edges if e["id"] not in existing_edge_ids]

        return {
            **event,
            "graph_json": {"nodes": existing_nodes + new_nodes, "edges": existing_edges + new_edges},
            "response": result.get("explanation", "Architecture updated."),
        }

    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s", e)
        return {**event, "response": "I understood your request but had trouble generating the architecture. Could you try rephrasing it?"}
    except Exception as e:
        logger.exception("Architect failed: %s", e)
        return {**event, "response": "I encountered an error while designing the architecture. Please try again."}
