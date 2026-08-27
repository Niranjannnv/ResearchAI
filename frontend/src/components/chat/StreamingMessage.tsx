"use client";

import React from "react";
import { Sparkles } from "lucide-react";

interface StreamingMessageProps {
  status: string | null;
  activeAgents?: string[];
}

export function StreamingMessage({ status }: StreamingMessageProps) {
  const defaultStatus = "Synthesizing research literature...";

  return (
    <div className="flex items-center gap-3 py-5 px-4 text-sm text-gray-600">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200/50 shadow-xs">
        <Sparkles className="h-3.5 w-3.5 animate-pulse text-emerald-600" />
      </div>

      <div className="flex items-center gap-2">
        <span className="text-gray-800 font-medium">{status || defaultStatus}</span>
        <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
      </div>
    </div>
  );
}
