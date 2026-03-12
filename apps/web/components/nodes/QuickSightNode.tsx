
import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const QuickSightNode = memo(function QuickSightNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white dark:bg-zinc-800 shadow-md min-w-[150px] ${selected ? "border-teal-500 ring-2 ring-teal-200" : "border-teal-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-teal-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-teal-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900 dark:text-gray-100">{data.label}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">QuickSight</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-teal-500" />
    </div>
  );
});
