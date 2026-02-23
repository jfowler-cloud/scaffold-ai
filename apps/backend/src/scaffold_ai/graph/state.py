"""Pydantic models for LangGraph state."""

from typing import Literal, TypedDict


Intent = Literal["new_feature", "modify_graph", "generate_code", "explain", "unknown"]


class GeneratedFile(TypedDict):
    """A generated file with path and content."""

    path: str
    content: str


class SecurityIssue(TypedDict):
    """A security issue found during review."""

    service: str
    issue: str
    severity: str  # critical, high, medium, low
    recommendation: str


class SecurityRecommendation(TypedDict):
    """A security recommendation."""

    service: str
    recommendation: str


class ConfigChange(TypedDict):
    """A recommended configuration change for security."""

    node_id: str
    changes: dict


class SecurityEnhancements(TypedDict):
    """Security enhancements to apply to the architecture."""

    nodes_to_add: list[dict]
    config_changes: list[ConfigChange]


class SecurityReview(TypedDict):
    """Results of a security review."""

    security_score: int  # 0-100
    passed: bool
    critical_issues: list[SecurityIssue]
    warnings: list[SecurityIssue]
    recommendations: list[SecurityRecommendation]
    compliant_services: list[str]
    security_enhancements: SecurityEnhancements


class GraphState(TypedDict):
    """
    State schema for the LangGraph workflow.

    This state flows through all nodes in the workflow and accumulates
    information as it passes through each agent.
    """

    # Input from user
    user_input: str

    # Interpreted intent
    intent: Intent

    # The React Flow graph JSON
    graph_json: dict

    # IaC format preference (cdk, cloudformation, terraform)
    iac_format: str

    # Security review results (populated before code generation)
    security_review: SecurityReview | None

    # Generated code files
    generated_files: list[GeneratedFile]

    # Any errors encountered
    errors: list[str]

    # Retry counter for error handling
    retry_count: int

    # Skip security review (user marked issues as resolved)
    skip_security: bool

    # Response to return to user
    response: str
