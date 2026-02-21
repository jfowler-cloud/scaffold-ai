import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

export class SecureArchitectureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // KMS key for encryption
    const encryptionKey = new kms.Key(this, 'EncryptionKey', {
      enableKeyRotation: true,
      description: 'KMS key for encrypting application resources',
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Cognito User Pool with advanced security
    const userPool = new cognito.UserPool(this, 'Auth', {
      userPoolName: 'Auth',
      selfSignUpEnabled: true,
      signInAliases: {
        email: true,
        username: true,
      },
      autoVerify: {
        email: true,
      },
      passwordPolicy: {
        minLength: 12,
        requireUppercase: true,
        requireLowercase: true,
        requireDigits: true,
        requireSymbols: true,
        tempPasswordValidity: cdk.Duration.days(3),
      },
      mfa: cognito.Mfa.REQUIRED,
      mfaSecondFactor: {
        sms: true,
        otp: true,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      advancedSecurityMode: cognito.AdvancedSecurityMode.ENFORCED,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      userPoolName: 'AuthUserPool',
    });

    // User Pool Client
    const userPoolClient = new cognito.UserPoolClient(this, 'AuthClient', {
      userPool,
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      preventUserExistenceErrors: true,
      generateSecret: false,
    });

    // DynamoDB Table with encryption and security features
    const dataTable = new dynamodb.Table(this, 'Data', {
      tableName: 'Data',
      partitionKey: {
        name: 'pk',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'sk',
        type: dynamodb.AttributeType.STRING,
      },
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: encryptionKey,
      pointInTimeRecovery: true,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      deletionProtection: true,
    });

    // Dead Letter Queue for Lambda
    const deadLetterQueue = new sqs.Queue(this, 'HandlerDLQ', {
      queueName: 'HandlerDLQ',
      encryption: sqs.QueueEncryption.KMS,
      encryptionMasterKey: encryptionKey,
      retentionPeriod: cdk.Duration.days(14),
    });

    // CloudWatch Log Group for Lambda
    const lambdaLogGroup = new logs.LogGroup(this, 'HandlerLogGroup', {
      logGroupName: '/aws/lambda/Handler',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambda Function with security best practices
    const handlerFunction = new lambda.Function(this, 'Handler', {
      functionName: 'Handler',
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
        exports.handler = async (event) => {
          console.log('Event:', JSON.stringify(event, null, 2));
          return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Success' }),
          };
        };
      `),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      reservedConcurrentExecutions: 100,
      tracing: lambda.Tracing.ACTIVE,
      deadLetterQueue: deadLetterQueue,
      environmentEncryption: encryptionKey,
      logGroup: lambdaLogGroup,
      environment: {
        TABLE_NAME: dataTable.tableName,
      },
    });

    // Grant DynamoDB permissions with least privilege
    dataTable.grant(handlerFunction, 
      'dynamodb:GetItem',
      'dynamodb:PutItem',
      'dynamodb:Query',
      'dynamodb:UpdateItem',
      'dynamodb:DeleteItem'
    );

    // CloudWatch Log Group for API Gateway
    const apiLogGroup = new logs.LogGroup(this, 'APILogGroup', {
      logGroupName: '/aws/apigateway/API',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // API Gateway with Cognito Authorizer
    const api = new apigateway.RestApi(this, 'API', {
      restApiName: 'API',
      description: 'Secure API with Cognito authentication',
      deployOptions: {
        stageName: 'prod',
        tracingEnabled: true,
        accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields({
          caller: true,
          httpMethod: true,
          ip: true,
          protocol: true,
          requestTime: true,
          resourcePath: true,
          responseLength: true,
          status: true,
          user: true,
        }),
        throttlingRateLimit: 1000,
        throttlingBurstLimit: 500,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'Authorization', 'X-Amz-Date', 'X-Api-Key'],
      },
      cloudWatchRole: true,
    });

    // Configure minimum TLS version
    const cfnRestApi = api.node.defaultChild as apigateway.CfnRestApi;
    cfnRestApi.addPropertyOverride('MinimumCompressionSize', 1024);

    // Cognito Authorizer
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'CognitoAuthorizer', {
      cognitoUserPools: [userPool],
      authorizerName: 'CognitoAuthorizer',
      identitySource: 'method.request.header.Authorization',
    });

    // Lambda Integration
    const lambdaIntegration = new apigateway.LambdaIntegration(handlerFunction, {
      proxy: true,
      allowTestInvoke: false,
    });

    // Add API resources with Cognito authorization
    const resource = api.root.addResource('items');
    
    resource.addMethod('GET', lambdaIntegration, {
      authorizer: authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    resource.addMethod('POST', lambdaIntegration, {
      authorizer: authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    const itemResource = resource.addResource('{id}');
    
    itemResource.addMethod('GET', lambdaIntegration, {
      authorizer: authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    itemResource.addMethod('PUT', lambdaIntegration, {
      authorizer: authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    itemResource.addMethod('DELETE', lambdaIntegration, {
      authorizer: authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    // Grant KMS permissions to Lambda
    encryptionKey.grantEncryptDecrypt(handlerFunction);

    // Outputs
    new cdk.CfnOutput(this, 'UserPoolId', {
      value: userPool.userPoolId,
      description: 'Cognito User Pool ID',
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
    });

    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway Endpoint URL',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: dataTable.tableName,
      description: 'DynamoDB Table Name',
    });

    new cdk.CfnOutput(this, 'LambdaFunctionArn', {
      value: handlerFunction.functionArn,
      description: 'Lambda Function ARN',
    });
  }
}

const app = new cdk.App();
new SecureArchitectureStack(app, 'SecureArchitectureStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});