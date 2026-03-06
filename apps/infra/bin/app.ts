#!/usr/bin/env node
import 'source-map-support/register'
import * as cdk from 'aws-cdk-lib'
import { DatabaseStack } from '../lib/database-stack'
import { FunctionsStack } from '../lib/functions-stack'
import { WorkflowStack } from '../lib/workflow-stack'

const app = new cdk.App()

const tier = (process.env.DEPLOYMENT_TIER ?? 'testing') as 'testing' | 'optimized' | 'premium'

const MODEL_MAP: Record<string, string> = {
  testing: 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
  optimized: 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
  premium: 'us.anthropic.claude-opus-4-5-20251101-v1:0',
}

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
}

const tags = {
  Project: 'scaffold-ai',
  Environment: tier,
  ManagedBy: 'cdk',
  CostCenter: 'portfolio',
}

const db = new DatabaseStack(app, 'ScaffoldAI-Database', {
  env, tags,
  description: 'Scaffold AI — Cognito, S3/CloudFront hosting, monitoring',
})

const fns = new FunctionsStack(app, 'ScaffoldAI-Functions', {
  env, tags,
  deploymentTier: tier,
  modelId: MODEL_MAP[tier],
  alarmTopic: db.alarmTopic,
  description: 'Scaffold AI — Lambda functions, layers, IAM',
})
fns.addDependency(db)

const workflow = new WorkflowStack(app, 'ScaffoldAI-Workflow', {
  env, tags,
  db, fns,
  description: 'Scaffold AI — Step Functions workflow, Cognito roles',
})
workflow.addDependency(fns)
