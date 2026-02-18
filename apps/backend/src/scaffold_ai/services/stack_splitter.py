"""Multi-stack architecture splitter for large deployments."""

from typing import Dict, List, Tuple


class StackSplitter:
    """Splits large architectures into multiple nested stacks."""

    MAX_RESOURCES_PER_STACK = 200  # CloudFormation limit is 500, use conservative limit

    def should_split(self, nodes: List[Dict]) -> bool:
        """Determine if architecture should be split into multiple stacks."""
        return len(nodes) > 15  # Split if more than 15 resources

    def split_by_layer(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict]:
        """Split architecture into logical stacks by layer (network, compute, data, frontend)."""
        stacks = {
            "network": {"nodes": [], "edges": []},
            "data": {"nodes": [], "edges": []},
            "compute": {"nodes": [], "edges": []},
            "frontend": {"nodes": [], "edges": []},
        }

        # Categorize nodes by type
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            node_id = node.get("id", "")

            if node_type in ["vpc", "subnet", "security-group"]:
                stacks["network"]["nodes"].append(node)
            elif node_type in ["database", "storage", "cache"]:
                stacks["data"]["nodes"].append(node)
            elif node_type in ["lambda", "ecs", "batch"]:
                stacks["compute"]["nodes"].append(node)
            elif node_type in ["frontend", "cdn", "api", "auth"]:
                stacks["frontend"]["nodes"].append(node)
            else:
                # Default to compute
                stacks["compute"]["nodes"].append(node)

        # Distribute edges to appropriate stacks
        for edge in edges:
            source_id = edge.get("source", "")
            target_id = edge.get("target", "")

            # Find which stacks contain source and target
            source_stack = self._find_node_stack(source_id, stacks)
            target_stack = self._find_node_stack(target_id, stacks)

            # Add edge to both stacks if cross-stack
            if source_stack:
                stacks[source_stack]["edges"].append(edge)
            if target_stack and target_stack != source_stack:
                stacks[target_stack]["edges"].append(edge)

        # Remove empty stacks
        return {k: v for k, v in stacks.items() if v["nodes"]}

    def generate_nested_stack_code(self, stacks: Dict[str, Dict], format: str = "cdk") -> List[Dict]:
        """Generate code for nested stacks."""
        files = []

        if format == "cdk":
            # Generate main stack that imports nested stacks
            main_stack = self._generate_main_stack_cdk(stacks)
            files.append({
                "path": "packages/generated/infrastructure/lib/main-stack.ts",
                "content": main_stack
            })

            # Generate each nested stack
            for stack_name, stack_data in stacks.items():
                nested_code = self._generate_nested_stack_cdk(stack_name, stack_data)
                files.append({
                    "path": f"packages/generated/infrastructure/lib/{stack_name}-stack.ts",
                    "content": nested_code
                })

        return files

    def _find_node_stack(self, node_id: str, stacks: Dict) -> str:
        """Find which stack contains a node."""
        for stack_name, stack_data in stacks.items():
            for node in stack_data["nodes"]:
                if node.get("id") == node_id:
                    return stack_name
        return ""

    def _generate_main_stack_cdk(self, stacks: Dict[str, Dict]) -> str:
        """Generate main CDK stack that orchestrates nested stacks."""
        imports = "\n".join([
            f"import {{ {name.capitalize()}Stack }} from './{name}-stack';"
            for name in stacks.keys()
        ])

        nested_stacks = "\n    ".join([
            f"const {name}Stack = new {name.capitalize()}Stack(this, '{name.capitalize()}Stack');"
            for name in stacks.keys()
        ])

        return f'''import * as cdk from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';
{imports}

export class MainStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);

    {nested_stacks}
  }}
}}
'''

    def _generate_nested_stack_cdk(self, stack_name: str, stack_data: Dict) -> str:
        """Generate a nested CDK stack."""
        nodes = stack_data["nodes"]
        
        # Simple construct generation (placeholder)
        constructs = "\n    ".join([
            f"// {node.get('data', {}).get('label', 'Resource')}"
            for node in nodes
        ])

        return f'''import * as cdk from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';

export class {stack_name.capitalize()}Stack extends cdk.NestedStack {{
  constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {{
    super(scope, id, props);

    {constructs}
  }}
}}
'''
