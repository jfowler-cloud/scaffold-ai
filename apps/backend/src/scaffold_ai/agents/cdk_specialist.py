"""CDK Specialist agent for generating AWS infrastructure code."""

CDK_SYSTEM_PROMPT = """You are an AWS CDK expert for Scaffold AI. Your role is to convert visual architecture diagrams into working AWS CDK TypeScript code.

## CDK Best Practices

### Use L2 Constructs
Prefer high-level (L2) constructs over L1 CloudFormation resources:

```typescript
// Good - L2 construct
new dynamodb.Table(this, 'Table', {
  partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
});

// Avoid - L1 construct
new dynamodb.CfnTable(this, 'Table', { ... });
```

### Serverless-First Architecture
- Lambda + API Gateway for APIs (not EC2/ECS)
- DynamoDB for databases (pay-per-request, no provisioning)
- SQS for async processing and decoupling
- EventBridge for event-driven patterns
- Step Functions for workflow orchestration
- SNS for fan-out and notifications
- CloudFront for static assets and caching

### IAM Least Privilege
Grant minimal permissions using L2 grant methods:

```typescript
table.grantReadWriteData(lambdaFunction);
bucket.grantRead(lambdaFunction);
queue.grantSendMessages(lambdaFunction);
```

### Resource Outputs
Export important ARNs and URLs:

```typescript
new cdk.CfnOutput(this, 'ApiUrl', {
  value: api.url,
  description: 'API Gateway URL',
});
```

## Service Templates

### DynamoDB Table
```typescript
const table = new dynamodb.Table(this, 'Table', {
  partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
  pointInTimeRecovery: true,
});
```

### Lambda Function
```typescript
const fn = new lambda.Function(this, 'Function', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
  timeout: cdk.Duration.seconds(30),
  memorySize: 256,
  tracing: lambda.Tracing.ACTIVE,
  environment: {
    TABLE_NAME: table.tableName,
  },
});
```

### API Gateway REST API
```typescript
const api = new apigateway.RestApi(this, 'Api', {
  restApiName: 'MyApi',
  deployOptions: {
    stageName: 'prod',
    tracingEnabled: true,
  },
  defaultCorsPreflightOptions: {
    allowOrigins: apigateway.Cors.ALL_ORIGINS,
    allowMethods: apigateway.Cors.ALL_METHODS,
  },
});

const items = api.root.addResource('items');
items.addMethod('GET', new apigateway.LambdaIntegration(fn));
items.addMethod('POST', new apigateway.LambdaIntegration(fn));
```

### Cognito User Pool
```typescript
const userPool = new cognito.UserPool(this, 'UserPool', {
  selfSignUpEnabled: true,
  signInAliases: { email: true },
  autoVerify: { email: true },
  passwordPolicy: {
    minLength: 8,
    requireLowercase: true,
    requireUppercase: true,
    requireDigits: true,
    requireSymbols: false,
  },
  accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
});

const userPoolClient = userPool.addClient('WebClient', {
  authFlows: { userPassword: true, userSrp: true },
});
```

### S3 Bucket
```typescript
const bucket = new s3.Bucket(this, 'Bucket', {
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  encryption: s3.BucketEncryption.S3_MANAGED,
  versioned: true,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
  autoDeleteObjects: true,
  cors: [{
    allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT],
    allowedOrigins: ['*'],
    allowedHeaders: ['*'],
  }],
});
```

### SQS Queue
```typescript
const dlq = new sqs.Queue(this, 'DeadLetterQueue', {
  retentionPeriod: cdk.Duration.days(14),
});

const queue = new sqs.Queue(this, 'Queue', {
  visibilityTimeout: cdk.Duration.seconds(300),
  deadLetterQueue: {
    queue: dlq,
    maxReceiveCount: 3,
  },
});
```

### EventBridge
```typescript
const bus = new events.EventBus(this, 'EventBus', {
  eventBusName: 'my-event-bus',
});

new events.Rule(this, 'Rule', {
  eventBus: bus,
  eventPattern: {
    source: ['my-service'],
    detailType: ['order-created'],
  },
  targets: [new targets.LambdaFunction(fn)],
});
```

### SNS Topic
```typescript
const topic = new sns.Topic(this, 'Topic', {
  displayName: 'Notifications',
});

topic.addSubscription(new subscriptions.EmailSubscription('user@example.com'));
topic.addSubscription(new subscriptions.LambdaSubscription(fn));
```

### Step Functions
```typescript
const definition = new sfn.Pass(this, 'StartState')
  .next(new tasks.LambdaInvoke(this, 'ProcessTask', {
    lambdaFunction: fn,
    outputPath: '$.Payload',
  }))
  .next(new sfn.Succeed(this, 'Success'));

const stateMachine = new sfn.StateMachine(this, 'StateMachine', {
  definition,
  timeout: cdk.Duration.minutes(5),
  tracingEnabled: true,
});
```

### CloudFront Distribution
```typescript
const distribution = new cloudfront.Distribution(this, 'Distribution', {
  defaultBehavior: {
    origin: new origins.S3Origin(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
  },
  defaultRootObject: 'index.html',
  errorResponses: [{
    httpStatus: 404,
    responseHttpStatus: 200,
    responsePagePath: '/index.html',
  }],
});
```

### Kinesis Stream
```typescript
const stream = new kinesis.Stream(this, 'Stream', {
  shardCount: 1,
  retentionPeriod: cdk.Duration.hours(24),
});

fn.addEventSource(new lambdaEventSources.KinesisEventSource(stream, {
  batchSize: 100,
  startingPosition: lambda.StartingPosition.LATEST,
}));
```

## Code Generation

Given a graph of nodes and edges representing an architecture, generate:
1. CDK Stack definitions with proper imports
2. Construct configurations for each service
3. IAM policies using grant methods
4. Connections between services (Lambda triggers, API integrations)
5. CloudFormation outputs for important values

The graph nodes contain:
- type: The AWS service type (database, auth, api, lambda, storage, queue, events, notification, workflow, cdn, stream)
- label: Human-readable name
- config: Optional service-specific configuration

Generate clean, well-documented TypeScript CDK code."""


class CDKSpecialistAgent:
    """Agent that generates AWS CDK infrastructure code."""

    def __init__(self):
        self.system_prompt = CDK_SYSTEM_PROMPT

    async def generate(self, graph: dict) -> list[dict]:
        """
        Generate CDK code from the architecture graph.

        In production, this would call Claude via AWS Bedrock.
        Returns a list of generated files.
        """
        nodes = graph.get("nodes", [])

        if not nodes:
            return []

        # Generate placeholder stack
        stack_code = self._generate_stack(nodes)

        return [
            {
                "path": "packages/generated/infrastructure/lib/scaffold-ai-stack.ts",
                "content": stack_code,
            }
        ]

    def _generate_stack(self, nodes: list) -> str:
        """Generate a CDK stack from nodes."""
        imports = set([
            "import * as cdk from 'aws-cdk-lib';",
            "import { Construct } from 'constructs';",
        ])
        constructs = []
        outputs = []

        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            label = node.get("data", {}).get("label", "Resource")
            safe_name = label.replace(" ", "").replace("-", "")

            if node_type == "database":
                imports.add("import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';")
                constructs.append(f'''
    // {label} - DynamoDB Table
    const {safe_name.lower()}Table = new dynamodb.Table(this, '{safe_name}Table', {{
      partitionKey: {{ name: 'pk', type: dynamodb.AttributeType.STRING }},
      sortKey: {{ name: 'sk', type: dynamodb.AttributeType.STRING }},
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}TableName', {{ value: {safe_name.lower()}Table.tableName }});")

            elif node_type == "auth":
                imports.add("import * as cognito from 'aws-cdk-lib/aws-cognito';")
                constructs.append(f'''
    // {label} - Cognito User Pool
    const userPool = new cognito.UserPool(this, '{safe_name}UserPool', {{
      selfSignUpEnabled: true,
      signInAliases: {{ email: true }},
      autoVerify: {{ email: true }},
      passwordPolicy: {{
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      }},
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
    }});

    const userPoolClient = userPool.addClient('{safe_name}WebClient', {{
      authFlows: {{ userPassword: true, userSrp: true }},
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}UserPoolId', {{ value: userPool.userPoolId }});")
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}ClientId', {{ value: userPoolClient.userPoolClientId }});")

            elif node_type == "api":
                imports.add("import * as apigateway from 'aws-cdk-lib/aws-apigateway';")
                constructs.append(f'''
    // {label} - API Gateway REST API
    const {safe_name.lower()}Api = new apigateway.RestApi(this, '{safe_name}Api', {{
      restApiName: '{label}',
      deployOptions: {{
        stageName: 'prod',
        tracingEnabled: true,
      }},
      defaultCorsPreflightOptions: {{
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      }},
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}ApiUrl', {{ value: {safe_name.lower()}Api.url }});")

            elif node_type == "lambda":
                imports.add("import * as lambda from 'aws-cdk-lib/aws-lambda';")
                constructs.append(f'''
    // {label} - Lambda Function
    const {safe_name.lower()}Fn = new lambda.Function(this, '{safe_name}Function', {{
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/{safe_name.lower()}'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      tracing: lambda.Tracing.ACTIVE,
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}FunctionArn', {{ value: {safe_name.lower()}Fn.functionArn }});")

            elif node_type == "storage":
                imports.add("import * as s3 from 'aws-cdk-lib/aws-s3';")
                constructs.append(f'''
    // {label} - S3 Bucket
    const {safe_name.lower()}Bucket = new s3.Bucket(this, '{safe_name}Bucket', {{
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      cors: [{{
        allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT],
        allowedOrigins: ['*'],
        allowedHeaders: ['*'],
      }}],
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}BucketName', {{ value: {safe_name.lower()}Bucket.bucketName }});")

            elif node_type == "queue":
                imports.add("import * as sqs from 'aws-cdk-lib/aws-sqs';")
                constructs.append(f'''
    // {label} - SQS Queue with Dead Letter Queue
    const {safe_name.lower()}Dlq = new sqs.Queue(this, '{safe_name}DLQ', {{
      retentionPeriod: cdk.Duration.days(14),
    }});

    const {safe_name.lower()}Queue = new sqs.Queue(this, '{safe_name}Queue', {{
      visibilityTimeout: cdk.Duration.seconds(300),
      deadLetterQueue: {{
        queue: {safe_name.lower()}Dlq,
        maxReceiveCount: 3,
      }},
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}QueueUrl', {{ value: {safe_name.lower()}Queue.queueUrl }});")

            elif node_type == "events":
                imports.add("import * as events from 'aws-cdk-lib/aws-events';")
                constructs.append(f'''
    // {label} - EventBridge Event Bus
    const {safe_name.lower()}Bus = new events.EventBus(this, '{safe_name}EventBus', {{
      eventBusName: '{safe_name.lower()}-bus',
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}EventBusName', {{ value: {safe_name.lower()}Bus.eventBusName }});")

            elif node_type == "notification":
                imports.add("import * as sns from 'aws-cdk-lib/aws-sns';")
                constructs.append(f'''
    // {label} - SNS Topic
    const {safe_name.lower()}Topic = new sns.Topic(this, '{safe_name}Topic', {{
      displayName: '{label}',
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}TopicArn', {{ value: {safe_name.lower()}Topic.topicArn }});")

            elif node_type == "workflow":
                imports.add("import * as sfn from 'aws-cdk-lib/aws-stepfunctions';")
                constructs.append(f'''
    // {label} - Step Functions State Machine
    const {safe_name.lower()}Definition = new sfn.Pass(this, '{safe_name}StartState');

    const {safe_name.lower()}StateMachine = new sfn.StateMachine(this, '{safe_name}StateMachine', {{
      definition: {safe_name.lower()}Definition,
      timeout: cdk.Duration.minutes(5),
      tracingEnabled: true,
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}StateMachineArn', {{ value: {safe_name.lower()}StateMachine.stateMachineArn }});")

            elif node_type == "cdn":
                imports.add("import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';")
                imports.add("import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';")
                constructs.append(f'''
    // {label} - CloudFront Distribution
    // Note: Requires an S3 bucket origin - connect to a Storage node
    // const {safe_name.lower()}Distribution = new cloudfront.Distribution(this, '{safe_name}Distribution', {{
    //   defaultBehavior: {{
    //     origin: new origins.S3Origin(bucket),
    //     viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    //   }},
    // }});''')

            elif node_type == "stream":
                imports.add("import * as kinesis from 'aws-cdk-lib/aws-kinesis';")
                constructs.append(f'''
    // {label} - Kinesis Data Stream
    const {safe_name.lower()}Stream = new kinesis.Stream(this, '{safe_name}Stream', {{
      shardCount: 1,
      retentionPeriod: cdk.Duration.hours(24),
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}StreamArn', {{ value: {safe_name.lower()}Stream.streamArn }});")

            elif node_type == "frontend":
                # Frontend node - generate hosting infrastructure
                imports.add("import * as s3 from 'aws-cdk-lib/aws-s3';")
                imports.add("import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';")
                imports.add("import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';")
                constructs.append(f'''
    // {label} - Static Website Hosting
    const {safe_name.lower()}WebBucket = new s3.Bucket(this, '{safe_name}WebBucket', {{
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    }});

    const {safe_name.lower()}Distribution = new cloudfront.Distribution(this, '{safe_name}Distribution', {{
      defaultBehavior: {{
        origin: new origins.S3Origin({safe_name.lower()}WebBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      }},
      defaultRootObject: 'index.html',
      errorResponses: [{{
        httpStatus: 404,
        responseHttpStatus: 200,
        responsePagePath: '/index.html',
      }}],
    }});''')
                outputs.append(f"    new cdk.CfnOutput(this, '{safe_name}DistributionUrl', {{ value: 'https://' + {safe_name.lower()}Distribution.distributionDomainName }});")

        # Sort imports for consistency
        sorted_imports = sorted(imports)

        # Build final stack
        outputs_str = "\n\n    // Stack Outputs\n" + "\n".join(outputs) if outputs else ""

        return f'''{chr(10).join(sorted_imports)}

export class ScaffoldAiStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);
{"".join(constructs)}{outputs_str}
  }}
}}
'''
