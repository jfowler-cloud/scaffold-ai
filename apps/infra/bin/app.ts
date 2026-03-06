#!/usr/bin/env node
import 'source-map-support/register'
import * as cdk from 'aws-cdk-lib'
import { WorkflowStack } from '../lib/workflow-stack'

const app = new cdk.App()

const tier = (process.env.DEPLOYMENT_TIER ?? 'testing') as 'testing' | 'optimized' | 'premium'

new WorkflowStack(app, 'ScaffoldAIWorkflowStack', {
  deploymentTier: tier,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region:  process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
  },
  tags: {
    Project: 'scaffold-ai',
    Tier: tier,
  },
})
