"""Lambda: generate React/Cloudscape component scaffolding."""
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger(__name__)


def handler(event: dict, context=None) -> dict:
    """
    Input:  {graph_json, generated_files, response, ...}
    Output: same dict + {generated_files (extended)}
    """
    graph = event.get("graph_json", {})
    if not graph.get("nodes"):
        return event

    try:
        import asyncio
        from react_specialist import ReactSpecialistAgent
        react_files = asyncio.run(ReactSpecialistAgent().generate(graph))
        if react_files:
            generated_files = list(event.get("generated_files", []))
            generated_files.extend(react_files)
            return {**event, "generated_files": generated_files}
    except Exception as e:
        logger.exception("React specialist failed: %s", e)

    return event
