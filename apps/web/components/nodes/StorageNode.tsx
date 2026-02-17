"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";

export const StorageNode = memo(function StorageNode({
  data,
  selected,
}: NodeProps<AppNode>) {
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected ? "border-pink-500 ring-2 ring-pink-200" : "border-pink-300"
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-pink-500" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-pink-100 flex items-center justify-center">
          <svg
            className="w-5 h-5 text-pink-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
            />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">S3 Storage</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-pink-500"
      />
    </div>
  );
});
