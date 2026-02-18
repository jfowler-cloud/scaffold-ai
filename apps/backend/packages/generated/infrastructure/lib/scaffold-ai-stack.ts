import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as xray from 'aws-cdk-lib/aws-xray';

class GenerateCodeStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Generate Code Lambda
    const generateCodeLambda = new lambda.Function(this, 'GenerateCodeLambda', {
      runtime: lambda.Runtime.NODEJS_14_X,
      code: lambda.Code.fromAsset('path/to/lambda/code'),
      handler: 'index.handler',
      tracing: lambda.Tracing.ACTIVE,
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        DYNAMODB_TABLE_NAME: generatedCodeTable.tableName,
      },
    });

    // Grant the minimum required permissions to the Lambda function
    generatedCodeTable.grantReadWriteData(generateCodeLambda);

    // Generate Code API
    const generateCodeApi = new apigateway.RestApi(this, 'GenerateCodeApi', {
      restApiName: 'Generate Code API',
      description: 'API Gateway for the Generate Code Lambda function',
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.ERROR,
        dataTraceEnabled: true,
      },
    });

    // Configure authentication and authorization for the API
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'Authorizer', {
      cognitoUserPools: [userPool],
    });
    const resource = generateCodeApi.root.addResource('generate-code');
    resource.addMethod('POST', new apigateway.LambdaIntegration(generateCodeLambda), {
      authorizer,
    });

    // Generated Code DynamoDB Table
    const generatedCodeTable = new dynamodb.Table(this, 'GeneratedCodeTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
      encryption: dynamodb.TableEncryption.DEFAULT,
    });

    // Generate Code Event
    const generateCodeEvent = new events.Rule(this, 'GenerateCodeEvent', {
      eventPattern: {
        source: ['aws.lambda'],
        detailType: ['AWS Lambda Function Invocation Result'],
        detail: {
          functionName: [generateCodeLambda.functionName],
        },
      },
    });
    generateCodeEvent.addTarget(new targets.LambdaFunction(someOtherLambda));
  }
}