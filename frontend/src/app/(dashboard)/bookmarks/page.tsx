"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Bookmark } from "@/types";
import { api } from "@/lib/api";
import { Bookmark as BookmarkIcon, ExternalLink, Trash2, Calendar, Tag } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  const fetchBookmarks = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/bookmarks");
      setBookmarks(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const handleDeleteClick = (id: string) => {
    setPendingDeleteId(id);
    setConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!pendingDeleteId) return;
    setConfirmOpen(false);
    await api.delete(`/bookmarks/${pendingDeleteId}`);
    setBookmarks(bookmarks.filter((b) => b.id !== pendingDeleteId));
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
        title="Remove Bookmark"
        message="This bookmark and any annotations will be permanently removed."
        confirmLabel="Remove"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
      <Header title="Saved Research Bookmarks & Annotations" />

      <div className="flex-1 overflow-y-auto p-3.5 sm:p-6 max-w-4xl mx-auto w-full space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Saved Citations & Excerpts ({bookmarks.length})
          </h3>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
          </div>
        ) : bookmarks.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500 space-y-2">
            <BookmarkIcon className="h-8 w-8 mx-auto text-slate-300" />
            <p className="font-semibold text-slate-700">No bookmarked evidence yet.</p>
            <p className="text-[11px] text-slate-500">
              Click the bookmark icon on any synthesis response or citation to save it here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {bookmarks.map((bm) => (
              <div
                key={bm.id}
                className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs hover:border-slate-300 transition-all space-y-2"
              >
                <div className="flex items-start justify-between gap-3">
                  <h4 className="text-xs font-bold text-slate-900 line-clamp-2">
                    {bm.title}
                  </h4>
                  <button
                    onClick={() => handleDeleteClick(bm.id)}
                    className="p-1 text-slate-400 hover:text-red-600 rounded"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                {bm.note && (
                  <p className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200 whitespace-pre-line leading-relaxed font-normal">
                    {bm.note}
                  </p>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(bm.created_at)}
                  </span>

                  {bm.url && (
                    <a
                      href={bm.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-emerald-700 hover:text-emerald-900 font-semibold"
                    >
                      <span>Open Link</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
