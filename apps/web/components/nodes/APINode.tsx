"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const APINode = memo(function APINode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${selected ? "border-amber-500 ring-2 ring-amber-200" : "border-amber-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-amber-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-amber-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">API Endpoint</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-amber-500" />
    </div>
  );
});
