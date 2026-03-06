import * as cdk from 'aws-cdk-lib'
import * as sfn from 'aws-cdk-lib/aws-stepfunctions'
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as iam from 'aws-cdk-lib/aws-iam'
import { Construct } from 'constructs'
import * as path from 'path'

interface WorkflowStackProps extends cdk.StackProps {
  deploymentTier: 'testing' | 'optimized' | 'premium'
}

const MODEL_MAP = {
  testing:   'us.anthropic.claude-haiku-4-5-20251001-v1:0',
  optimized: 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
  premium:   'us.anthropic.claude-opus-4-5-20251101-v1:0',
}

export class WorkflowStack extends cdk.Stack {
  public readonly stateMachineArn: string

  constructor(scope: Construct, id: string, props: WorkflowStackProps) {
    super(scope, id, props)

    const { deploymentTier } = props
    const modelId = MODEL_MAP[deploymentTier]

    const bedrockPolicy = new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: [`arn:aws:bedrock:${this.region}::foundation-model/*`],
    })

    const commonEnv = {
      DEPLOYMENT_TIER: deploymentTier,
      BEDROCK_MODEL_ID: modelId,
      AWS_REGION: this.region,
    }

    const fnProps = (name: string): lambda.FunctionProps => ({
      functionName: `scaffold-ai-${name}`,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '..', '..', 'functions', name)),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: commonEnv,
      tracing: lambda.Tracing.ACTIVE,
    })

    const interpretFn      = new lambda.Function(this, 'InterpretFn',     fnProps('interpret'))
    const architectFn      = new lambda.Function(this, 'ArchitectFn',     fnProps('architect'))
    const securityReviewFn = new lambda.Function(this, 'SecurityReviewFn', fnProps('security_review'))
    const cdkSpecialistFn  = new lambda.Function(this, 'CDKSpecialistFn', fnProps('cdk_specialist'))
    const reactSpecialistFn = new lambda.Function(this, 'ReactSpecialistFn', fnProps('react_specialist'))

    for (const fn of [interpretFn, architectFn, securityReviewFn, cdkSpecialistFn, reactSpecialistFn]) {
      fn.addToRolePolicy(bedrockPolicy)
    }

    // ── Step Functions tasks ──────────────────────────────────────────────────

    const interpret = new tasks.LambdaInvoke(this, 'Interpret', {
      lambdaFunction: interpretFn,
      outputPath: '$.Payload',
    })

    const architect = new tasks.LambdaInvoke(this, 'Architect', {
      lambdaFunction: architectFn,
      outputPath: '$.Payload',
    })

    const securityReview = new tasks.LambdaInvoke(this, 'SecurityReview', {
      lambdaFunction: securityReviewFn,
      outputPath: '$.Payload',
    })

    const cdkSpecialist = new tasks.LambdaInvoke(this, 'CDKSpecialist', {
      lambdaFunction: cdkSpecialistFn,
      outputPath: '$.Payload',
    })

    const reactSpecialist = new tasks.LambdaInvoke(this, 'ReactSpecialist', {
      lambdaFunction: reactSpecialistFn,
      outputPath: '$.Payload',
    })

    // ── Routing — mirrors LangGraph conditional edges ─────────────────────────

    const respondOnly = new sfn.Succeed(this, 'RespondOnly')
    const securityFailed = new sfn.Succeed(this, 'SecurityFailed')

    // Replaces should_generate_code()
    const shouldGenerate = new sfn.Choice(this, 'ShouldGenerate')
      .when(sfn.Condition.stringEquals('$.intent', 'generate_code'), securityReview)
      .otherwise(respondOnly)

    // Replaces security_gate()
    const secGate = new sfn.Choice(this, 'SecurityGate')
      .when(sfn.Condition.booleanEquals('$.security_review.passed', true), cdkSpecialist)
      .otherwise(securityFailed)

    cdkSpecialist.next(reactSpecialist)

    securityReview.next(secGate)

    const definition = interpret.next(architect).next(shouldGenerate)

    const stateMachine = new sfn.StateMachine(this, 'ScaffoldAIWorkflow', {
      stateMachineName: 'ScaffoldAI-Workflow',
      definitionBody: sfn.DefinitionBody.fromChainable(definition),
      timeout: cdk.Duration.minutes(10),
    })

    this.stateMachineArn = stateMachine.stateMachineArn
    new cdk.CfnOutput(this, 'WorkflowArn', { value: stateMachine.stateMachineArn })
  }
}
