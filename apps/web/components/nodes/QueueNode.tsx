"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const QueueNode = memo(function QueueNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${selected ? "border-orange-500 ring-2 ring-orange-200" : "border-orange-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-orange-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-orange-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">SQS Queue</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-orange-500" />
    </div>
  );
});
