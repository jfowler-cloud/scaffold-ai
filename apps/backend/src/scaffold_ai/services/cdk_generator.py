"""Unified CDK code generator for consistent, secure infrastructure code."""

from typing import Dict, List, Set


class CDKGenerator:
    """Generates secure CDK TypeScript code from architecture nodes."""

    def generate(self, nodes: List[Dict], edges: List[Dict] = None) -> str:
        """Generate complete CDK stack code."""
        imports = self._get_imports(nodes)
        constructs = self._generate_constructs(nodes, edges or [])
        
        return f'''import * as cdk from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';
{imports}

export class ScaffoldAiStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);

{constructs}
  }}
}}
'''

    def _get_imports(self, nodes: List[Dict]) -> str:
        """Get required CDK imports based on node types."""
        imports = set()
        
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            if node_type == "lambda":
                imports.add("import * as lambda from 'aws-cdk-lib/aws-lambda';")
            elif node_type == "api":
                imports.add("import * as apigateway from 'aws-cdk-lib/aws-apigateway';")
            elif node_type == "database":
                imports.add("import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';")
            elif node_type == "storage":
                imports.add("import * as s3 from 'aws-cdk-lib/aws-s3';")
            elif node_type == "queue":
                imports.add("import * as sqs from 'aws-cdk-lib/aws-sqs';")
            elif node_type == "auth":
                imports.add("import * as cognito from 'aws-cdk-lib/aws-cognito';")
            elif node_type == "cdn":
                imports.add("import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';")
            elif node_type == "events":
                imports.add("import * as events from 'aws-cdk-lib/aws-events';")
            elif node_type == "notification":
                imports.add("import * as sns from 'aws-cdk-lib/aws-sns';")
            elif node_type == "workflow":
                imports.add("import * as sfn from 'aws-cdk-lib/aws-stepfunctions';")
            elif node_type == "stream":
                imports.add("import * as kinesis from 'aws-cdk-lib/aws-kinesis';")
        
        return "\n".join(sorted(imports))

    def _generate_constructs(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Generate CDK constructs with security best practices."""
        constructs = []
        node_vars = {}  # Track variable names for edge wiring
        
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("data", {}).get("type", "")
            label = node.get("data", {}).get("label", "Resource")
            var_name = self._to_var_name(label)
            node_vars[node_id] = var_name
            
            if node_type == "lambda":
                constructs.append(f'''    const {var_name} = new lambda.Function(this, '{node_id}', {{
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {{"statusCode": 200}}'),
      timeout: cdk.Duration.seconds(30),
      environment: {{
        LOG_LEVEL: 'INFO',
      }},
    }});''')
            
            elif node_type == "api":
                constructs.append(f'''    const {var_name} = new apigateway.RestApi(this, '{node_id}', {{
      restApiName: '{label}',
      deployOptions: {{
        stageName: 'prod',
        tracingEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
      }},
      defaultCorsPreflightOptions: {{
        allowOrigins: ['https://example.com'],  // TODO: Configure allowed origins
        allowMethods: apigateway.Cors.ALL_METHODS,
      }},
    }});''')
            
            elif node_type == "database":
                constructs.append(f'''    const {var_name} = new dynamodb.Table(this, '{node_id}', {{
      partitionKey: {{ name: 'id', type: dynamodb.AttributeType.STRING }},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    }});''')
            
            elif node_type == "storage":
                constructs.append(f'''    const {var_name} = new s3.Bucket(this, '{node_id}', {{
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    }});''')
            
            elif node_type == "queue":
                constructs.append(f'''    const {var_name}Dlq = new sqs.Queue(this, '{node_id}Dlq', {{
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    }});
    
    const {var_name} = new sqs.Queue(this, '{node_id}', {{
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {{
        queue: {var_name}Dlq,
        maxReceiveCount: 3,
      }},
    }});''')
            
            elif node_type == "auth":
                constructs.append(f'''    const {var_name} = new cognito.UserPool(this, '{node_id}', {{
      selfSignUpEnabled: true,
      signInAliases: {{ email: true }},
      passwordPolicy: {{
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: true,
      }},
      mfa: cognito.Mfa.OPTIONAL,
      advancedSecurityMode: cognito.AdvancedSecurityMode.ENFORCED,
    }});''')
            
            elif node_type == "cdn":
                constructs.append(f'''    const {var_name} = new cloudfront.Distribution(this, '{node_id}', {{
      defaultBehavior: {{
        origin: new cloudfront.HttpOrigin('example.com'),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      }},
    }});''')
            
            elif node_type == "events":
                constructs.append(f'''    const {var_name} = new events.EventBus(this, '{node_id}', {{
      eventBusName: '{label}',
    }});''')
            
            elif node_type == "notification":
                constructs.append(f'''    const {var_name} = new sns.Topic(this, '{node_id}', {{
      displayName: '{label}',
    }});''')
            
            elif node_type == "workflow":
                constructs.append(f'''    const {var_name} = new sfn.StateMachine(this, '{node_id}', {{
      definition: new sfn.Pass(this, 'PassState'),
      tracingEnabled: true,
    }});''')
            
            elif node_type == "stream":
                constructs.append(f'''    const {var_name} = new kinesis.Stream(this, '{node_id}', {{
      encryption: kinesis.StreamEncryption.MANAGED,
      retentionPeriod: cdk.Duration.hours(24),
    }});''')
        
        # Add edge-based wiring
        for edge in edges:
            source_id = edge.get("source", "")
            target_id = edge.get("target", "")
            source_var = node_vars.get(source_id)
            target_var = node_vars.get(target_id)
            
            if source_var and target_var:
                # Add grants/integrations based on connection types
                source_type = self._get_node_type(nodes, source_id)
                target_type = self._get_node_type(nodes, target_id)
                
                if source_type == "lambda" and target_type == "database":
                    constructs.append(f"\n    {target_var}.grantReadWriteData({source_var});")
                elif source_type == "lambda" and target_type == "storage":
                    constructs.append(f"\n    {target_var}.grantReadWrite({source_var});")
                elif source_type == "api" and target_type == "lambda":
                    constructs.append(f"\n    {source_var}.root.addMethod('ANY', new apigateway.LambdaIntegration({target_var}));")
        
        return "\n\n".join(constructs)

    def _get_node_type(self, nodes: List[Dict], node_id: str) -> str:
        """Get node type by ID."""
        for node in nodes:
            if node.get("id") == node_id:
                return node.get("data", {}).get("type", "")
        return ""

    def _to_var_name(self, label: str) -> str:
        """Convert label to valid TypeScript variable name."""
        return label.lower().replace(" ", "").replace("-", "")
