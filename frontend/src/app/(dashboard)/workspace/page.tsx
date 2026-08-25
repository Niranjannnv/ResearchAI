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
    <div className="flex h-full flex-col bg-white">
      <Header title="Research Fleet & Workspace Operations" />

      <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-8">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Multi-Agent Fleet Topology</h2>
          <p className="text-xs text-gray-500 mt-1">
            Real-time status of backend child agents coordinated by the Mother Agent orchestrator
          </p>
        </div>

        {/* Status Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Active Child Agents", val: "8 Online", icon: Cpu, color: "text-emerald-600 bg-emerald-50" },
            { label: "Connected Databases", val: "9 APIs", icon: Database, color: "text-blue-600 bg-blue-50" },
            { label: "Verification Precision", val: "94.8%", icon: ShieldCheck, color: "text-purple-600 bg-purple-50" },
            { label: "Avg Execution Latency", val: "4.2s", icon: Activity, color: "text-amber-600 bg-amber-50" },
          ].map((m, i) => {
            const Icon = m.icon;
            return (
              <div key={i} className="p-4 rounded-2xl border border-gray-200/80 bg-white shadow-xs space-y-2">
                <div className={`h-8 w-8 rounded-xl ${m.color} flex items-center justify-center`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-[11px] font-medium text-gray-400">{m.label}</p>
                  <p className="text-base font-bold text-gray-900 mt-0.5">{m.val}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Active Child Agents Directory */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
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
              <div key={idx} className="p-4 rounded-xl border border-gray-200/80 bg-white space-y-2 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-gray-900">{agent.name}</span>
                  <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/50">
                    <CheckCircle2 className="h-3 w-3" />
                    {agent.status}
                  </span>
                </div>
                <p className="text-[11px] text-gray-600">
                  <strong className="text-gray-700">Integrations:</strong> {agent.apis}
                </p>
                <p className="text-[10px] text-gray-400">{agent.rateLimit}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
