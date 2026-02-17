"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useGraphStore, type AppNode } from "@/lib/store";
import { DatabaseNode } from "./nodes/DatabaseNode";
import { AuthNode } from "./nodes/AuthNode";
import { APINode } from "./nodes/APINode";

const nodeTypes = {
  database: DatabaseNode,
  auth: AuthNode,
  api: APINode,
};

const nodeColors: Record<string, string> = {
  database: "#3b82f6",
  auth: "#10b981",
  api: "#f59e0b",
  frontend: "#8b5cf6",
  storage: "#ec4899",
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

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => nodeColors[node.type ?? ""] ?? "#6b7280"}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
        <Panel position="top-right" className="flex gap-2">
          <button
            onClick={() => handleAddNode("database")}
            className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            + Database
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
        </Panel>
      </ReactFlow>
    </div>
  );
}
