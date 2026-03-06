/**
 * FunctionsStack — Lambda functions with PythonLayerVersion, CloudWatch alarms.
 */
import * as cdk from 'aws-cdk-lib'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch'
import * as cwActions from 'aws-cdk-lib/aws-cloudwatch-actions'
import * as sns from 'aws-cdk-lib/aws-sns'
import { PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha'
import { Construct } from 'constructs'
import * as path from 'path'

interface FunctionsStackProps extends cdk.StackProps {
  deploymentTier: string
  modelId: string
  alarmTopic: sns.Topic
}

export class FunctionsStack extends cdk.Stack {
  readonly interpretFn: lambda.Function
  readonly architectFn: lambda.Function
  readonly securityReviewFn: lambda.Function
  readonly cdkSpecialistFn: lambda.Function
  readonly reactSpecialistFn: lambda.Function
  readonly getExecutionFn: lambda.Function

  constructor(scope: Construct, id: string, props: FunctionsStackProps) {
    super(scope, id, props)

    const { deploymentTier, modelId, alarmTopic } = props

    // ── Layers ───────────────────────────────────────────────────────────────
    const sharedLayer = new PythonLayerVersion(this, 'SharedLayer', {
      entry: path.join(__dirname, '..', 'layers', 'shared'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: 'Scaffold AI shared utilities — pydantic-settings, powertools, xray',
    })

    const agentsLayer = new PythonLayerVersion(this, 'AgentsLayer', {
      entry: path.join(__dirname, '..', 'layers', 'agents'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: 'Scaffold AI strands-agents core',
    })

    // ── IAM ──────────────────────────────────────────────────────────────────
    const bedrockPolicy = new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: [`arn:aws:bedrock:${this.region}::foundation-model/*`],
    })

    const sfnPolicy = new iam.PolicyStatement({
      actions: ['states:DescribeExecution'],
      resources: ['*'],
    })

    const commonEnv = {
      DEPLOYMENT_TIER: deploymentTier,
      BEDROCK_MODEL_ID: modelId,
    }

    // ── Lambda Functions ─────────────────────────────────────────────────────
    const fnProps = (name: string, layers: lambda.ILayerVersion[]): lambda.FunctionProps => ({
      functionName: `scaffold-ai-${name}`,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '..', '..', 'functions', name)),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: commonEnv,
      tracing: lambda.Tracing.ACTIVE,
      layers,
    })

    const agentFns = ['interpret', 'architect', 'security_review', 'cdk_specialist', 'react_specialist']
    const allAgentLayers = [sharedLayer, agentsLayer]

    this.interpretFn = new lambda.Function(this, 'InterpretFn', fnProps('interpret', allAgentLayers))
    this.architectFn = new lambda.Function(this, 'ArchitectFn', fnProps('architect', allAgentLayers))
    this.securityReviewFn = new lambda.Function(this, 'SecurityReviewFn', fnProps('security_review', allAgentLayers))
    this.cdkSpecialistFn = new lambda.Function(this, 'CDKSpecialistFn', fnProps('cdk_specialist', allAgentLayers))
    this.reactSpecialistFn = new lambda.Function(this, 'ReactSpecialistFn', fnProps('react_specialist', allAgentLayers))

    // get_execution only needs shared layer (no agents)
    this.getExecutionFn = new lambda.Function(this, 'GetExecutionFn', {
      ...fnProps('get_execution', [sharedLayer]),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    })
    this.getExecutionFn.addToRolePolicy(sfnPolicy)

    const allFns = [this.interpretFn, this.architectFn, this.securityReviewFn, this.cdkSpecialistFn, this.reactSpecialistFn]
    for (const fn of allFns) {
      fn.addToRolePolicy(bedrockPolicy)
    }

    // ── CloudWatch Alarms ────────────────────────────────────────────────────
    for (const fn of [...allFns, this.getExecutionFn]) {
      fn.metricErrors({ period: cdk.Duration.minutes(5) })
        .createAlarm(this, `${fn.node.id}ErrorAlarm`, {
          alarmName: `ScaffoldAI-${fn.node.id}-Errors`,
          threshold: 1, evaluationPeriods: 1,
          treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
        })
        .addAlarmAction(new cwActions.SnsAction(alarmTopic))

      fn.metricDuration({ statistic: 'p99', period: cdk.Duration.minutes(5) })
        .createAlarm(this, `${fn.node.id}DurationAlarm`, {
          alarmName: `ScaffoldAI-${fn.node.id}-P99Duration`,
          threshold: fn.timeout!.toMilliseconds() * 0.8,
          evaluationPeriods: 3,
          treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
        })
        .addAlarmAction(new cwActions.SnsAction(alarmTopic))
    }
  }
}
