import { create } from "zustand";
import type { Edge, Node } from "@xyflow/react";

export type NodeType = "character" | "image" | "video" | "prompt" | "note";

export interface FlowboardNodeData extends Record<string, unknown> {
  type: NodeType;
  shortId: string;
  title: string;
  status?: "idle" | "queued" | "running" | "done" | "error";
  prompt?: string;
  thumbnailUrl?: string;
}

export type FlowNode = Node<FlowboardNodeData>;

const seedNodes: FlowNode[] = [
  {
    id: "seed-1",
    type: "note",
    position: { x: 0, y: 0 },
    data: {
      type: "note",
      shortId: "0001",
      title: "Welcome",
      prompt: "Phase 0 skeleton. Canvas lives here.",
    },
  },
];

interface BoardState {
  nodes: FlowNode[];
  edges: Edge[];
  setNodes: (nodes: FlowNode[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: FlowNode) => void;
}

export const useBoardStore = create<BoardState>((set) => ({
  nodes: seedNodes,
  edges: [],
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  addNode: (node) => set((s) => ({ nodes: [...s.nodes, node] })),
}));
