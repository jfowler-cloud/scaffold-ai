
import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  BackgroundVariant,
  MarkerType,
  type DefaultEdgeOptions,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useGraphStore, type AppNode } from "@/lib/store";
import { DatabaseNode } from "./nodes/DatabaseNode";
import { AuthNode } from "./nodes/AuthNode";
import { APINode } from "./nodes/APINode";
import { LambdaNode } from "./nodes/LambdaNode";
import { StorageNode } from "./nodes/StorageNode";
import { FrontendNode } from "./nodes/FrontendNode";
import { QueueNode } from "./nodes/QueueNode";
import { EventsNode } from "./nodes/EventsNode";
import { NotificationNode } from "./nodes/NotificationNode";
import { WorkflowNode } from "./nodes/WorkflowNode";
import { CdnNode } from "./nodes/CdnNode";
import { StreamNode } from "./nodes/StreamNode";
// Compute
import { Ec2Node } from "./nodes/Ec2Node";
import { EcsNode } from "./nodes/EcsNode";
import { EksNode } from "./nodes/EksNode";
import { FargateNode } from "./nodes/FargateNode";
import { BatchNode } from "./nodes/BatchNode";
import { AppRunnerNode } from "./nodes/AppRunnerNode";
import { LightsailNode } from "./nodes/LightsailNode";
import { ElasticBeanstalkNode } from "./nodes/ElasticBeanstalkNode";
// Database
import { RdsNode } from "./nodes/RdsNode";
import { AuroraNode } from "./nodes/AuroraNode";
import { ElastiCacheNode } from "./nodes/ElastiCacheNode";
import { NeptuneNode } from "./nodes/NeptuneNode";
import { DocumentDbNode } from "./nodes/DocumentDbNode";
import { TimestreamNode } from "./nodes/TimestreamNode";
import { RedshiftNode } from "./nodes/RedshiftNode";
import { OpenSearchNode } from "./nodes/OpenSearchNode";
// Storage
import { EfsNode } from "./nodes/EfsNode";
import { EbsNode } from "./nodes/EbsNode";
import { BackupNode } from "./nodes/BackupNode";
// Networking
import { VpcNode } from "./nodes/VpcNode";
import { ElbNode } from "./nodes/ElbNode";
import { Route53Node } from "./nodes/Route53Node";
import { NatGatewayNode } from "./nodes/NatGatewayNode";
// Security
import { WafNode } from "./nodes/WafNode";
import { SecretsManagerNode } from "./nodes/SecretsManagerNode";
import { KmsNode } from "./nodes/KmsNode";
import { IamNode } from "./nodes/IamNode";
import { ShieldNode } from "./nodes/ShieldNode";
import { GuardDutyNode } from "./nodes/GuardDutyNode";
// ML/AI
import { BedrockNode } from "./nodes/BedrockNode";
import { SageMakerNode } from "./nodes/SageMakerNode";
import { RekognitionNode } from "./nodes/RekognitionNode";
// Analytics
import { AthenaNode } from "./nodes/AthenaNode";
import { GlueNode } from "./nodes/GlueNode";
import { QuickSightNode } from "./nodes/QuickSightNode";
import { EmrNode } from "./nodes/EmrNode";
import { FirehoseNode } from "./nodes/FirehoseNode";
import { MskNode } from "./nodes/MskNode";
// Integration
import { AppSyncNode } from "./nodes/AppSyncNode";
import { MqNode } from "./nodes/MqNode";
import { AppFlowNode } from "./nodes/AppFlowNode";
// Management
import { CloudWatchNode } from "./nodes/CloudWatchNode";
import { XRayNode } from "./nodes/XRayNode";
import { CloudTrailNode } from "./nodes/CloudTrailNode";
import { SystemsManagerNode } from "./nodes/SystemsManagerNode";
// Developer
import { CodePipelineNode } from "./nodes/CodePipelineNode";
import { CodeBuildNode } from "./nodes/CodeBuildNode";
import { EcrNode } from "./nodes/EcrNode";
import { AmplifyNode } from "./nodes/AmplifyNode";
// Other
import { SesNode } from "./nodes/SesNode";
import { PinpointNode } from "./nodes/PinpointNode";
import { IotNode } from "./nodes/IotNode";
import { ApiGwWebSocketNode } from "./nodes/ApiGwWebSocketNode";

import ButtonDropdown from "@cloudscape-design/components/button-dropdown";
import SpaceBetween from "@cloudscape-design/components/space-between";

const nodeTypes = {
  // Existing
  database: DatabaseNode,
  auth: AuthNode,
  api: APINode,
  lambda: LambdaNode,
  storage: StorageNode,
  frontend: FrontendNode,
  queue: QueueNode,
  events: EventsNode,
  notification: NotificationNode,
  workflow: WorkflowNode,
  cdn: CdnNode,
  stream: StreamNode,
  // Compute
  ec2: Ec2Node,
  ecs: EcsNode,
  eks: EksNode,
  fargate: FargateNode,
  batch: BatchNode,
  apprunner: AppRunnerNode,
  lightsail: LightsailNode,
  elasticbeanstalk: ElasticBeanstalkNode,
  // Database
  rds: RdsNode,
  aurora: AuroraNode,
  elasticache: ElastiCacheNode,
  neptune: NeptuneNode,
  documentdb: DocumentDbNode,
  timestream: TimestreamNode,
  redshift: RedshiftNode,
  opensearch: OpenSearchNode,
  // Storage
  efs: EfsNode,
  ebs: EbsNode,
  backup: BackupNode,
  // Networking
  vpc: VpcNode,
  elb: ElbNode,
  route53: Route53Node,
  natgateway: NatGatewayNode,
  // Security
  waf: WafNode,
  secretsmanager: SecretsManagerNode,
  kms: KmsNode,
  iam: IamNode,
  shield: ShieldNode,
  guardduty: GuardDutyNode,
  // ML/AI
  bedrock: BedrockNode,
  sagemaker: SageMakerNode,
  rekognition: RekognitionNode,
  // Analytics
  athena: AthenaNode,
  glue: GlueNode,
  quicksight: QuickSightNode,
  emr: EmrNode,
  firehose: FirehoseNode,
  msk: MskNode,
  // Integration
  appsync: AppSyncNode,
  mq: MqNode,
  appflow: AppFlowNode,
  // Management
  cloudwatch: CloudWatchNode,
  xray: XRayNode,
  cloudtrail: CloudTrailNode,
  systemsmanager: SystemsManagerNode,
  // Developer
  codepipeline: CodePipelineNode,
  codebuild: CodeBuildNode,
  ecr: EcrNode,
  amplify: AmplifyNode,
  // Other
  ses: SesNode,
  pinpoint: PinpointNode,
  iot: IotNode,
  apigw_websocket: ApiGwWebSocketNode,
};

const nodeColors: Record<string, string> = {
  // Existing
  database: "#3b82f6",
  auth: "#10b981",
  api: "#f59e0b",
  lambda: "#8b5cf6",
  storage: "#ec4899",
  frontend: "#06b6d4",
  queue: "#f97316",
  events: "#f43f5e",
  notification: "#ef4444",
  workflow: "#6366f1",
  cdn: "#0ea5e9",
  stream: "#14b8a6",
  // Compute (violet / lime)
  ec2: "#8b5cf6",
  ecs: "#84cc16",
  eks: "#84cc16",
  fargate: "#84cc16",
  batch: "#8b5cf6",
  apprunner: "#8b5cf6",
  lightsail: "#8b5cf6",
  elasticbeanstalk: "#8b5cf6",
  // Database (blue)
  rds: "#3b82f6",
  aurora: "#3b82f6",
  elasticache: "#3b82f6",
  neptune: "#3b82f6",
  documentdb: "#3b82f6",
  timestream: "#3b82f6",
  redshift: "#3b82f6",
  opensearch: "#3b82f6",
  // Storage (pink)
  efs: "#ec4899",
  ebs: "#ec4899",
  backup: "#ec4899",
  // Networking (amber)
  vpc: "#f59e0b",
  elb: "#f59e0b",
  route53: "#f59e0b",
  natgateway: "#f59e0b",
  // Security (green)
  waf: "#22c55e",
  secretsmanager: "#22c55e",
  kms: "#22c55e",
  iam: "#22c55e",
  shield: "#22c55e",
  guardduty: "#22c55e",
  // ML/AI (emerald)
  bedrock: "#10b981",
  sagemaker: "#10b981",
  rekognition: "#10b981",
  // Analytics (teal)
  athena: "#14b8a6",
  glue: "#14b8a6",
  quicksight: "#14b8a6",
  emr: "#14b8a6",
  firehose: "#14b8a6",
  msk: "#14b8a6",
  // Integration (indigo / orange)
  appsync: "#6366f1",
  mq: "#f97316",
  appflow: "#6366f1",
  // Management (slate)
  cloudwatch: "#64748b",
  xray: "#64748b",
  cloudtrail: "#64748b",
  systemsmanager: "#64748b",
  // Developer (sky)
  codepipeline: "#0ea5e9",
  codebuild: "#0ea5e9",
  ecr: "#0ea5e9",
  amplify: "#0ea5e9",
  // Other (rose / amber)
  ses: "#f43f5e",
  pinpoint: "#f43f5e",
  iot: "#f59e0b",
  apigw_websocket: "#f59e0b",
};

const defaultEdgeOptions: DefaultEdgeOptions = {
  type: "smoothstep",
  animated: true,
  style: {
    strokeWidth: 2,
    stroke: "#94a3b8",
  },
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: "#94a3b8",
    width: 20,
    height: 20,
  },
};

export function Canvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    setSelectedNode,
    applyLayout,
  } = useGraphStore();

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: AppNode) => {
      setSelectedNode(node);
    },
    [setSelectedNode]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  const handleAddNode = (type: AppNode["data"]["type"]) => {
    const newNode: AppNode = {
      id: `${type}-${Date.now()}`,
      type,
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
        type,
      },
    };
    addNode(newNode);
  };

  // Apply default edge options to all edges
  const styledEdges = useMemo(() => {
    return edges.map((edge) => ({
      ...edge,
      type: "smoothstep",
      animated: true,
      style: {
        strokeWidth: 2,
        stroke: "#94a3b8",
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: "#94a3b8",
        width: 20,
        height: 20,
      },
    }));
  }, [edges]);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={styledEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        className="bg-background"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => nodeColors[node.type ?? ""] ?? "#6b7280"}
          maskColor="rgba(0, 0, 0, 0.1)"
        />

        {/* Layout Controls - Top Left */}
        <Panel position="top-left">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-2 shadow-sm border border-transparent dark:border-zinc-700">
            <SpaceBetween direction="horizontal" size="xs">
              <ButtonDropdown
                items={[
                  { id: "horizontal", text: "Horizontal Flow", iconName: "angle-right" },
                  { id: "vertical", text: "Vertical Flow", iconName: "angle-down" },
                  { id: "grid", text: "Grid Layout", iconName: "view-full" },
                  { id: "circular", text: "Circular Layout", iconName: "status-positive" },
                ]}
                onItemClick={({ detail }) => applyLayout(detail.id as "horizontal" | "vertical" | "grid" | "circular")}
              >
                Layout
              </ButtonDropdown>
            </SpaceBetween>
          </div>
        </Panel>

        {/* Add Node Controls - Top Right */}
        <Panel position="top-right">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-2 shadow-sm border border-transparent dark:border-zinc-700">
            <SpaceBetween direction="horizontal" size="xs">
              <ButtonDropdown
                variant="primary"
                items={[
                  { id: "lambda", text: "Lambda", description: "Serverless function" },
                  { id: "ec2", text: "EC2", description: "Virtual server" },
                  { id: "ecs", text: "ECS", description: "Container service" },
                  { id: "eks", text: "EKS", description: "Kubernetes" },
                  { id: "fargate", text: "Fargate", description: "Serverless containers" },
                  { id: "batch", text: "Batch", description: "Batch processing" },
                  { id: "apprunner", text: "App Runner", description: "Container web apps" },
                  { id: "lightsail", text: "Lightsail", description: "Simple VPS" },
                  { id: "elasticbeanstalk", text: "Elastic Beanstalk", description: "Deploy web apps" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Compute
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "database", text: "DynamoDB", description: "NoSQL database" },
                  { id: "rds", text: "RDS", description: "Relational database" },
                  { id: "aurora", text: "Aurora", description: "MySQL/PostgreSQL" },
                  { id: "elasticache", text: "ElastiCache", description: "In-memory cache" },
                  { id: "neptune", text: "Neptune", description: "Graph database" },
                  { id: "documentdb", text: "DocumentDB", description: "Document database" },
                  { id: "timestream", text: "Timestream", description: "Time-series DB" },
                  { id: "redshift", text: "Redshift", description: "Data warehouse" },
                  { id: "opensearch", text: "OpenSearch", description: "Search & analytics" },
                  { id: "storage", text: "S3", description: "Object storage" },
                  { id: "efs", text: "EFS", description: "File system" },
                  { id: "ebs", text: "EBS", description: "Block storage" },
                  { id: "backup", text: "AWS Backup", description: "Backup service" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Database & Storage
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "api", text: "API Gateway", description: "REST API" },
                  { id: "apigw_websocket", text: "API GW WebSocket", description: "WebSocket API" },
                  { id: "appsync", text: "AppSync", description: "GraphQL API" },
                  { id: "cdn", text: "CloudFront", description: "CDN" },
                  { id: "frontend", text: "Frontend", description: "React + Vite SPA" },
                  { id: "vpc", text: "VPC", description: "Virtual network" },
                  { id: "elb", text: "Load Balancer", description: "ELB/ALB/NLB" },
                  { id: "route53", text: "Route 53", description: "DNS" },
                  { id: "natgateway", text: "NAT Gateway", description: "NAT Gateway" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Networking & CDN
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "auth", text: "Cognito", description: "User authentication" },
                  { id: "iam", text: "IAM", description: "Identity & access" },
                  { id: "waf", text: "WAF", description: "Web app firewall" },
                  { id: "shield", text: "Shield", description: "DDoS protection" },
                  { id: "guardduty", text: "GuardDuty", description: "Threat detection" },
                  { id: "kms", text: "KMS", description: "Key management" },
                  { id: "secretsmanager", text: "Secrets Manager", description: "Secrets store" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Security & Auth
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "workflow", text: "Step Functions", description: "Workflow orchestration" },
                  { id: "events", text: "EventBridge", description: "Event bus" },
                  { id: "queue", text: "SQS", description: "Message queue" },
                  { id: "notification", text: "SNS", description: "Push notifications" },
                  { id: "ses", text: "SES", description: "Email service" },
                  { id: "pinpoint", text: "Pinpoint", description: "Customer engagement" },
                  { id: "mq", text: "Amazon MQ", description: "Message broker" },
                  { id: "appflow", text: "AppFlow", description: "SaaS integration" },
                  { id: "iot", text: "IoT Core", description: "IoT messaging" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Integration & Messaging
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "stream", text: "Kinesis", description: "Data streaming" },
                  { id: "firehose", text: "Data Firehose", description: "Data delivery" },
                  { id: "msk", text: "MSK", description: "Managed Kafka" },
                  { id: "athena", text: "Athena", description: "SQL query service" },
                  { id: "glue", text: "Glue", description: "ETL service" },
                  { id: "quicksight", text: "QuickSight", description: "BI dashboards" },
                  { id: "emr", text: "EMR", description: "Big data processing" },
                  { id: "bedrock", text: "Bedrock", description: "Foundation models" },
                  { id: "sagemaker", text: "SageMaker", description: "ML platform" },
                  { id: "rekognition", text: "Rekognition", description: "Image analysis" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Analytics & ML
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "cloudwatch", text: "CloudWatch", description: "Monitoring" },
                  { id: "xray", text: "X-Ray", description: "Distributed tracing" },
                  { id: "cloudtrail", text: "CloudTrail", description: "API audit logs" },
                  { id: "systemsmanager", text: "Systems Manager", description: "Ops management" },
                  { id: "codepipeline", text: "CodePipeline", description: "CI/CD pipeline" },
                  { id: "codebuild", text: "CodeBuild", description: "Build service" },
                  { id: "ecr", text: "ECR", description: "Container registry" },
                  { id: "amplify", text: "Amplify", description: "Full-stack platform" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                DevOps & Monitoring
              </ButtonDropdown>
            </SpaceBetween>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
