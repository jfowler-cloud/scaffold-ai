/**
 * DatabaseStack — Cognito, S3/CloudFront hosting, monitoring.
 */
import * as cdk from 'aws-cdk-lib'
import * as cognito from 'aws-cdk-lib/aws-cognito'
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront'
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins'
import * as sns from 'aws-cdk-lib/aws-sns'
import * as budgets from 'aws-cdk-lib/aws-budgets'
import { Construct } from 'constructs'

export class DatabaseStack extends cdk.Stack {
  readonly userPool: cognito.UserPool
  readonly userPoolClient: cognito.UserPoolClient
  readonly identityPool: cognito.CfnIdentityPool
  readonly hostingBucket: s3.Bucket
  readonly distribution: cloudfront.Distribution
  readonly alarmTopic: sns.Topic

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    // ── Cognito ──────────────────────────────────────────────────────────────
    this.userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: 'ScaffoldAI-Users',
      signInAliases: { email: true },
      autoVerify: { email: true },
      standardAttributes: { email: { required: true, mutable: true } },
      passwordPolicy: { minLength: 8, requireLowercase: true, requireUppercase: true, requireDigits: true, requireSymbols: false },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      selfSignUpEnabled: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    })

    new cognito.CfnUserPoolGroup(this, 'UsersGroup', { userPoolId: this.userPool.userPoolId, groupName: 'users' })
    new cognito.CfnUserPoolGroup(this, 'AdminsGroup', { userPoolId: this.userPool.userPoolId, groupName: 'admins' })

    this.userPoolClient = this.userPool.addClient('WebClient', {
      userPoolClientName: 'ScaffoldAI-WebClient',
      authFlows: { userPassword: true, userSrp: true },
      preventUserExistenceErrors: true,
    })

    this.identityPool = new cognito.CfnIdentityPool(this, 'IdentityPool', {
      identityPoolName: 'ScaffoldAI-IdentityPool',
      allowUnauthenticatedIdentities: false,
      cognitoIdentityProviders: [{ clientId: this.userPoolClient.userPoolClientId, providerName: this.userPool.userPoolProviderName }],
    })

    // ── S3 + CloudFront ─────────────────────────────────────────────────────
    this.hostingBucket = new s3.Bucket(this, 'HostingBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    })

    const oac = new cloudfront.S3OriginAccessControl(this, 'OAC', { description: 'OAC for Scaffold AI frontend' })

    this.distribution = new cloudfront.Distribution(this, 'Distribution', {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(this.hostingBucket, { originAccessControl: oac }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        { httpStatus: 404, responseHttpStatus: 200, responsePagePath: '/index.html', ttl: cdk.Duration.minutes(5) },
        { httpStatus: 403, responseHttpStatus: 200, responsePagePath: '/index.html', ttl: cdk.Duration.minutes(5) },
      ],
    })

    // ── Monitoring ───────────────────────────────────────────────────────────
    this.alarmTopic = new sns.Topic(this, 'AlarmTopic', { topicName: 'ScaffoldAI-Alarms' })

    new budgets.CfnBudget(this, 'MonthlyBudget', {
      budget: {
        budgetName: 'scaffold-ai-monthly',
        budgetLimit: { amount: 25, unit: 'USD' },
        budgetType: 'COST',
        timeUnit: 'MONTHLY',
        costFilters: { TagKeyValue: ['user:Project$scaffold-ai'] },
      },
      notificationsWithSubscribers: [{
        notification: { comparisonOperator: 'GREATER_THAN', notificationType: 'ACTUAL', threshold: 80, thresholdType: 'PERCENTAGE' },
        subscribers: [{ address: this.alarmTopic.topicArn, subscriptionType: 'SNS' }],
      }],
    })

    // ── Outputs ──────────────────────────────────────────────────────────────
    new cdk.CfnOutput(this, 'UserPoolId', { value: this.userPool.userPoolId })
    new cdk.CfnOutput(this, 'UserPoolClientId', { value: this.userPoolClient.userPoolClientId })
    new cdk.CfnOutput(this, 'IdentityPoolId', { value: this.identityPool.ref })
    new cdk.CfnOutput(this, 'DistributionDomain', { value: this.distribution.distributionDomainName })
  }
}
