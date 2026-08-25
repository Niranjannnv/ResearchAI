"use client";

import React, { useState, useEffect } from "react";
import { Message, SourceResult, CitationItem, ReportContent } from "@/types";
import { Sparkles, User, FileText, ChevronDown, ChevronUp, Bookmark as BookmarkIcon, Loader2 } from "lucide-react";
import { CitationCard } from "./CitationCard";
import { ReportPreview } from "../reports/ReportPreview";
import { DownloadButton } from "../reports/DownloadButton";
import { api } from "@/lib/api";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [showCitations, setShowCitations] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [fetchedReport, setFetchedReport] = useState<ReportContent | null>(
    message.metadata_?.report || null
  );
  const [loadingReport, setLoadingReport] = useState(false);

  const sources = message.metadata_?.sources || [];
  const citations = message.metadata_?.citations || [];
  const reportId = message.report_id || message.metadata_?.report_id;

  // Auto-fetch full report data if we have a reportId but no inline report object
  useEffect(() => {
    if (reportId && !fetchedReport && !isUser) {
      let isMounted = true;
      setLoadingReport(true);
      api
        .get(`/reports/${reportId}`)
        .then((res) => {
          if (isMounted && res.data?.content) {
            setFetchedReport(res.data.content);
          }
        })
        .catch((err) => {
          console.warn("Could not fetch detailed report for message", err);
        })
        .finally(() => {
          if (isMounted) setLoadingReport(false);
        });
      return () => {
        isMounted = false;
      };
    }
  }, [reportId, fetchedReport, isUser]);

  const handleBookmark = async () => {
    try {
      await api.post("/bookmarks", {
        title: message.content.slice(0, 100),
        note: message.content,
        chat_id: message.chat_id,
        report_id: reportId,
      });
      setIsBookmarked(true);
    } catch (e) {
      alert("Failed to bookmark message");
    }
  };

  if (isUser) {
    return (
      <div className="flex gap-4 py-6 border-b border-gray-100 px-6 justify-end">
        <div className="max-w-2xl rounded-2xl bg-gray-100/90 px-4 py-3 text-sm text-gray-900 leading-relaxed font-medium">
          {message.content}
        </div>
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-gray-200 text-gray-700 text-xs font-semibold">
          <User className="h-4 w-4" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 py-6 border-b border-gray-100 bg-white px-4 sm:px-6">
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-emerald-600 text-white shadow-xs">
        <Sparkles className="h-4 w-4" />
      </div>

      <div className="flex-1 space-y-4 max-w-4xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-900">
              ResearchAI
            </span>
            <span className="text-[11px] text-gray-400 font-medium">
              Verified Scientific Intelligence Report
            </span>
          </div>

          <div className="flex items-center gap-2">
            {reportId && <DownloadButton reportId={reportId} />}
            <button
              onClick={handleBookmark}
              className={`p-1.5 rounded-lg border text-xs transition-colors ${
                isBookmarked
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-white text-gray-400 border-gray-200 hover:text-gray-700"
              }`}
              title="Bookmark synthesis"
            >
              <BookmarkIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Render the Full Detailed Multi-Section Report if Available */}
        {fetchedReport ? (
          <div className="pt-1">
            <ReportPreview content={fetchedReport} reportId={reportId} />
          </div>
        ) : loadingReport ? (
          <div className="flex items-center gap-2 py-4 text-xs text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin text-emerald-600" />
            <span>Loading full detailed enterprise report...</span>
          </div>
        ) : (
          /* Fallback Text Summary */
          <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed whitespace-pre-line text-sm">
            {message.content}
          </div>
        )}

        {/* Citations & Evidence Drawer (if not using ReportPreview or as backup) */}
        {!fetchedReport && (sources.length > 0 || citations.length > 0) && (
          <div className="pt-2 border-t border-gray-100">
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center gap-2 text-xs font-semibold text-emerald-700 hover:text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200/50 transition-colors"
            >
              <span>
                {showCitations
                  ? "Hide Citations & Evidence"
                  : `View ${sources.length || citations.length} Primary Sources & Citations`}
              </span>
              {showCitations ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </button>

            {showCitations && (
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                {sources.length > 0
                  ? sources.map((source, idx) => (
                      <CitationCard key={idx} source={source} index={idx} />
                    ))
                  : citations.map((citation, idx) => (
                      <CitationCard key={idx} citation={citation} index={idx} />
                    ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
