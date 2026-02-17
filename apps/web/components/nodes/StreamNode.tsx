"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNode } from "@/lib/store";

export const StreamNode = memo(function StreamNode({
  data,
  selected,
}: NodeProps<AppNode>) {
  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[150px] ${
        selected ? "border-teal-500 ring-2 ring-teal-200" : "border-teal-300"
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-teal-500" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-teal-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
        </div>
        <div>
          <div className="font-medium text-sm text-gray-900">{data.label}</div>
          <div className="text-xs text-gray-500">Kinesis Stream</div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-teal-500" />
    </div>
  );
});
