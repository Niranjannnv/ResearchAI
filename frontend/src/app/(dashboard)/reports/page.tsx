"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { DownloadButton } from "@/components/reports/DownloadButton";
import { ReportPreview } from "@/components/reports/ReportPreview";
import { Report } from "@/types";
import { api } from "@/lib/api";
import { FileText, Calendar, Database, Eye, Trash2, ArrowRight } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/reports");
      setReports(data.reports || []);
      if (data.reports?.length > 0 && !selectedReport) {
        setSelectedReport(data.reports[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Delete this research report?")) {
      await api.delete(`/reports/${id}`);
      setReports(reports.filter((r) => r.id !== id));
      if (selectedReport?.id === id) {
        setSelectedReport(null);
      }
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      <Header title="Research Reports Repository" />

      <div className="flex flex-1 overflow-hidden">
        {/* Reports List */}
        <div className="w-full sm:w-96 border-r border-gray-100 overflow-y-auto p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-gray-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
              Generated Reports ({reports.length})
            </h3>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
            </div>
          ) : reports.length === 0 ? (
            <div className="py-12 text-center text-xs text-gray-400 space-y-2">
              <FileText className="h-8 w-8 mx-auto text-gray-300" />
              <p>No research reports generated yet.</p>
            </div>
          ) : (
            reports.map((report) => {
              const isSelected = selectedReport?.id === report.id;
              return (
                <div
                  key={report.id}
                  onClick={() => setSelectedReport(report)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                    isSelected
                      ? "bg-emerald-50/50 border-emerald-300 shadow-xs"
                      : "bg-white border-gray-200/80 hover:border-gray-300 hover:shadow-subtle"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-xs font-semibold text-gray-900 line-clamp-2">
                      {report.title}
                    </h4>
                    <button
                      onClick={(e) => handleDelete(report.id, e)}
                      className="text-gray-300 hover:text-red-500 p-1 rounded"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <p className="text-[11px] text-gray-500 line-clamp-2">
                    {report.summary || report.query}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-[11px] text-gray-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(report.created_at)}
                    </span>
                    <span className="flex items-center gap-1 font-medium text-emerald-700">
                      <Database className="h-3 w-3" />
                      {report.source_count || 0} Sources
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Report Preview Panel */}
        <div className="hidden sm:flex flex-1 flex-col overflow-y-auto p-6">
          {selectedReport ? (
            <div className="max-w-4xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200/50">
                  Report ID: {selectedReport.id.slice(0, 8)}
                </span>
                <DownloadButton reportId={selectedReport.id} />
              </div>

              {selectedReport.content ? (
                <ReportPreview
                  content={selectedReport.content}
                  reportId={selectedReport.id}
                />
              ) : (
                <div className="rounded-2xl border border-gray-200 p-8 text-center text-xs text-gray-500">
                  Detailed report structure not available.
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-xs text-gray-400">
              Select a report from the left panel to inspect findings & export.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
