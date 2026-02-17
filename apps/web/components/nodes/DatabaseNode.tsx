"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";

export const DatabaseNode = memo(function DatabaseNode({
  data,
  selected,
}: NodeProps<AppNode>) {
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected ? "border-blue-500 ring-2 ring-blue-200" : "border-blue-300"
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-blue-500" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-blue-100 flex items-center justify-center">
          <svg
            className="w-5 h-5 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
            />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">Database</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-500"
      />
    </div>
  );
});
