import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { APINode } from '../components/nodes/APINode';
import { AuthNode } from '../components/nodes/AuthNode';
import { CdnNode } from '../components/nodes/CdnNode';
import { DatabaseNode } from '../components/nodes/DatabaseNode';
import { EventsNode } from '../components/nodes/EventsNode';
import { FrontendNode } from '../components/nodes/FrontendNode';
import { LambdaNode } from '../components/nodes/LambdaNode';
import { NotificationNode } from '../components/nodes/NotificationNode';
import { QueueNode } from '../components/nodes/QueueNode';
import { StorageNode } from '../components/nodes/StorageNode';
import { StreamNode } from '../components/nodes/StreamNode';
import { WorkflowNode } from '../components/nodes/WorkflowNode';
// Compute
import { Ec2Node } from '../components/nodes/Ec2Node';
import { EcsNode } from '../components/nodes/EcsNode';
import { EksNode } from '../components/nodes/EksNode';
import { FargateNode } from '../components/nodes/FargateNode';
import { BatchNode } from '../components/nodes/BatchNode';
import { AppRunnerNode } from '../components/nodes/AppRunnerNode';
import { LightsailNode } from '../components/nodes/LightsailNode';
import { ElasticBeanstalkNode } from '../components/nodes/ElasticBeanstalkNode';
// Database
import { RdsNode } from '../components/nodes/RdsNode';
import { AuroraNode } from '../components/nodes/AuroraNode';
import { ElastiCacheNode } from '../components/nodes/ElastiCacheNode';
import { NeptuneNode } from '../components/nodes/NeptuneNode';
import { DocumentDbNode } from '../components/nodes/DocumentDbNode';
import { TimestreamNode } from '../components/nodes/TimestreamNode';
import { RedshiftNode } from '../components/nodes/RedshiftNode';
import { OpenSearchNode } from '../components/nodes/OpenSearchNode';
// Storage
import { EfsNode } from '../components/nodes/EfsNode';
import { EbsNode } from '../components/nodes/EbsNode';
import { BackupNode } from '../components/nodes/BackupNode';
// Networking
import { VpcNode } from '../components/nodes/VpcNode';
import { ElbNode } from '../components/nodes/ElbNode';
import { Route53Node } from '../components/nodes/Route53Node';
import { NatGatewayNode } from '../components/nodes/NatGatewayNode';
// Security
import { WafNode } from '../components/nodes/WafNode';
import { SecretsManagerNode } from '../components/nodes/SecretsManagerNode';
import { KmsNode } from '../components/nodes/KmsNode';
import { IamNode } from '../components/nodes/IamNode';
import { ShieldNode } from '../components/nodes/ShieldNode';
import { GuardDutyNode } from '../components/nodes/GuardDutyNode';
// ML/AI
import { BedrockNode } from '../components/nodes/BedrockNode';
import { SageMakerNode } from '../components/nodes/SageMakerNode';
import { RekognitionNode } from '../components/nodes/RekognitionNode';
// Analytics
import { AthenaNode } from '../components/nodes/AthenaNode';
import { GlueNode } from '../components/nodes/GlueNode';
import { QuickSightNode } from '../components/nodes/QuickSightNode';
import { EmrNode } from '../components/nodes/EmrNode';
import { FirehoseNode } from '../components/nodes/FirehoseNode';
import { MskNode } from '../components/nodes/MskNode';
// Integration
import { AppSyncNode } from '../components/nodes/AppSyncNode';
import { MqNode } from '../components/nodes/MqNode';
import { AppFlowNode } from '../components/nodes/AppFlowNode';
// Management
import { CloudWatchNode } from '../components/nodes/CloudWatchNode';
import { XRayNode } from '../components/nodes/XRayNode';
import { CloudTrailNode } from '../components/nodes/CloudTrailNode';
import { SystemsManagerNode } from '../components/nodes/SystemsManagerNode';
// Developer
import { CodePipelineNode } from '../components/nodes/CodePipelineNode';
import { CodeBuildNode } from '../components/nodes/CodeBuildNode';
import { EcrNode } from '../components/nodes/EcrNode';
import { AmplifyNode } from '../components/nodes/AmplifyNode';
// Other
import { SesNode } from '../components/nodes/SesNode';
import { PinpointNode } from '../components/nodes/PinpointNode';
import { IotNode } from '../components/nodes/IotNode';
import { ApiGwWebSocketNode } from '../components/nodes/ApiGwWebSocketNode';

import { SecurityBadge } from '../components/nodes/SecurityBadge';
import type { NodeType } from '../lib/store';

// Minimal props factory for node components
const makeProps = (label: string, type: NodeType, selected = false) => ({
  id: 'test-id',
  type,
  selected,
  dragging: false,
  draggable: true,
  deletable: true,
  selectable: true,
  zIndex: 0,
  isConnectable: true,
  positionAbsoluteX: 0,
  positionAbsoluteY: 0,
  data: { label, type, config: undefined },
});

vi.mock('@xyflow/react', () => ({
  Handle: ({ type, position }: any) => <div data-testid={`handle-${type}`} data-position={position} />,
  Position: { Left: 'left', Right: 'right', Top: 'top', Bottom: 'bottom' },
  memo: (fn: any) => fn,
}));

describe('Node components', () => {
  const nodes: Array<{ Component: React.ComponentType<any>; label: string; type: NodeType; subtitle: string }> = [
    // Existing
    { Component: APINode, label: 'My API', type: 'api', subtitle: 'API Endpoint' },
    { Component: AuthNode, label: 'My Auth', type: 'auth', subtitle: 'Cognito' },
    { Component: CdnNode, label: 'My CDN', type: 'cdn', subtitle: 'CloudFront' },
    { Component: DatabaseNode, label: 'My DB', type: 'database', subtitle: 'DynamoDB' },
    { Component: EventsNode, label: 'My Events', type: 'events', subtitle: 'EventBridge' },
    { Component: FrontendNode, label: 'My Frontend', type: 'frontend', subtitle: 'Frontend' },
    { Component: LambdaNode, label: 'My Lambda', type: 'lambda', subtitle: 'Lambda' },
    { Component: NotificationNode, label: 'My SNS', type: 'notification', subtitle: 'SNS' },
    { Component: QueueNode, label: 'My Queue', type: 'queue', subtitle: 'SQS' },
    { Component: StorageNode, label: 'My Storage', type: 'storage', subtitle: 'S3' },
    { Component: StreamNode, label: 'My Stream', type: 'stream', subtitle: 'Kinesis' },
    { Component: WorkflowNode, label: 'My Workflow', type: 'workflow', subtitle: 'Step Functions' },
    // Compute
    { Component: Ec2Node, label: 'My EC2', type: 'ec2', subtitle: 'EC2 Instance' },
    { Component: EcsNode, label: 'My ECS', type: 'ecs', subtitle: 'ECS' },
    { Component: EksNode, label: 'My EKS', type: 'eks', subtitle: 'EKS' },
    { Component: FargateNode, label: 'My Fargate', type: 'fargate', subtitle: 'Fargate' },
    { Component: BatchNode, label: 'My Batch', type: 'batch', subtitle: 'AWS Batch' },
    { Component: AppRunnerNode, label: 'My AppRunner', type: 'apprunner', subtitle: 'App Runner' },
    { Component: LightsailNode, label: 'My Lightsail', type: 'lightsail', subtitle: 'Lightsail' },
    { Component: ElasticBeanstalkNode, label: 'My EB', type: 'elasticbeanstalk', subtitle: 'Elastic Beanstalk' },
    // Database
    { Component: RdsNode, label: 'My RDS', type: 'rds', subtitle: 'RDS' },
    { Component: AuroraNode, label: 'My Aurora', type: 'aurora', subtitle: 'Aurora' },
    { Component: ElastiCacheNode, label: 'My Cache', type: 'elasticache', subtitle: 'ElastiCache' },
    { Component: NeptuneNode, label: 'My Neptune', type: 'neptune', subtitle: 'Neptune' },
    { Component: DocumentDbNode, label: 'My DocDB', type: 'documentdb', subtitle: 'DocumentDB' },
    { Component: TimestreamNode, label: 'My TS', type: 'timestream', subtitle: 'Timestream' },
    { Component: RedshiftNode, label: 'My RS', type: 'redshift', subtitle: 'Redshift' },
    { Component: OpenSearchNode, label: 'My OS', type: 'opensearch', subtitle: 'OpenSearch' },
    // Storage
    { Component: EfsNode, label: 'My EFS', type: 'efs', subtitle: 'EFS' },
    { Component: EbsNode, label: 'My EBS', type: 'ebs', subtitle: 'EBS' },
    { Component: BackupNode, label: 'My Backup', type: 'backup', subtitle: 'AWS Backup' },
    // Networking
    { Component: VpcNode, label: 'My VPC', type: 'vpc', subtitle: 'VPC' },
    { Component: ElbNode, label: 'My ELB', type: 'elb', subtitle: 'Load Balancer' },
    { Component: Route53Node, label: 'My R53', type: 'route53', subtitle: 'Route 53' },
    { Component: NatGatewayNode, label: 'My NAT', type: 'natgateway', subtitle: 'NAT Gateway' },
    // Security
    { Component: WafNode, label: 'My WAF', type: 'waf', subtitle: 'WAF' },
    { Component: SecretsManagerNode, label: 'My SM', type: 'secretsmanager', subtitle: 'Secrets Manager' },
    { Component: KmsNode, label: 'My KMS', type: 'kms', subtitle: 'KMS' },
    { Component: IamNode, label: 'My IAM', type: 'iam', subtitle: 'IAM' },
    { Component: ShieldNode, label: 'My Shield', type: 'shield', subtitle: 'Shield' },
    { Component: GuardDutyNode, label: 'My GD', type: 'guardduty', subtitle: 'GuardDuty' },
    // ML/AI
    { Component: BedrockNode, label: 'My Bedrock', type: 'bedrock', subtitle: 'Bedrock' },
    { Component: SageMakerNode, label: 'My SM', type: 'sagemaker', subtitle: 'SageMaker' },
    { Component: RekognitionNode, label: 'My Rek', type: 'rekognition', subtitle: 'Rekognition' },
    // Analytics
    { Component: AthenaNode, label: 'My Athena', type: 'athena', subtitle: 'Athena' },
    { Component: GlueNode, label: 'My Glue', type: 'glue', subtitle: 'Glue' },
    { Component: QuickSightNode, label: 'My QS', type: 'quicksight', subtitle: 'QuickSight' },
    { Component: EmrNode, label: 'My EMR', type: 'emr', subtitle: 'EMR' },
    { Component: FirehoseNode, label: 'My FH', type: 'firehose', subtitle: 'Data Firehose' },
    { Component: MskNode, label: 'My MSK', type: 'msk', subtitle: 'MSK' },
    // Integration
    { Component: AppSyncNode, label: 'My AS', type: 'appsync', subtitle: 'AppSync' },
    { Component: MqNode, label: 'My MQ', type: 'mq', subtitle: 'Amazon MQ' },
    { Component: AppFlowNode, label: 'My AF', type: 'appflow', subtitle: 'AppFlow' },
    // Management
    { Component: CloudWatchNode, label: 'My CW', type: 'cloudwatch', subtitle: 'CloudWatch' },
    { Component: XRayNode, label: 'My XR', type: 'xray', subtitle: 'X-Ray' },
    { Component: CloudTrailNode, label: 'My CT', type: 'cloudtrail', subtitle: 'CloudTrail' },
    { Component: SystemsManagerNode, label: 'My SSM', type: 'systemsmanager', subtitle: 'Systems Manager' },
    // Developer
    { Component: CodePipelineNode, label: 'My CP', type: 'codepipeline', subtitle: 'CodePipeline' },
    { Component: CodeBuildNode, label: 'My CB', type: 'codebuild', subtitle: 'CodeBuild' },
    { Component: EcrNode, label: 'My ECR', type: 'ecr', subtitle: 'ECR' },
    { Component: AmplifyNode, label: 'My Amp', type: 'amplify', subtitle: 'Amplify' },
    // Other
    { Component: SesNode, label: 'My SES', type: 'ses', subtitle: 'SES' },
    { Component: PinpointNode, label: 'My PP', type: 'pinpoint', subtitle: 'Pinpoint' },
    { Component: IotNode, label: 'My IoT', type: 'iot', subtitle: 'IoT Core' },
    { Component: ApiGwWebSocketNode, label: 'My WS', type: 'apigw_websocket', subtitle: 'API GW WebSocket' },
  ];

  nodes.forEach(({ Component, label, type }) => {
    it(`${type}: renders label`, () => {
      render(<Component {...makeProps(label, type)} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    });

    it(`${type}: renders selected state`, () => {
      const { container } = render(<Component {...makeProps(label, type, true)} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });
});

describe('SecurityBadge', () => {
  it('renders nothing when no config', () => {
    const { container } = render(<SecurityBadge />);
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when config has no security flags', () => {
    const { container } = render(<SecurityBadge config={{}} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders badge when encryption is set', () => {
    const { container } = render(<SecurityBadge config={{ encryption: true }} />);
    expect(container.firstChild).not.toBeNull();
  });

  it('renders badge for all security flags', () => {
    const config = {
      encryption: true,
      vpc_enabled: true,
      waf_enabled: true,
      block_public_access: true,
      pitr: true,
      has_dlq: true,
      tracing: true,
      mfa: 'REQUIRED',
      security_headers: true,
    };
    const { container } = render(<SecurityBadge config={config} />);
    expect(container.firstChild).not.toBeNull();
  });
});
