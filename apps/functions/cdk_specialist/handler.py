"""Lambda: generate IaC code (CDK/CloudFormation/Terraform/Python-CDK)."""
import json
import logging
import os
import pathlib
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
sys.path.insert(0, os.path.dirname(__file__))

from strands import Agent
from strands.models.bedrock import BedrockModel
from config import app_config

logger = logging.getLogger(__name__)

CDK_SYSTEM_PROMPT = """You are an AWS CDK expert. Generate TypeScript CDK code for this architecture.

Include: proper imports, L2 constructs with security best practices, least-privilege grants, encryption, logging.
Output ONLY valid TypeScript CDK code, no markdown."""


def _write_file(path: str, content: str) -> None:
    """Best-effort write to disk under repo root."""
    try:
        repo_root = pathlib.Path(__file__).resolve().parents[4]
        if not (repo_root / "apps").exists():
            return
        dest = repo_root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    except (OSError, IndexError) as e:
        logger.error("Could not write generated file: %s", e)


def handler(event: dict, context=None) -> dict:
    """
    Input:  {graph_json, iac_format, security_review, response, ...}
    Output: same dict + {generated_files, response (updated)}
    """
    graph = event.get("graph_json", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    iac_format = event.get("iac_format", "cdk")
    security_review = event.get("security_review", {})
    generated_files = list(event.get("generated_files", []))

    if not nodes:
        return {**event, "response": "No components in your architecture yet."}

    # Check for nested stacks
    from stack_splitter import StackSplitter
    splitter = StackSplitter()

    if iac_format == "python-cdk":
        from python_cdk_specialist import PythonCDKSpecialist
        spec = PythonCDKSpecialist()
        files = [
            {"path": "packages/generated/infrastructure/mystack_stack.py", "content": spec.generate_stack(nodes, edges)},
            {"path": "packages/generated/infrastructure/app.py", "content": spec.generate_app()},
            {"path": "packages/generated/infrastructure/requirements.txt", "content": spec.generate_requirements()},
        ]
        for f in files:
            _write_file(f["path"], f["content"])
        generated_files.extend(files)
        return {**event, "generated_files": generated_files, "response": f"{event.get('response', '')}\n\n**Python CDK Generated!**"}

    if iac_format == "cloudformation":
        from cloudformation_specialist import CloudFormationSpecialistAgent
        import asyncio
        code = asyncio.run(CloudFormationSpecialistAgent().generate(graph))
        file = {"path": "packages/generated/infrastructure/template.yaml", "content": code}
        _write_file(file["path"], file["content"])
        generated_files.append(file)
        return {**event, "generated_files": generated_files, "response": f"{event.get('response', '')}\n\n**CloudFormation Template Generated!**"}

    if iac_format == "terraform":
        from terraform_specialist import TerraformSpecialistAgent
        import asyncio
        code = asyncio.run(TerraformSpecialistAgent().generate(graph))
        file = {"path": "packages/generated/infrastructure/main.tf", "content": code}
        _write_file(file["path"], file["content"])
        generated_files.append(file)
        return {**event, "generated_files": generated_files, "response": f"{event.get('response', '')}\n\n**Terraform Generated!**"}

    # Default: CDK TypeScript
    if splitter.should_split(nodes):
        stacks = splitter.split_by_layer(nodes, edges)
        nested_files = splitter.generate_nested_stack_code(stacks, "cdk")
        for f in nested_files:
            _write_file(f["path"], f["content"])
        generated_files.extend(nested_files)
        return {
            **event,
            "generated_files": generated_files,
            "response": f"**Multi-Stack CDK Generated!** Split into {len(stacks)} stacks: {', '.join(stacks.keys())}.",
        }

    # Single CDK stack via Strands
    sec_reqs = "\n".join(
        f"Node {c['node_id']}: {c['changes']}"
        for c in security_review.get("security_enhancements", {}).get("config_changes", [])
    ) or "Standard security best practices"

    try:
        model = BedrockModel(model_id=app_config.model_id, max_tokens=app_config.bedrock_max_tokens, temperature=0.3)
        agent = Agent(model=model, system_prompt=CDK_SYSTEM_PROMPT)
        code = str(agent(f"Architecture:\n{json.dumps(graph, indent=2)}\n\nSecurity requirements:\n{sec_reqs}"))
        if "```typescript" in code:
            code = code.split("```typescript")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
    except Exception as e:
        logger.exception("CDK LLM generation failed, using fallback: %s", e)
        from cdk_generator import CDKGenerator
        code = CDKGenerator().generate(nodes, [])

    file_path = "packages/generated/infrastructure/lib/scaffold-ai-stack.ts"
    file = {"path": file_path, "content": code.strip()}
    _write_file(file_path, code.strip())
    generated_files.append(file)

    return {
        **event,
        "generated_files": generated_files,
        "response": f"{event.get('response', '')}\n\n**CDK Code Generated!** Saved to `{file_path}`.",
    }
