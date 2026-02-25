"""Application configuration."""

import os
from typing import Literal

# Deployment tier — controls model selection
# Set DEPLOYMENT_TIER env var to override (testing/optimized/premium)
DeploymentTier = Literal["testing", "optimized", "premium"]

DEPLOYMENT_TIER: DeploymentTier = os.getenv("DEPLOYMENT_TIER", "testing")  # type: ignore[assignment]

# Bedrock model IDs per tier
_MODEL_MAP: dict[str, str] = {
    "testing":   "anthropic.claude-haiku-4-5-20251001-v1:0",
    "optimized": "anthropic.claude-sonnet-4-5-20250929-v1:0",
    "premium":   "anthropic.claude-opus-4-5-20251101-v1:0",
}

def get_model_id() -> str:
    """Return the Bedrock model ID for the current deployment tier.

    BEDROCK_MODEL_ID env var always takes precedence for manual overrides.
    """
    return os.getenv("BEDROCK_MODEL_ID") or _MODEL_MAP.get(DEPLOYMENT_TIER, _MODEL_MAP["testing"])
