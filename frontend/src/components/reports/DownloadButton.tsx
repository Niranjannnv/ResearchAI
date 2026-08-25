"use client";

import React, { useState } from "react";
import { Download, FileText, Code, Globe, ChevronDown, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DownloadButtonProps {
  reportId: string;
  className?: string;
}

export function DownloadButton({ reportId, className }: DownloadButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  const formats = [
    { key: "pdf", label: "PDF Document (.pdf)", icon: FileText, desc: "Executive styled print layout" },
    { key: "docx", label: "Word Document (.docx)", icon: FileText, desc: "Editable Microsoft Word report" },
    { key: "markdown", label: "Markdown (.md)", icon: Code, desc: "Clean markdown for notes & GitHub" },
    { key: "html", label: "Standalone HTML (.html)", icon: Globe, desc: "Self-contained interactive page" },
  ];

  const handleDownload = async (format: string) => {
    setDownloadingFormat(format);
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = typeof window !== "undefined" ? localStorage.getItem("researchai_access_token") : "";

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/download/${format}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Download failed");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ResearchReport-${reportId.slice(0, 8)}.${format === "markdown" ? "md" : format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      alert("Failed to download report. Please ensure the backend generated the file.");
    } finally {
      setDownloadingFormat(null);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative inline-block text-left">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="outline"
        size="sm"
        className="gap-2 bg-white text-gray-800 border-gray-200 shadow-xs hover:bg-gray-50"
      >
        <Download className="h-4 w-4 text-emerald-600" />
        <span>Export Report</span>
        <ChevronDown className="h-3 w-3 text-gray-400" />
      </Button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-20" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-72 rounded-xl border border-gray-200 bg-white p-1.5 shadow-float z-30 space-y-1">
            <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
              Select Export Format
            </div>
            {formats.map((fmt) => {
              const Icon = fmt.icon;
              return (
                <button
                  key={fmt.key}
                  onClick={() => handleDownload(fmt.key)}
                  disabled={downloadingFormat !== null}
                  className="w-full flex items-start gap-2.5 rounded-lg px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  <Icon className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{fmt.label}</p>
                    <p className="text-[11px] text-gray-400">{fmt.desc}</p>
                  </div>
                  {downloadingFormat === fmt.key && (
                    <span className="text-[10px] text-emerald-600 font-medium">Downloading...</span>
                  )}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
