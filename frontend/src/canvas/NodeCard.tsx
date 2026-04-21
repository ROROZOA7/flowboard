import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { FlowboardNodeData } from "../store/board";

const ICON: Record<string, string> = {
  character: "◎",
  image: "▣",
  video: "▶",
  prompt: "✦",
  note: "✎",
};

export function NodeCard(props: NodeProps) {
  const data = props.data as FlowboardNodeData;
  return (
    <div className="node-card">
      <Handle type="target" position={Position.Left} />
      <div className="title">
        <span>{ICON[data.type] ?? "□"}</span>
        <span>{data.title}</span>
        <span className="short-id" style={{ marginLeft: "auto" }}>
          #{data.shortId}
        </span>
      </div>
      {data.prompt && (
        <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 8 }}>
          {data.prompt}
        </div>
      )}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
