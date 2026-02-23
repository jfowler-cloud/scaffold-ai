import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DataStack } from './data-stack';
import { ComputeStack } from './compute-stack';
import { FrontendStack } from './frontend-stack';

export class MainStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const dataStack = new DataStack(this, 'DataStack');
    const computeStack = new ComputeStack(this, 'ComputeStack');
    const frontendStack = new FrontendStack(this, 'FrontendStack');
  }
}
