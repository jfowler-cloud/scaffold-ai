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
import { useGraphStore, type AppNode, type LayoutType } from "@/lib/store";
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
        <Panel position="top-left" className="flex gap-1 bg-white/90 rounded-lg p-2 shadow-sm">
          <button
            onClick={() => applyLayout("horizontal")}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-1"
            title="Horizontal Flow"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
            Horizontal
          </button>
          <button
            onClick={() => applyLayout("vertical")}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-1"
            title="Vertical Flow"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            Vertical
          </button>
          <button
            onClick={() => applyLayout("grid")}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-1"
            title="Grid Layout"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Grid
          </button>
          <button
            onClick={() => applyLayout("circular")}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-1"
            title="Circular Layout"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Circular
          </button>
        </Panel>
        <Panel position="top-right" className="flex gap-2 flex-wrap max-w-md justify-end">
          <button
            onClick={() => handleAddNode("frontend")}
            className="px-3 py-1.5 text-sm bg-cyan-500 text-white rounded hover:bg-cyan-600"
          >
            + Frontend
          </button>
          <button
            onClick={() => handleAddNode("auth")}
            className="px-3 py-1.5 text-sm bg-emerald-500 text-white rounded hover:bg-emerald-600"
          >
            + Auth
          </button>
          <button
            onClick={() => handleAddNode("api")}
            className="px-3 py-1.5 text-sm bg-amber-500 text-white rounded hover:bg-amber-600"
          >
            + API
          </button>
          <button
            onClick={() => handleAddNode("lambda")}
            className="px-3 py-1.5 text-sm bg-violet-500 text-white rounded hover:bg-violet-600"
          >
            + Lambda
          </button>
          <button
            onClick={() => handleAddNode("database")}
            className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            + Database
          </button>
          <button
            onClick={() => handleAddNode("storage")}
            className="px-3 py-1.5 text-sm bg-pink-500 text-white rounded hover:bg-pink-600"
          >
            + Storage
          </button>
        </Panel>
      </ReactFlow>
    </div>
  );
}
