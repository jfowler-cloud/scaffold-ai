/**
 * WorkflowStack — Step Functions workflow + Cognito identity pool role bindings.
 */
import * as cdk from 'aws-cdk-lib'
import * as sfn from 'aws-cdk-lib/aws-stepfunctions'
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as cognito from 'aws-cdk-lib/aws-cognito'
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch'
import * as cwActions from 'aws-cdk-lib/aws-cloudwatch-actions'
import * as sns from 'aws-cdk-lib/aws-sns'
import { Construct } from 'constructs'
import { FunctionsStack } from './functions-stack'
import { DatabaseStack } from './database-stack'

interface WorkflowStackProps extends cdk.StackProps {
  db: DatabaseStack
  fns: FunctionsStack
}

export class WorkflowStack extends cdk.Stack {
  readonly stateMachineArn: string

  constructor(scope: Construct, id: string, props: WorkflowStackProps) {
    super(scope, id, props)

    const { db, fns } = props

    // ── Step Functions tasks ─────────────────────────────────────────────────
    const interpret = new tasks.LambdaInvoke(this, 'Interpret', { lambdaFunction: fns.interpretFn, outputPath: '$.Payload' })
    const architect = new tasks.LambdaInvoke(this, 'Architect', { lambdaFunction: fns.architectFn, outputPath: '$.Payload' })
    const securityReview = new tasks.LambdaInvoke(this, 'SecurityReview', { lambdaFunction: fns.securityReviewFn, outputPath: '$.Payload' })
    const cdkSpecialist = new tasks.LambdaInvoke(this, 'CDKSpecialist', { lambdaFunction: fns.cdkSpecialistFn, outputPath: '$.Payload' })
    const reactSpecialist = new tasks.LambdaInvoke(this, 'ReactSpecialist', { lambdaFunction: fns.reactSpecialistFn, outputPath: '$.Payload' })

    // ── Routing ──────────────────────────────────────────────────────────────
    const respondOnly = new sfn.Succeed(this, 'RespondOnly')
    const securityFailed = new sfn.Succeed(this, 'SecurityFailed')

    const shouldGenerate = new sfn.Choice(this, 'ShouldGenerate')
      .when(sfn.Condition.stringEquals('$.intent', 'generate_code'), securityReview)
      .otherwise(respondOnly)

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

    // SFN failure alarm
    stateMachine.metricFailed({ period: cdk.Duration.minutes(5) })
      .createAlarm(this, 'WorkflowFailedAlarm', {
        alarmName: 'ScaffoldAI-Workflow-ExecutionFailed',
        threshold: 0,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        evaluationPeriods: 1,
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      })
      .addAlarmAction(new cwActions.SnsAction(db.alarmTopic))

    // ── Cognito Identity Pool Roles ──────────────────────────────────────────
    const userRole = new iam.Role(this, 'UserRole', {
      assumedBy: new iam.FederatedPrincipal('cognito-identity.amazonaws.com', {
        'StringEquals': { 'cognito-identity.amazonaws.com:aud': db.identityPool.ref },
        'ForAnyValue:StringLike': { 'cognito-identity.amazonaws.com:amr': 'authenticated' },
      }, 'sts:AssumeRoleWithWebIdentity'),
    })

    // Users can invoke getExecution and start the workflow
    fns.getExecutionFn.grantInvoke(userRole)
    stateMachine.grantStartExecution(userRole)

    // Allow reading plan handoff data from Project Planner AI
    userRole.addToPolicy(new iam.PolicyStatement({
      actions: ['dynamodb:GetItem'],
      resources: [
        cdk.Arn.format({ service: 'dynamodb', resource: 'table', resourceName: 'project-planner-handoff' }, this),
      ],
    }))

    new cognito.CfnIdentityPoolRoleAttachment(this, 'RoleAttachment', {
      identityPoolId: db.identityPool.ref,
      roles: { authenticated: userRole.roleArn },
    })

    // ── Outputs ──────────────────────────────────────────────────────────────
    new cdk.CfnOutput(this, 'WorkflowArn', { value: stateMachine.stateMachineArn })
  }
}
