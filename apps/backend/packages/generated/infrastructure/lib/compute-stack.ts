import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class ComputeStack extends cdk.NestedStack {
  constructor(scope: Construct, id: string, props?: cdk.NestedStackProps) {
    super(scope, id, props);

    const logprocessingqueueDlq = new sqs.Queue(this, 'log-processor-queueDlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    const logprocessingqueue = new sqs.Queue(this, 'log-processor-queue', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: logprocessingqueueDlq,
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

    const anomalydetector = new lambda.Function(this, 'anomaly-detector-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const securityeventsbus = new events.EventBus(this, 'event-bus', {
      eventBusName: 'Security Events Bus',
    });

    const alertnotifications = new sns.Topic(this, 'alert-notifications', {
      displayName: 'Alert Notifications',
    });

    const alerthandler = new lambda.Function(this, 'alert-handler-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const dashboardapihandler = new lambda.Function(this, 'dashboard-api-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const athenaqueryhandler = new lambda.Function(this, 'athena-query-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const anomalydetectionqueueDlq = new sqs.Queue(this, 'anomaly-queueDlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    const anomalydetectionqueue = new sqs.Queue(this, 'anomaly-queue', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: anomalydetectionqueueDlq,
        maxReceiveCount: 3,
      },
    });

    const dlqhandler = new lambda.Function(this, 'dlq-handler-lambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      code: lambda.Code.fromInline('def handler(event, context): return {"statusCode": 200}'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        LOG_LEVEL: 'INFO',
      },
    });

    const deadletterqueueDlq = new sqs.Queue(this, 'dead-letter-queueDlq', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
    });

    const deadletterqueue = new sqs.Queue(this, 'dead-letter-queue', {
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        queue: deadletterqueueDlq,
        maxReceiveCount: 3,
      },
    });
  }
}
