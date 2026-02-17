import { create } from "zustand";
import { Node, Edge, addEdge, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import type { NodeChange, EdgeChange, Connection } from "@xyflow/react";

export type NodeType = "database" | "auth" | "api" | "frontend" | "storage";

export interface AppNode extends Node {
  data: {
    label: string;
    type: NodeType;
    config?: Record<string, unknown>;
  };
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
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,

  addMessage: (message) => {
    set({ messages: [...get().messages, message] });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  clearMessages: () => {
    set({ messages: [] });
  },
}));
