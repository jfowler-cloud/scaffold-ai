import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { WorkflowStack } from '../lib/workflow-stack';

describe('WorkflowStack', () => {
  let template: Template;

  beforeAll(() => {
    const app = new cdk.App({ context: { 'aws:cdk:bundling-stacks': [] } });
    new WorkflowStack(app, 'TestWorkflow', { deploymentTier: 'testing' });
    template = Template.fromStack(app.node.findChild('TestWorkflow') as cdk.Stack);
  });

  test('snapshot', () => {
    expect(template.toJSON()).toMatchSnapshot();
  });

  // ── Lambda Functions ──────────────────────────────────────────────────────

  test('creates 5 Lambda functions', () => {
    template.resourceCountIs('AWS::Lambda::Function', 5);
  });

  test('all Lambda functions use Python 3.12', () => {
    const fns = template.findResources('AWS::Lambda::Function');
    for (const fn of Object.values(fns)) {
      expect((fn as any).Properties.Runtime).toBe('python3.12');
    }
  });

  test('all Lambda functions have X-Ray tracing', () => {
    const fns = template.findResources('AWS::Lambda::Function');
    for (const fn of Object.values(fns)) {
      expect((fn as any).Properties.TracingConfig).toEqual({ Mode: 'Active' });
    }
  });

  test('Lambda functions have DEPLOYMENT_TIER env var set to testing', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Environment: { Variables: Match.objectLike({ DEPLOYMENT_TIER: 'testing' }) },
    });
  });

  // ── Step Functions ────────────────────────────────────────────────────────

  test('creates state machine with correct name', () => {
    template.resourceCountIs('AWS::StepFunctions::StateMachine', 1);
    template.hasResourceProperties('AWS::StepFunctions::StateMachine', {
      StateMachineName: 'ScaffoldAI-Workflow',
    });
  });

  // ── IAM ───────────────────────────────────────────────────────────────────

  test('grants Bedrock InvokeModel to Lambda roles', () => {
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: 'bedrock:InvokeModel',
            Effect: 'Allow',
          }),
        ]),
      },
    });
  });

  // ── Monitoring ────────────────────────────────────────────────────────────

  test('creates SNS alarm topic', () => {
    template.hasResourceProperties('AWS::SNS::Topic', {
      TopicName: 'ScaffoldAI-Alarms',
    });
  });

  test('creates Lambda error alarms for all functions', () => {
    const alarms = template.findResources('AWS::CloudWatch::Alarm', {
      Properties: { AlarmName: Match.stringLikeRegexp('ScaffoldAI-.*-Errors') },
    });
    expect(Object.keys(alarms).length).toBe(5);
  });

  test('creates SFN execution failure alarm', () => {
    template.hasResourceProperties('AWS::CloudWatch::Alarm', {
      AlarmName: 'ScaffoldAI-Workflow-ExecutionFailed',
      Threshold: 0,
      ComparisonOperator: 'GreaterThanThreshold',
    });
  });

  // ── Budget ────────────────────────────────────────────────────────────────

  test('creates $25/mo cost budget', () => {
    template.hasResourceProperties('AWS::Budgets::Budget', {
      Budget: Match.objectLike({
        BudgetName: 'scaffold-ai-monthly',
        BudgetLimit: { Amount: 25, Unit: 'USD' },
        BudgetType: 'COST',
        TimeUnit: 'MONTHLY',
      }),
    });
  });

  // ── Outputs ───────────────────────────────────────────────────────────────

  test('exports WorkflowArn', () => {
    template.hasOutput('WorkflowArn', {});
  });
});
