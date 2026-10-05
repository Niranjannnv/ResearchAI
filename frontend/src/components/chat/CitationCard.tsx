"use client";

import React, { useState } from "react";
import { ExternalLink, Copy, Check, BookMarked, Award } from "lucide-react";
import { SourceResult, CitationItem } from "@/types";

interface CitationCardProps {
  source?: SourceResult;
  citation?: CitationItem;
  index: number;
}

export function CitationCard({ source, citation, index }: CitationCardProps) {
  const [copiedFormat, setCopiedFormat] = useState<string | null>(null);

  const title = source?.title || citation?.title || "Scholarly Publication";
  const url = source?.url || citation?.url;
  const doi = source?.doi || citation?.doi;
  const authors = source?.authors || [];
  const publisher = source?.publisher;
  const year = source?.publication_date?.slice(0, 4);
  const confidence = source?.confidence_score ? Math.round(source.confidence_score * 100) : 85;

  const apa = source?.citation_apa || citation?.apa;
  const mla = source?.citation_mla || citation?.mla;
  const chicago = source?.citation_chicago || citation?.chicago;

  const handleCopy = (format: string, text?: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedFormat(format);
    setTimeout(() => setCopiedFormat(null), 2000);
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-xs transition-all hover:border-slate-300 hover:shadow-subtle">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-[10px] font-bold text-emerald-800">
            {index + 1}
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-700 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded">
            {source?.source_type || "Academic"}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-300">
            <Award className="h-3 w-3" />
            <span>{confidence}% Confidence</span>
          </div>
        </div>
      </div>

      <h4 className="mt-2.5 text-xs font-bold text-slate-900 line-clamp-2">
        {title}
      </h4>

      {authors.length > 0 && (
        <p className="mt-1 text-[11px] text-slate-600 font-medium line-clamp-1">
          {authors.slice(0, 3).join(", ")} {authors.length > 3 && `+${authors.length - 3} more`}
          {year && ` • ${year}`}
          {publisher && ` • ${publisher}`}
        </p>
      )}

      {source?.abstract && (
        <p className="mt-2 text-[11px] text-slate-700 line-clamp-2 italic bg-slate-50 p-2.5 rounded-lg border border-slate-200 leading-relaxed font-normal">
          "{source.abstract}"
        </p>
      )}

      {/* Citation format copy bar & direct link */}
      <div className="mt-3 flex items-center justify-between pt-2.5 border-t border-slate-200 text-[11px]">
        <div className="flex items-center gap-1">
          <span className="text-slate-500 mr-1 font-semibold">Cite:</span>
          {apa && (
            <button
              onClick={() => handleCopy("APA", apa)}
              className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-semibold border border-slate-200 flex items-center gap-1 shadow-2xs"
            >
              {copiedFormat === "APA" ? <Check className="h-2.5 w-2.5 text-emerald-600" /> : null}
              APA
            </button>
          )}
          {mla && (
            <button
              onClick={() => handleCopy("MLA", mla)}
              className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-semibold border border-slate-200 flex items-center gap-1 shadow-2xs"
            >
              {copiedFormat === "MLA" ? <Check className="h-2.5 w-2.5 text-emerald-600" /> : null}
              MLA
            </button>
          )}
          {chicago && (
            <button
              onClick={() => handleCopy("Chicago", chicago)}
              className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-semibold border border-slate-200 flex items-center gap-1 shadow-2xs"
            >
              {copiedFormat === "Chicago" ? <Check className="h-2.5 w-2.5 text-emerald-600" /> : null}
              Chicago
            </button>
          )}
        </div>

        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-emerald-700 hover:text-emerald-900 font-semibold"
          >
            <span>View Source</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </div>
  );
}
