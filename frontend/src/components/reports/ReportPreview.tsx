"use client";

import React, { useState } from "react";
import { ReportContent } from "@/types";
import { DownloadButton } from "./DownloadButton";
import { CitationCard } from "../chat/CitationCard";
import { FileText, CheckCircle2, Layers, Compass, Lightbulb, ShieldAlert, BookOpen, Sparkles } from "lucide-react";

interface ReportPreviewProps {
  content: ReportContent;
  reportId?: string;
}

export function ReportPreview({ content, reportId }: ReportPreviewProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "findings" | "analysis" | "comparisons" | "roadmap" | "references">("summary");

  const references = content.references || [];
  const comparisons = content.comparisons || [];
  const findings = content.findings || [];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6 text-slate-900">
      {/* Header & Export Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 text-xs text-emerald-800 font-bold uppercase tracking-wider">
            <FileText className="h-4 w-4 text-emerald-600" />
            <span>Comprehensive Scientific Intelligence Report</span>
          </div>
          <h2 className="mt-1 text-lg font-bold text-slate-900">
            {content.research_question || "Research Investigation"}
          </h2>
          <p className="text-xs text-slate-600 mt-0.5 font-medium">
            Cross-synthesized and validated from {content.source_count || references.length} primary scholarly repositories
          </p>
        </div>

        {reportId && <DownloadButton reportId={reportId} />}
      </div>

      {/* Navigation Tabs — hide tabs whose data is empty */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-slate-200 pb-2.5 text-xs font-medium">
        {[
          { id: "summary",      label: "Executive Summary & Context",         show: true },
          { id: "findings",     label: `Empirical Findings (${findings.length})`,    show: findings.length > 0 },
          { id: "analysis",     label: "In-Depth Analysis & Implications",     show: !!(content.analysis || content.practical_implications) },
          { id: "comparisons",  label: `Evidence Matrix (${comparisons.length})`,    show: comparisons.length > 0 },
          { id: "roadmap",      label: "Conclusions & Future Directions",       show: !!(content.conclusions || content.future_directions) },
          { id: "references",   label: `Citations & Sources (${references.length})`, show: references.length > 0 },
        ]
          .filter((tab) => tab.show)
          .map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-1.5 rounded-lg transition-all ${
                activeTab === tab.id
                  ? "bg-emerald-50 text-emerald-950 font-bold border border-emerald-300 shadow-2xs"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-medium border border-transparent"
              }`}
            >
              {tab.label}
            </button>
          ))}
      </div>

      {/* Tab Content Panels */}
      <div className="min-h-[280px]">
        {/* TAB 1: SUMMARY & BACKGROUND */}
        {activeTab === "summary" && (
          <div className="space-y-5 text-sm leading-relaxed text-slate-800">
            <div className="bg-emerald-50/50 p-5 rounded-xl border border-emerald-200 shadow-2xs">
              <h3 className="font-bold text-emerald-950 mb-2.5 flex items-center gap-2 text-xs uppercase tracking-wider">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                Executive Summary
              </h3>
              <p className="text-slate-800 whitespace-pre-line leading-relaxed text-xs sm:text-sm font-normal">
                {content.executive_summary}
              </p>
            </div>

            {content.background_and_context && (
              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200 shadow-2xs">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <BookOpen className="h-3.5 w-3.5 text-slate-700" />
                  Background & Foundational Context
                </h4>
                <p className="text-xs sm:text-sm text-slate-800 whitespace-pre-line leading-relaxed">
                  {content.background_and_context}
                </p>
              </div>
            )}

            {content.methodology && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
                <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-1">
                  Multi-Agent Discovery & Verification Protocol
                </h4>
                <p className="leading-relaxed">{content.methodology}</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: EMPIRICAL FINDINGS */}
        {activeTab === "findings" && (
          <div className="space-y-4">
            {findings.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No individual findings extracted.</p>
            ) : (
              findings.map((f, i) => (
                <div key={i} className="p-5 rounded-xl border border-slate-200 bg-white shadow-xs space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="h-6 w-6 rounded-lg bg-emerald-100 text-xs font-bold text-emerald-800 flex items-center justify-center">
                      {i + 1}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900">{f.section}</h4>
                  </div>

                  <p className="text-xs sm:text-sm leading-relaxed text-slate-800 whitespace-pre-line font-normal">
                    {f.content}
                  </p>

                  {f.key_takeaways && f.key_takeaways.length > 0 && (
                    <div className="rounded-lg bg-emerald-50/70 p-3.5 border border-emerald-200">
                      <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-950 mb-1.5 flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-emerald-700" /> Key Empirical Takeaways:
                      </p>
                      <ul className="list-disc list-inside space-y-1 text-xs text-emerald-950 font-medium">
                        {f.key_takeaways.map((t, tIdx) => (
                          <li key={tIdx}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {f.evidence && f.evidence.length > 0 && (
                    <div className="text-[11px] text-slate-600 pt-1.5 border-t border-slate-200">
                      <span className="font-semibold text-slate-900">Supported by: </span>
                      {f.evidence.join(" • ")}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB 3: IN-DEPTH ANALYSIS & IMPLICATIONS */}
        {activeTab === "analysis" && (
          <div className="space-y-5 text-sm leading-relaxed text-slate-800">
            <div className="p-5 rounded-xl border border-slate-200 bg-white shadow-xs space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center gap-1.5">
                <Lightbulb className="h-4 w-4 text-amber-600" />
                In-Depth Technical Analysis & Synthesis
              </h3>
              <p className="whitespace-pre-line text-slate-800 leading-relaxed text-xs sm:text-sm">
                {content.analysis}
              </p>
            </div>

            {content.practical_implications && (
              <div className="p-5 rounded-xl bg-blue-50/60 border border-blue-200 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-blue-950 flex items-center gap-1.5">
                  <Compass className="h-3.5 w-3.5 text-blue-700" />
                  Practical, Clinical & Industrial Implications
                </h4>
                <p className="text-xs sm:text-sm text-blue-950 whitespace-pre-line leading-relaxed font-normal">
                  {content.practical_implications}
                </p>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: EVIDENCE MATRIX */}
        {activeTab === "comparisons" && (
          <div className="space-y-4">
            {comparisons.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No conflicting viewpoints detected across sources.</p>
            ) : (
              comparisons.map((c, idx) => (
                <div key={idx} className="p-5 rounded-xl border border-slate-200 bg-white space-y-3 shadow-xs">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center gap-1.5">
                    <Layers className="h-3.5 w-3.5 text-emerald-600" />
                    {c.aspect}
                  </h4>
                  {c.analysis && (
                    <p className="text-xs text-slate-700 leading-relaxed italic">{c.analysis}</p>
                  )}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    {c.positions.map((pos, pIdx) => (
                      <div key={pIdx} className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                        <p className="font-bold text-slate-900">{pos.stance}</p>
                        {pos.sources && (
                          <p className="text-[11px] text-slate-600">
                            <strong className="text-slate-800">Sources:</strong> {pos.sources.join(", ")}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB 5: ROADMAP & LIMITATIONS */}
        {activeTab === "roadmap" && (
          <div className="space-y-5 text-sm leading-relaxed text-slate-800">
            {content.conclusions && (
              <div className="p-5 rounded-xl bg-emerald-50/60 border border-emerald-200/90 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-950 flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  Conclusions & Consensus Verdict
                </h4>
                <p className="text-xs sm:text-sm text-emerald-950 whitespace-pre-line leading-relaxed">
                  {content.conclusions}
                </p>
              </div>
            )}

            {content.future_directions && (
              <div className="p-5 rounded-xl bg-purple-50/60 border border-purple-200 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-purple-950 flex items-center gap-1.5">
                  <Compass className="h-3.5 w-3.5 text-purple-700" />
                  Future Research Directions & Strategic Roadmap
                </h4>
                <p className="text-xs sm:text-sm text-purple-950 whitespace-pre-line leading-relaxed">
                  {content.future_directions}
                </p>
              </div>
            )}

            {content.limitations && (
              <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-xs text-amber-950 space-y-1">
                <h4 className="font-bold uppercase tracking-wider flex items-center gap-1.5 text-amber-950">
                  <ShieldAlert className="h-3.5 w-3.5 text-amber-700" />
                  Limitations & Methodological Constraints
                </h4>
                <p className="leading-relaxed">{content.limitations}</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: CITATIONS & SOURCES */}
        {activeTab === "references" && (
          <div className="grid grid-cols-1 gap-3">
            {references.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No citation references attached.</p>
            ) : (
              references.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} index={idx} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
