"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";
import { SecurityBadge } from "./SecurityBadge";

export const NotificationNode = memo(function NotificationNode({ data, selected }: NodeProps<AppNode>) {
  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${selected ? "border-red-500 ring-2 ring-red-200" : "border-red-300"}`}>
      <SecurityBadge config={data.config} />
      <Handle type="target" position={Position.Left} className="!bg-red-500" />
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-red-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">SNS Topic</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-red-500" />
    </div>
  );
});
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected ? "border-red-500 ring-2 ring-red-200" : "border-red-300"
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-red-500" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-red-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">SNS Topic</div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-red-500" />
    </div>
  );
});
