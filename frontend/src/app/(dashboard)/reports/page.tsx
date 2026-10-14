"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { DownloadButton } from "@/components/reports/DownloadButton";
import { ReportPreview } from "@/components/reports/ReportPreview";
import { Report } from "@/types";
import { api } from "@/lib/api";
import { FileText, Calendar, Database, Eye, Trash2, ArrowLeft } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { cn } from "@/lib/utils";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [mobileShowDetail, setMobileShowDetail] = useState(false);

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

  const handleSelectReport = (report: Report) => {
    setSelectedReport(report);
    setMobileShowDetail(true);
  };

  const handleDeleteClick = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setPendingDeleteId(id);
    setConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!pendingDeleteId) return;
    setConfirmOpen(false);
    await api.delete(`/reports/${pendingDeleteId}`);
    setReports(reports.filter((r) => r.id !== pendingDeleteId));
    if (selectedReport?.id === pendingDeleteId) {
      setSelectedReport(null);
      setMobileShowDetail(false);
    }
    setPendingDeleteId(null);
  };

  const handleCancelDelete = () => {
    setConfirmOpen(false);
    setPendingDeleteId(null);
  };

  return (
    <div className="flex h-full flex-col bg-slate-50/40">
      <ConfirmDialog
        open={confirmOpen}
        title="Delete Research Report"
        message="This report and all its exports will be permanently deleted. This action cannot be undone."
        confirmLabel="Delete Report"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
      <Header title="Research Reports Repository" />

      <div className="flex flex-1 overflow-hidden">
        {/* Reports List */}
        <div
          className={cn(
            "w-full sm:w-96 border-r border-slate-200 overflow-y-auto p-4 space-y-3 bg-white shrink-0",
            mobileShowDetail ? "hidden sm:block" : "block"
          )}
        >
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Generated Reports ({reports.length})
            </h3>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
            </div>
          ) : reports.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 space-y-2">
              <FileText className="h-8 w-8 mx-auto text-slate-300" />
              <p>No research reports generated yet.</p>
            </div>
          ) : (
            reports.map((report) => {
              const isSelected = selectedReport?.id === report.id;
              return (
                <div
                  key={report.id}
                  onClick={() => handleSelectReport(report)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                    isSelected
                      ? "bg-emerald-50/70 border-emerald-300 shadow-xs"
                      : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-subtle"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-xs font-bold text-slate-900 line-clamp-2">
                      {report.title}
                    </h4>
                    <button
                      onClick={(e) => handleDeleteClick(report.id, e)}
                      className="text-slate-400 hover:text-red-600 p-1 rounded"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <p className="text-[11px] text-slate-600 line-clamp-2 font-normal">
                    {report.summary || report.query}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(report.created_at)}
                    </span>
                    <span className="flex items-center gap-1 font-semibold text-emerald-800">
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
        <div
          className={cn(
            "flex-1 flex-col overflow-y-auto p-4 sm:p-6 bg-slate-50/50 min-w-0",
            mobileShowDetail ? "flex" : "hidden sm:flex"
          )}
        >
          {/* Mobile Back Button */}
          {mobileShowDetail && (
            <button
              type="button"
              onClick={() => setMobileShowDetail(false)}
              className="sm:hidden inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 px-3 py-2 rounded-lg shadow-2xs hover:bg-slate-50 w-fit mb-3"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Reports List</span>
            </button>
          )}

          {selectedReport ? (
            <div className="max-w-4xl mx-auto w-full space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider bg-emerald-50 px-3 py-1 rounded-full border border-emerald-300">
                  Report ID: {selectedReport.id.slice(0, 8)}
                </span>
                {!selectedReport.content && <DownloadButton reportId={selectedReport.id} />}
              </div>

              {selectedReport.content ? (
                <ReportPreview
                  content={selectedReport.content}
                  reportId={selectedReport.id}
                />
              ) : (
                <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-xs text-slate-600">
                  Detailed report structure not available.
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-xs text-slate-500">
              Select a report from the left panel to inspect findings & export.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
