"""Python CDK code generation specialist."""

from typing import Dict, List


class PythonCDKSpecialist:
    """Generates Python CDK infrastructure code."""

    def generate_stack(self, nodes: List[Dict], edges: List[Dict], stack_name: str = "MyStack") -> str:
        """Generate Python CDK stack from architecture graph."""
        imports = self._get_imports(nodes)
        constructs = self._generate_constructs(nodes, edges)
        
        return f'''from aws_cdk import (
    Stack,
    {imports}
)
from constructs import Construct

class {stack_name}(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
{constructs}
'''

    def generate_app(self, stack_name: str = "MyStack") -> str:
        """Generate Python CDK app entry point."""
        return f'''#!/usr/bin/env python3
import aws_cdk as cdk
from {stack_name.lower()}_stack import {stack_name}

app = cdk.App()
{stack_name}(app, "{stack_name}")
app.synth()
'''

    def generate_requirements(self) -> str:
        """Generate requirements.txt for Python CDK."""
        return '''aws-cdk-lib>=2.0.0
constructs>=10.0.0
'''

    def _get_imports(self, nodes: List[Dict]) -> str:
        """Get required CDK imports based on node types."""
        imports = set(["RemovalPolicy"])
        
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            if node_type == "lambda":
                imports.update(["aws_lambda as _lambda", "Duration"])
            elif node_type == "api":
                imports.add("aws_apigateway as apigw")
            elif node_type == "database":
                imports.add("aws_dynamodb as dynamodb")
            elif node_type == "storage":
                imports.add("aws_s3 as s3")
            elif node_type == "queue":
                imports.add("aws_sqs as sqs")
            elif node_type == "auth":
                imports.add("aws_cognito as cognito")
            elif node_type == "cdn":
                imports.add("aws_cloudfront as cloudfront")
            elif node_type == "events":
                imports.add("aws_events as events")
        
        return ",\n    ".join(sorted(imports))

    def _generate_constructs(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Generate CDK construct definitions."""
        constructs = []
        
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("data", {}).get("type", "")
            label = node.get("data", {}).get("label", "Resource")
            var_name = self._to_var_name(label)
            
            if node_type == "lambda":
                constructs.append(f'''        {var_name} = _lambda.Function(
            self, "{node_id}",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_inline("def handler(event, context): return {{'statusCode': 200}}"),
            timeout=Duration.seconds(30)
        )''')
            
            elif node_type == "api":
                constructs.append(f'''        {var_name} = apigw.RestApi(
            self, "{node_id}",
            rest_api_name="{label}"
        )''')
            
            elif node_type == "database":
                constructs.append(f'''        {var_name} = dynamodb.Table(
            self, "{node_id}",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )''')
            
            elif node_type == "storage":
                constructs.append(f'''        {var_name} = s3.Bucket(
            self, "{node_id}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )''')
            
            elif node_type == "queue":
                constructs.append(f'''        {var_name} = sqs.Queue(
            self, "{node_id}",
            visibility_timeout=Duration.seconds(300)
        )''')
            
            elif node_type == "auth":
                constructs.append(f'''        {var_name} = cognito.UserPool(
            self, "{node_id}",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True)
        )''')
        
        return "\n\n".join(constructs)

    def _to_var_name(self, label: str) -> str:
        """Convert label to valid Python variable name."""
        return label.lower().replace(" ", "_").replace("-", "_")
