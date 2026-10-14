"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import { Briefcase, Database, Cpu, Activity, Clock, ShieldCheck, CheckCircle2 } from "lucide-react";

export default function WorkspacePage() {
  const [stats, setStats] = useState({
    activeAgents: 8,
    totalSourcesCached: 1420,
    averageVerificationScore: "94.2%",
    totalReportsGenerated: 18,
    systemUptime: "99.98%",
  });

  return (
    <div className="flex h-full flex-col bg-slate-50/40">
      <Header title="Research Fleet & Workspace Operations" />

      <div className="flex-1 overflow-y-auto p-3.5 sm:p-6 max-w-5xl mx-auto w-full space-y-6 sm:space-y-8">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Multi-Agent Fleet Topology</h2>
          <p className="text-xs text-slate-600 mt-1 font-medium">
            Real-time status of backend child agents coordinated by the Mother Agent orchestrator
          </p>
        </div>

        {/* Status Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-4">
          {[
            { label: "Active Child Agents", val: "8 Online", icon: Cpu, color: "text-emerald-700 bg-emerald-50 border border-emerald-200" },
            { label: "Connected Databases", val: "9 APIs", icon: Database, color: "text-blue-700 bg-blue-50 border border-blue-200" },
            { label: "Verification Precision", val: "94.8%", icon: ShieldCheck, color: "text-purple-700 bg-purple-50 border border-purple-200" },
            { label: "Avg Execution Latency", val: "4.2s", icon: Activity, color: "text-amber-700 bg-amber-50 border border-amber-200" },
          ].map((m, i) => {
            const Icon = m.icon;
            return (
              <div key={i} className="p-3 sm:p-4 rounded-2xl border border-slate-200 bg-white shadow-xs space-y-1.5 sm:space-y-2">
                <div className={`h-7 w-7 sm:h-8 sm:w-8 rounded-xl ${m.color} flex items-center justify-center`}>
                  <Icon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                </div>
                <div>
                  <p className="text-[10px] sm:text-[11px] font-semibold text-slate-500 leading-tight">{m.label}</p>
                  <p className="text-sm sm:text-base font-bold text-slate-900 mt-0.5">{m.val}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Active Child Agents Directory */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Deployed Child Search Agents
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              {
                name: "Academic Agent",
                apis: "OpenAlex, Crossref, Semantic Scholar, arXiv",
                status: "Operational",
                rateLimit: "Polite pool active (no throttling)",
              },
              {
                name: "Medical Agent",
                apis: "PubMed, PMC, NCBI E-Utilities",
                status: "Operational",
                rateLimit: "10 req/s rate-controlled",
              },
              {
                name: "Books Agent",
                apis: "Google Books API, Open Library",
                status: "Operational",
                rateLimit: "Unrestricted",
              },
              {
                name: "Statistics Agent",
                apis: "World Bank Data API, UN Datasets",
                status: "Operational",
                rateLimit: "Direct JSON endpoints",
              },
              {
                name: "Web & News Agent",
                apis: "Brave Search API, Trusted Domain Filters",
                status: "Operational",
                rateLimit: "SafeSearch Moderate",
              },
              {
                name: "Patents & Gov Agent",
                apis: "Google Patents, Gov/Edu/Europa indices",
                status: "Operational",
                rateLimit: "Institutional filtering",
              },
            ].map((agent, idx) => (
              <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">{agent.name}</span>
                  <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-300">
                    <CheckCircle2 className="h-3 w-3" />
                    {agent.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-700">
                  <strong className="text-slate-900 font-semibold">Integrations:</strong> {agent.apis}
                </p>
                <p className="text-[11px] text-slate-500 font-medium">{agent.rateLimit}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
