import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class ComputeStack extends cdk.NestedStack {
  constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
    super(scope, id, props);

    const eventbridgeeventbus = new events.EventBus(this, 'eventbridge', {
      eventBusName: 'EventBridge Event Bus',
    });

    const logingestionqueueDlq = new sqs.Queue(this, 'ingestion-queueDlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    const logingestionqueue = new sqs.Queue(this, 'ingestion-queue', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: logingestionqueueDlq,
        maxReceiveCount: 3,
      },
    });

    const flowlogprocessor = new lambda.Function(this, 'log-processor-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const anomalydetectionengine = new lambda.Function(this, 'anomaly-detection-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const analyticsaggregator = new lambda.Function(this, 'analytics-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const athenaqueryservice = new lambda.Function(this, 'athena-query-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const securityalertssns = new sns.Topic(this, 'alert-topic', {
      displayName: 'Security Alerts SNS',
    });

    const apihandler = new lambda.Function(this, 'api-handler-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const cdkinfrastructurestack = new sfn.StateMachine(this, 'cdk-stack', {
      definition: new sfn.Pass(this, 'PassState'),
      tracingEnabled: true,
    });

    const deadletterqueueDlq = new sqs.Queue(this, 'dlqDlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    const deadletterqueue = new sqs.Queue(this, 'dlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: deadletterqueueDlq,
        maxReceiveCount: 3,
      },
    });
  }
}
