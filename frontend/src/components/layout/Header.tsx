"use client";

import React from "react";
import { ShieldCheck, Menu } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";

interface HeaderProps {
  title?: string;
  domain?: string;
}

export function Header({ title = "ResearchAI Studio", domain }: HeaderProps) {
  const { toggleMobileSidebar } = useUIStore();

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white/95 backdrop-blur-md px-3 sm:px-6 z-10 select-none shadow-2xs shrink-0">
      <div className="flex items-center gap-2.5 min-w-0">
        {/* Mobile Hamburger Menu Toggle */}
        <button
          type="button"
          onClick={toggleMobileSidebar}
          className="md:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 active:bg-slate-200 transition-colors shrink-0"
          aria-label="Toggle navigation menu"
        >
          <Menu className="h-4 w-4" />
        </button>

        <h1 className="text-xs sm:text-sm font-bold text-slate-900 truncate max-w-[200px] sm:max-w-md">
          {title}
        </h1>
        {domain && (
          <span className="hidden xs:inline-flex text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2 py-0.5 rounded-full capitalize shrink-0">
            {domain}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <div className="flex items-center gap-1.5 text-xs text-slate-700 bg-slate-100 border border-slate-200/90 rounded-full px-2.5 sm:px-3 py-1 font-medium shadow-2xs">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
          <span className="hidden sm:inline">Multi-Agent Verification Active</span>
          <span className="sm:hidden text-[11px] font-semibold">Verified</span>
        </div>
      </div>
    </header>
  );
}
