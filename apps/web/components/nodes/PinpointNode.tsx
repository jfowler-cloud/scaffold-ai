
import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const PinpointNode = memo(function PinpointNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white dark:bg-zinc-800 shadow-md min-w-[150px] ${selected ? "border-rose-500 ring-2 ring-rose-200" : "border-rose-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-rose-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-rose-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900 dark:text-gray-100">{data.label}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Pinpoint</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-rose-500" />
    </div>
  );
});
