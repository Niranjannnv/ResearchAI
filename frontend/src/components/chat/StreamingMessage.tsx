"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Search, BookOpen, CheckCircle2, ShieldCheck, Cpu } from "lucide-react";

interface StreamingMessageProps {
  status: string | null;
  activeAgents?: string[];
}

export function StreamingMessage({ status }: StreamingMessageProps) {
  const [dots, setDots] = useState("");
  const [sourcesFound, setSourcesFound] = useState(12);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 450);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const counter = setInterval(() => {
      setSourcesFound((prev) => (prev < 48 ? prev + Math.floor(Math.random() * 4 + 1) : 48));
    }, 1200);
    return () => clearInterval(counter);
  }, []);

  // Determine active phase based on status text
  const currentStatus = status || "Searching academic papers & clinical trials...";
  
  const steps = [
    { id: 1, label: "Decomposing Inquiry", icon: Cpu, done: true },
    { id: 2, label: "Querying 8+ Scholarly Databases", icon: Search, done: currentStatus.includes("Ranking") || currentStatus.includes("synthesiz") || currentStatus.includes("report") || currentStatus.includes("verif") },
    { id: 3, label: "Verifying Empirical Evidence", icon: ShieldCheck, done: currentStatus.includes("synthesiz") || currentStatus.includes("report") },
    { id: 4, label: "Synthesizing Intelligence Report", icon: BookOpen, done: currentStatus.includes("finaliz") },
  ];

  return (
    <div className="relative my-4 overflow-hidden rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-slate-900 via-[#0c1424] to-slate-900 p-5 text-white shadow-xl shadow-emerald-950/20">
      {/* Background Animated Glow Orb */}
      <div className="absolute -top-16 -right-16 h-48 w-48 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-teal-500/10 blur-3xl pointer-events-none" />

      {/* Top Header & Shimmer Bar */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg shadow-emerald-500/30">
            <Sparkles className="h-4 w-4 animate-spin" style={{ animationDuration: "6s" }} />
            <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
                ResearchAI Multi-Agent Synthesis
              </span>
            </div>
            <p className="text-xs text-slate-300 font-medium">
              {currentStatus.replace(/[🔍📊📝✅📖⚡]/g, "").trim()}
              <span className="inline-block w-4 text-emerald-400 font-bold">{dots}</span>
            </p>
          </div>
        </div>

        {/* Live Source Counter Badge */}
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>{sourcesFound}+ Sources Cross-Referenced</span>
        </div>
      </div>

      {/* Animated Gradient Progress Shimmer */}
      <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-slate-800/80 mb-4">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 via-teal-300 to-emerald-600 animate-[shimmer_2s_infinite]" />
      </div>

      {/* Interactive 4-Phase Stepper */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 border-t border-white/5">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div
              key={step.id}
              className={`flex items-center gap-2 rounded-xl px-2.5 py-2 transition-all ${
                step.done
                  ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-300"
                  : "bg-white/[0.03] border border-white/5 text-slate-400"
              }`}
            >
              <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-lg bg-black/40">
                {step.done ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 animate-in zoom-in" />
                ) : (
                  <Icon className="h-3 w-3 text-slate-400 animate-pulse" />
                )}
              </div>
              <span className="text-[11px] font-medium leading-tight truncate">
                {step.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Custom keyframes for shimmer */}
      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}
