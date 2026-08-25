"use client";

import React from "react";
import { Sparkles, ShieldCheck, Share2, HelpCircle } from "lucide-react";

interface HeaderProps {
  title?: string;
  domain?: string;
}

export function Header({ title = "ResearchAI Studio", domain }: HeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-gray-100 bg-white/80 backdrop-blur-md px-6 z-10 select-none">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold text-gray-900 truncate max-w-md">
          {title}
        </h1>
        {domain && (
          <span className="text-[11px] font-medium text-emerald-800 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full capitalize">
            {domain}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs text-gray-500 bg-gray-50 border border-gray-200/60 rounded-full px-3 py-1">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
          <span>Multi-Agent Verification Active</span>
        </div>
      </div>
    </header>
  );
}
