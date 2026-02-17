"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";

export const AuthNode = memo(function AuthNode({
  data,
  selected,
}: NodeProps<AppNode>) {
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected
          ? "border-emerald-500 ring-2 ring-emerald-200"
          : "border-emerald-300"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-emerald-500"
      />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-emerald-100 flex items-center justify-center">
          <svg
            className="w-5 h-5 text-emerald-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">Authentication</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-emerald-500"
      />
    </div>
  );
});
