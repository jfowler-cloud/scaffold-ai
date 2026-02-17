"use client";

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
import Button from "@cloudscape-design/components/button";
import ButtonDropdown from "@cloudscape-design/components/button-dropdown";
import SpaceBetween from "@cloudscape-design/components/space-between";

const nodeTypes = {
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
};

const nodeColors: Record<string, string> = {
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
          <div style={{ backgroundColor: "white", borderRadius: "8px", padding: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
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
          <div style={{ backgroundColor: "white", borderRadius: "8px", padding: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <SpaceBetween direction="horizontal" size="xs">
              <ButtonDropdown
                variant="primary"
                items={[
                  { id: "frontend", text: "Frontend", description: "Next.js/React app" },
                  { id: "auth", text: "Auth", description: "Cognito User Pool" },
                  { id: "api", text: "API", description: "API Gateway" },
                  { id: "lambda", text: "Lambda", description: "Serverless function" },
                  { id: "database", text: "Database", description: "DynamoDB table" },
                  { id: "storage", text: "Storage", description: "S3 bucket" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                Add Service
              </ButtonDropdown>
              <ButtonDropdown
                items={[
                  { id: "queue", text: "Queue", description: "SQS queue" },
                  { id: "events", text: "Events", description: "EventBridge" },
                  { id: "notification", text: "Notification", description: "SNS topic" },
                  { id: "workflow", text: "Workflow", description: "Step Functions" },
                  { id: "cdn", text: "CDN", description: "CloudFront" },
                  { id: "stream", text: "Stream", description: "Kinesis stream" },
                ]}
                onItemClick={({ detail }) => handleAddNode(detail.id as AppNode["data"]["type"])}
              >
                More Services
              </ButtonDropdown>
            </SpaceBetween>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
