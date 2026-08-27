"use client";

import React from "react";

interface StreamingMessageProps {
  status: string | null;
  activeAgents?: string[];
}

export function StreamingMessage({ status }: StreamingMessageProps) {
  // Strip any accidental emojis or punctuation clutter
  const rawStatus = status || "Searching academic databases and literature";
  const cleanStatus = rawStatus.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}]/gu, "").trim();

  return (
    <div className="py-4 px-2">
      <div className="flex items-center gap-3">
        {/* Subtle pulsing status dot */}
        <div className="relative flex h-3 w-3 items-center justify-center">
          <span className="absolute h-full w-full rounded-full bg-emerald-500 opacity-60 animate-ping" />
          <span className="relative h-2 w-2 rounded-full bg-emerald-600" />
        </div>

        {/* Clean status text */}
        <span className="text-sm font-medium text-gray-700 tracking-tight">
          {cleanStatus}
        </span>
      </div>

      {/* Sleek minimal progress line */}
      <div className="mt-2.5 h-0.5 w-48 overflow-hidden rounded-full bg-gray-100">
        <div className="h-full w-full bg-emerald-600 animate-[progress_1.6s_ease-in-out_infinite]" />
      </div>

      <style jsx>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          50% { transform: translateX(0%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}
