"use client";

import React from "react";
import { Sparkles, ShieldCheck, Share2, HelpCircle } from "lucide-react";

interface HeaderProps {
  title?: string;
  domain?: string;
}

export function Header({ title = "ResearchAI Studio", domain }: HeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white/95 backdrop-blur-md px-6 z-10 select-none shadow-2xs">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-bold text-slate-900 truncate max-w-md">
          {title}
        </h1>
        {domain && (
          <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2.5 py-0.5 rounded-full capitalize">
            {domain}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs text-slate-700 bg-slate-100 border border-slate-200/90 rounded-full px-3 py-1 font-medium shadow-2xs">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
          <span>Multi-Agent Verification Active</span>
        </div>
      </div>
    </header>
  );
}
