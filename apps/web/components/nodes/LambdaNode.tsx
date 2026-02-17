"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";

export const LambdaNode = memo(function LambdaNode({
  data,
  selected,
}: NodeProps<AppNode>) {
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected
          ? "border-violet-500 ring-2 ring-violet-200"
          : "border-violet-300"
      }`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-violet-500"
      />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-violet-100 flex items-center justify-center">
          <svg
            className="w-5 h-5 text-violet-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">Lambda</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-violet-500"
      />
    </div>
  );
});
