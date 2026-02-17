"""Pydantic models for LangGraph state."""

from typing import Literal, TypedDict


Intent = Literal["new_feature", "modify_graph", "generate_code", "explain", "unknown"]


class GeneratedFile(TypedDict):
    """A generated file with path and content."""

    path: str
    content: str


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

    # Generated code files
    generated_files: list[GeneratedFile]

    # Any errors encountered
    errors: list[str]

    # Retry counter for error handling
    retry_count: int

    # Response to return to user
    response: str
