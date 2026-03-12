
import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const EfsNode = memo(function EfsNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white dark:bg-zinc-800 shadow-md min-w-[150px] ${selected ? "border-pink-500 ring-2 ring-pink-200" : "border-pink-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-pink-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-pink-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900 dark:text-gray-100">{data.label}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">EFS</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-pink-500" />
    </div>
  );
});
