
import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const LightsailNode = memo(function LightsailNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white dark:bg-zinc-800 shadow-md min-w-[150px] ${selected ? "border-violet-500 ring-2 ring-violet-200" : "border-violet-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-violet-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-violet-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900 dark:text-gray-100">{data.label}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Lightsail</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-violet-500" />
    </div>
  );
});
