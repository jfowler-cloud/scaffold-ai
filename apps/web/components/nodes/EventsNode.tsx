"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const EventsNode = memo(function EventsNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${selected ? "border-rose-500 ring-2 ring-rose-200" : "border-rose-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-rose-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-rose-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">EventBridge</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-rose-500" />
    </div>
  );
});
