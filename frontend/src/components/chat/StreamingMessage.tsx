"use client";

import React from "react";
import { Sparkles, Loader2, BookOpen } from "lucide-react";

interface StreamingMessageProps {
  status: string | null;
  activeAgents: string[];
}

export function StreamingMessage({ status, activeAgents }: StreamingMessageProps) {
  const defaultStatus = "Searching across academic databases and trusted sources...";

  return (
    <div className="flex gap-4 py-6 border-b border-gray-100 bg-emerald-50/20 px-6 rounded-2xl">
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-emerald-600 text-white shadow-xs">
        <Sparkles className="h-4 w-4 animate-spin" />
      </div>

      <div className="flex-1 space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
            ResearchAI
          </span>
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
        </div>

        <div className="flex items-center gap-2.5 text-sm font-medium text-gray-800">
          <Loader2 className="h-4 w-4 animate-spin text-emerald-600 shrink-0" />
          <span>{status || defaultStatus}</span>
        </div>

        {/* Data source indicators — friendly labels only */}
        <div className="rounded-xl border border-emerald-100 bg-white/80 p-3 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-medium text-gray-500">
            <span className="flex items-center gap-1">
              <BookOpen className="h-3 w-3 text-emerald-600" />
              Searching trusted sources
            </span>
            <span className="text-emerald-700 font-semibold">In progress</span>
          </div>

          <div className="flex flex-wrap gap-1.5 pt-1">
            {[
              "Academic Papers",
              "Medical Research",
              "Web & News",
              "Books & Reports",
              "Official Statistics",
            ].map((label) => (
              <div
                key={label}
                className="flex items-center gap-1 text-[11px] bg-emerald-50/80 text-emerald-800 border border-emerald-200/50 px-2 py-0.5 rounded-md"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse" />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
