"""Lambda: security review gate before code generation."""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from strands import Agent
from strands.models.bedrock import BedrockModel
from config import app_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AWS security specialist. Respond with JSON only.

Review the architecture for: IAM least privilege, encryption at rest/transit, authentication, no unnecessary public access, logging, data protection.

Config flags already applied (do NOT flag these as issues):
- config.encryption="KMS", config.block_public_access=true, config.versioning=true,
  config.https_only=true, config.pitr=true, config.vpc_enabled=true,
  config.tracing="Active", config.waf_enabled=true, config.has_dlq=true,
  config.mfa="REQUIRED", config.security_headers=true, config.throttling=true

Respond with ONLY this JSON:
{
  "security_score": 0-100,
  "passed": true/false,
  "critical_issues": [{"service": "...", "issue": "...", "severity": "critical", "recommendation": "..."}],
  "warnings": [{"service": "...", "issue": "...", "severity": "high|medium", "recommendation": "..."}],
  "recommendations": [{"service": "...", "recommendation": "..."}],
  "compliant_services": ["..."],
  "security_enhancements": {"nodes_to_add": [], "config_changes": [{"node_id": "...", "changes": {}}]}
}

Pass criteria: no critical issues, ≤3 high severity warnings."""

_EMPTY_REVIEW = {
    "security_score": 100, "passed": True,
    "critical_issues": [], "warnings": [], "recommendations": [],
    "compliant_services": [],
    "security_enhancements": {"nodes_to_add": [], "config_changes": []},
}


def _format_response(review: dict) -> str:
    score = review.get("security_score", 0)
    passed = review.get("passed", False)
    critical = review.get("critical_issues", [])
    warnings = review.get("warnings", [])

    if passed:
        lines = [f"**Security Review: PASSED** (Score: {score}/100)"]
        if warnings:
            lines += ["", f"**{len(warnings)} warnings:**"] + [f"- {w['service']}: {w['issue']}" for w in warnings[:3]]
        lines += ["", "Proceeding with code generation..."]
    else:
        lines = [f"**Security Review: FAILED** (Score: {score}/100)", "", "Code generation blocked:"]
        if critical:
            lines += ["", "**Critical Issues:**"] + [f"- {c['service']}: {c['issue']}" for c in critical]
        lines += ["", "Please address these issues and try again."]
    return "\n".join(lines)


def handler(event: dict, context=None) -> dict:
    """
    Input:  {user_input, graph_json, iac_format, skip_security, intent, response}
    Output: same dict + {security_review, response (updated)}
    """
    graph = event.get("graph_json", {})
    if not graph.get("nodes"):
        return {**event, "security_review": _EMPTY_REVIEW}

    if event.get("skip_security"):
        return {**event, "security_review": {**_EMPTY_REVIEW, "security_score": 80}}

    try:
        model = BedrockModel(model_id=app_config.model_id, max_tokens=2048, temperature=0.0)
        agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)
        raw = str(agent(f"Architecture to review:\n{json.dumps(graph, indent=2)}")).strip()

        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
            if "```" in raw:
                raw = raw.split("```")[0]

        review = json.loads(raw)
    except Exception as e:
        logger.warning("Security review LLM failed, using autofix fallback: %s", e)
        # Fallback: use the existing SecurityAutoFix service
        from security_autofix import SecurityAutoFix
        autofix = SecurityAutoFix()
        score_data = autofix.get_security_score(graph)
        review = {
            **_EMPTY_REVIEW,
            "security_score": score_data.get("percentage", 80),
            "passed": score_data.get("percentage", 80) >= 60,
        }

    return {**event, "security_review": review, "response": _format_response(review)}
