"use client";

import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Message, SourceResult, CitationItem, ReportContent } from "@/types";
import {
  Sparkles,
  User,
  FileText,
  ChevronDown,
  ChevronUp,
  Bookmark as BookmarkIcon,
  Loader2,
  Copy,
  Check,
  Pencil,
  RotateCcw,
  ArrowUpRight,
} from "lucide-react";
import { CitationCard } from "./CitationCard";
import { ReportPreview } from "../reports/ReportPreview";
import { DownloadButton } from "../reports/DownloadButton";
import { api } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const { sendMessage } = useChatStore();

  const [showCitations, setShowCitations] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);

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

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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

  const handleSaveEdit = () => {
    if (!editContent.trim()) return;
    setIsEditing(false);
    sendMessage(message.chat_id, editContent.trim());
  };

  if (isUser) {
    return (
      <div className="group flex gap-3 py-4 border-b border-gray-100/70 px-4 sm:px-6 justify-end">
        <div className="flex flex-col items-end space-y-1.5 max-w-2xl w-full sm:w-auto">
          {isEditing ? (
            /* Inline Edit Box */
            <div className="w-full sm:w-[480px] rounded-2xl border border-emerald-500 bg-white p-3 shadow-md">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={3}
                className="w-full resize-none bg-transparent text-sm text-gray-900 focus:outline-none"
                autoFocus
              />
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100 mt-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setEditContent(message.content);
                  }}
                  className="rounded-lg px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveEdit}
                  disabled={!editContent.trim()}
                  className="rounded-lg bg-emerald-600 px-3.5 py-1 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-40 transition-colors"
                >
                  Save & Submit
                </button>
              </div>
            </div>
          ) : (
            /* Standard User Message Bubble */
            <div className="rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-gray-900 leading-relaxed font-medium">
              {message.content}
            </div>
          )}

          {/* Action Bar (Copy & Edit) */}
          {!isEditing && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                type="button"
                onClick={handleCopy}
                className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                title="Copy message"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
              </button>

              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                title="Edit message"
              >
                <Pencil className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>

        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-slate-200 text-slate-700 text-xs font-semibold">
          <User className="h-4 w-4" />
        </div>
      </div>
    );
  }

  return (
    <div className="group flex gap-4 py-6 border-b border-gray-100 bg-white px-4 sm:px-6">
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-emerald-600 text-white shadow-xs">
        <Sparkles className="h-4 w-4" />
      </div>

      <div className="flex-1 space-y-3.5 max-w-4xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-900">
              ResearchAI
            </span>
            <span className="text-[11px] text-gray-400 font-medium">
              Verified Scientific Intelligence Report
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Copy button */}
            <button
              type="button"
              onClick={handleCopy}
              className="p-1.5 rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-gray-700 hover:bg-gray-50 transition-colors"
              title="Copy response"
            >
              {copied ? (
                <Check className="h-3.5 w-3.5 text-emerald-600" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </button>

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

        {/* Render ChatGPT-Style Stopped State if Research was Paused */}
        {message.metadata_?.stopped || message.content === "_Research paused by user._" ? (
          <div className="space-y-3 pt-1">
            <div className="inline-flex items-center gap-2 rounded-lg bg-gray-100/90 px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-200/60">
              <span className="h-2 w-2 rounded-xs bg-gray-500" />
              <span>Research paused (generation stopped by user)</span>
            </div>
          </div>
        ) : fetchedReport ? (
          <div className="pt-1">
            <ReportPreview content={fetchedReport} reportId={reportId} />
          </div>
        ) : loadingReport ? (
          <div className="flex items-center gap-2 py-4 text-xs text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin text-emerald-600" />
            <span>Loading full detailed enterprise report...</span>
          </div>
        ) : (
          /* Rich Markdown & Interactive Suggestion Cards */
          <div className="text-gray-800 leading-relaxed text-sm">
            <ReactMarkdown
              components={{
                strong: ({ node, ...props }) => (
                  <span className="font-semibold text-gray-900" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="mb-3 last:mb-0 text-sm leading-relaxed text-gray-700" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="space-y-2 my-3 list-none pl-0" {...props} />
                ),
                li: ({ node, children, ...props }) => {
                  // Extract raw string to pass to search
                  const rawString = React.Children.toArray(children)
                    .map((c) => (typeof c === "string" ? c : (c as any)?.props?.children || ""))
                    .join("")
                    .replace(/^[•*\-\s]+|[•*\-\s]+$/g, "")
                    .trim();

                  return (
                    <li
                      onClick={() => {
                        if (rawString.length > 5) {
                          sendMessage(message.chat_id, rawString);
                        }
                      }}
                      className="group/pill flex items-center justify-between gap-3 rounded-xl border border-emerald-200/70 bg-gradient-to-r from-emerald-50/80 to-teal-50/40 hover:from-emerald-100/90 hover:to-teal-100/70 hover:border-emerald-400/80 px-4 py-2.5 text-xs font-medium text-emerald-950 cursor-pointer shadow-xs transition-all active:scale-[0.99]"
                      title={`Click to research: "${rawString}"`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Sparkles className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                        <span className="font-medium text-emerald-900">{children}</span>
                      </div>
                      <ArrowUpRight className="h-4 w-4 text-emerald-600 opacity-60 group-hover/pill:opacity-100 group-hover/pill:translate-x-0.5 group-hover/pill:-translate-y-0.5 transition-all shrink-0" />
                    </li>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
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
