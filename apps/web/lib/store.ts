import { create } from "zustand";
import { Node, Edge, addEdge, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import type { NodeChange, EdgeChange, Connection } from "@xyflow/react";

export type NodeType =
  | "database"
  | "auth"
  | "api"
  | "frontend"
  | "storage"
  | "lambda"
  | "queue"
  | "events"
  | "notification"
  | "workflow"
  | "cdn"
  | "stream";

export type LayoutType = "horizontal" | "vertical" | "grid" | "circular";

export interface AppNode extends Node {
  data: {
    label: string;
    type: NodeType;
    config?: Record<string, unknown>;
  };
}

export interface GeneratedFile {
  path: string;
  content: string;
}

interface GraphState {
  nodes: AppNode[];
  edges: Edge[];
  selectedNode: AppNode | null;

  // Actions
  onNodesChange: (changes: NodeChange<AppNode>[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: (node: AppNode) => void;
  updateNode: (id: string, data: Partial<AppNode["data"]>) => void;
  removeNode: (id: string) => void;
  setSelectedNode: (node: AppNode | null) => void;
  setGraph: (nodes: AppNode[], edges: Edge[]) => void;
  getGraphJSON: () => { nodes: AppNode[]; edges: Edge[] };
  applyLayout: (layout: LayoutType) => void;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes) as AppNode[],
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },

  addNode: (node) => {
    set({
      nodes: [...get().nodes, node],
    });
  },

  updateNode: (id, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, ...data } } : node
      ),
    });
  },

  removeNode: (id) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== id),
      edges: get().edges.filter(
        (edge) => edge.source !== id && edge.target !== id
      ),
    });
  },

  setSelectedNode: (node) => {
    set({ selectedNode: node });
  },

  setGraph: (nodes, edges) => {
    set({ nodes, edges });
  },

  getGraphJSON: () => {
    const { nodes, edges } = get();
    return { nodes, edges };
  },

  applyLayout: (layout: LayoutType) => {
    const { nodes } = get();
    if (nodes.length === 0) return;

    const SPACING_X = 350;
    const SPACING_Y = 220;
    const START_X = 50;
    const START_Y = 50;

    // Group nodes by type for type-based layouts (serverless flow)
    const typeOrder: Record<string, number> = {
      frontend: 0,
      cdn: 0,
      auth: 1,
      api: 2,
      lambda: 3,
      workflow: 3,
      queue: 4,
      events: 4,
      notification: 4,
      stream: 5,
      database: 6,
      storage: 6,
    };

    let newNodes: AppNode[];

    switch (layout) {
      case "horizontal": {
        // Group by type, flow left to right
        const byType: Record<number, AppNode[]> = {};
        nodes.forEach((node) => {
          const col = typeOrder[node.data.type] ?? 2;
          if (!byType[col]) byType[col] = [];
          byType[col].push(node);
        });

        newNodes = nodes.map((node) => {
          const col = typeOrder[node.data.type] ?? 2;
          const row = byType[col].indexOf(node);
          return {
            ...node,
            position: {
              x: START_X + col * SPACING_X,
              y: START_Y + row * SPACING_Y,
            },
          };
        });
        break;
      }

      case "vertical": {
        // Group by type, flow top to bottom
        const byType: Record<number, AppNode[]> = {};
        nodes.forEach((node) => {
          const row = typeOrder[node.data.type] ?? 2;
          if (!byType[row]) byType[row] = [];
          byType[row].push(node);
        });

        newNodes = nodes.map((node) => {
          const row = typeOrder[node.data.type] ?? 2;
          const col = byType[row].indexOf(node);
          return {
            ...node,
            position: {
              x: START_X + col * SPACING_X,
              y: START_Y + row * SPACING_Y,
            },
          };
        });
        break;
      }

      case "grid": {
        // Simple grid layout
        const cols = Math.ceil(Math.sqrt(nodes.length));
        newNodes = nodes.map((node, i) => ({
          ...node,
          position: {
            x: START_X + (i % cols) * SPACING_X,
            y: START_Y + Math.floor(i / cols) * SPACING_Y,
          },
        }));
        break;
      }

      case "circular": {
        // Circular layout
        const centerX = 400;
        const centerY = 300;
        const radius = Math.max(200, nodes.length * 40);
        newNodes = nodes.map((node, i) => {
          const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
          return {
            ...node,
            position: {
              x: centerX + radius * Math.cos(angle),
              y: centerY + radius * Math.sin(angle),
            },
          };
        });
        break;
      }

      default:
        return;
    }

    set({ nodes: newNodes });
  },
}));

// Chat state
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  generatedFiles: GeneratedFile[];
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  setGeneratedFiles: (files: GeneratedFile[]) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  generatedFiles: [],

  addMessage: (message) => {
    set({ messages: [...get().messages, message] });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setGeneratedFiles: (files) => {
    set({ generatedFiles: files });
  },

  clearMessages: () => {
    set({ messages: [] });
  },
}));
