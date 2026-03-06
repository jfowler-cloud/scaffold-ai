"""Lambda: classify user intent from natural language."""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from strands import Agent
from strands.models.bedrock import BedrockModel
from config import app_config

logger = logging.getLogger(__name__)

PROMPT = """You are an intent classifier for Scaffold AI, a visual AWS architecture designer.

Classify the user's message into exactly ONE of these intents:
- new_feature: User wants to add new components or build something new
- modify_graph: User wants to change, remove, or reconnect existing components
- generate_code: User wants to generate CDK infrastructure or React code
- explain: User wants to understand the architecture or get help

Respond with ONLY the intent name, nothing else."""

_KEYWORD_FALLBACK = {
    "generate_code": ["generate", "code", "deploy", "build", "cdk", "export"],
    "explain":       ["explain", "what is", "how does", "describe", "?"],
    "modify_graph":  ["remove", "delete", "disconnect", "change", "modify", "update", "connect"],
}


def _keyword_classify(text: str) -> str:
    t = text.lower()
    for intent, words in _KEYWORD_FALLBACK.items():
        if any(w in t for w in words):
            return intent
    return "new_feature"


def handler(event: dict, context=None) -> dict:
    """
    Input:  {user_input, graph_json, iac_format, skip_security}
    Output: same dict + {intent}
    """
    user_input = event["user_input"]

    try:
        model = BedrockModel(
            model_id=app_config.model_id,
            max_tokens=256,
            temperature=0.0,
        )
        agent = Agent(model=model, system_prompt=PROMPT)
        result = str(agent(user_input)).strip().lower()
        valid = {"new_feature", "modify_graph", "generate_code", "explain"}
        intent = result if result in valid else _keyword_classify(user_input)
    except Exception as e:
        logger.warning("LLM intent classification failed: %s", e)
        intent = _keyword_classify(user_input)

    return {**event, "intent": intent}
