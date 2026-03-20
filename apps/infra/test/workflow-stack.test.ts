import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { DatabaseStack } from '../lib/database-stack';
import { FunctionsStack } from '../lib/functions-stack';
import { WorkflowStack } from '../lib/workflow-stack';

describe('ScaffoldAI Multi-Stack', () => {
  let dbTemplate: Template;
  let fnsTemplate: Template;
  let wfTemplate: Template;

  beforeAll(() => {
    const app = new cdk.App({ context: { 'aws:cdk:bundling-stacks': [] } });
    const db = new DatabaseStack(app, 'TestDB');
    const fns = new FunctionsStack(app, 'TestFns', {
      deploymentTier: 'testing',
      modelId: 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
      alarmTopic: db.alarmTopic,
    });
    new WorkflowStack(app, 'TestWF', { db, fns });

    dbTemplate = Template.fromStack(db);
    fnsTemplate = Template.fromStack(fns);
    wfTemplate = Template.fromStack(app.node.findChild('TestWF') as cdk.Stack);
  });

  // ── DatabaseStack ─────────────────────────────────────────────────────────

  test('creates Cognito user pool', () => {
    dbTemplate.hasResourceProperties('AWS::Cognito::UserPool', {
      UserPoolName: 'ScaffoldAI-Users',
    });
  });

  test('creates identity pool', () => {
    dbTemplate.resourceCountIs('AWS::Cognito::IdentityPool', 1);
  });

  test('creates S3 hosting bucket', () => {
    dbTemplate.resourceCountIs('AWS::S3::Bucket', 1);
  });

  test('creates CloudFront distribution', () => {
    dbTemplate.resourceCountIs('AWS::CloudFront::Distribution', 1);
  });

  test('creates DynamoDB sessions table with TTL', () => {
    dbTemplate.hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'scaffold-ai-sessions',
      KeySchema: [{ AttributeName: 'sessionId', KeyType: 'HASH' }],
      BillingMode: 'PAY_PER_REQUEST',
      TimeToLiveSpecification: { AttributeName: 'ttl', Enabled: true },
      PointInTimeRecoverySpecification: { PointInTimeRecoveryEnabled: true },
    });
  });

  test('creates SNS alarm topic', () => {
    dbTemplate.hasResourceProperties('AWS::SNS::Topic', { TopicName: 'ScaffoldAI-Alarms' });
  });

  test('creates $25/mo cost budget', () => {
    dbTemplate.hasResourceProperties('AWS::Budgets::Budget', {
      Budget: Match.objectLike({ BudgetName: 'scaffold-ai-monthly', BudgetLimit: { Amount: 25, Unit: 'USD' } }),
    });
  });

  // ── FunctionsStack ────────────────────────────────────────────────────────

  test('creates 6 Lambda functions (5 agents + get_execution)', () => {
    fnsTemplate.resourceCountIs('AWS::Lambda::Function', 6);
  });

  test('Lambda functions use Python 3.13', () => {
    fnsTemplate.hasResourceProperties('AWS::Lambda::Function', { Runtime: 'python3.13' });
  });

  test('Lambda functions have DEPLOYMENT_TIER env var', () => {
    fnsTemplate.hasResourceProperties('AWS::Lambda::Function', {
      Environment: { Variables: Match.objectLike({ DEPLOYMENT_TIER: 'testing' }) },
    });
  });

  test('creates error alarms for all functions', () => {
    const alarms = fnsTemplate.findResources('AWS::CloudWatch::Alarm', {
      Properties: { AlarmName: Match.stringLikeRegexp('ScaffoldAI-.*-Errors') },
    });
    expect(Object.keys(alarms).length).toBe(6);
  });

  // ── WorkflowStack ────────────────────────────────────────────────────────

  test('creates state machine', () => {
    wfTemplate.hasResourceProperties('AWS::StepFunctions::StateMachine', {
      StateMachineName: 'ScaffoldAI-Workflow',
    });
  });

  test('creates SFN failure alarm', () => {
    wfTemplate.hasResourceProperties('AWS::CloudWatch::Alarm', {
      AlarmName: 'ScaffoldAI-Workflow-ExecutionFailed',
    });
  });

  test('creates Cognito identity pool role attachment', () => {
    wfTemplate.resourceCountIs('AWS::Cognito::IdentityPoolRoleAttachment', 1);
  });

  test('exports WorkflowArn', () => {
    wfTemplate.hasOutput('WorkflowArn', {});
  });
});
