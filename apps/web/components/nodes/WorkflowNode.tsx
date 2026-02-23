"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const WorkflowNode = memo(function WorkflowNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${selected ? "border-indigo-500 ring-2 ring-indigo-200" : "border-indigo-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-indigo-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-indigo-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">Step Functions</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-indigo-500" />
    </div>
  );
});
