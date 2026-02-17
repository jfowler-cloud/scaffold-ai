"""LangGraph workflow definition for Scaffold AI."""

from langgraph.graph import StateGraph, END

from .state import GraphState
from .nodes import (
    interpret_intent,
    architect_node,
    cdk_specialist_node,
    react_specialist_node,
    should_generate_code,
)


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for processing user requests.

    The workflow follows this flow:
    1. Interpret Intent - Determine what the user wants
    2. Architect - Design/modify the architecture
    3. (Conditional) CDK Specialist - Generate infrastructure code
    4. (Conditional) React Specialist - Generate frontend code
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("interpret", interpret_intent)
    workflow.add_node("architect", architect_node)
    workflow.add_node("cdk_specialist", cdk_specialist_node)
    workflow.add_node("react_specialist", react_specialist_node)

    # Define edges
    workflow.set_entry_point("interpret")
    workflow.add_edge("interpret", "architect")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "architect",
        should_generate_code,
        {
            "generate": "cdk_specialist",
            "respond": END,
        },
    )

    workflow.add_edge("cdk_specialist", "react_specialist")
    workflow.add_edge("react_specialist", END)

    return workflow


# Compile the workflow
_workflow = create_workflow()
_app = _workflow.compile()


async def run_workflow(initial_state: GraphState) -> GraphState:
    """
    Run the LangGraph workflow with the given initial state.

    Args:
        initial_state: The starting state with user input and graph

    Returns:
        The final state after all nodes have processed
    """
    result = await _app.ainvoke(initial_state)
    return result
