"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Bookmark } from "@/types";
import { api } from "@/lib/api";
import { Bookmark as BookmarkIcon, ExternalLink, Trash2, Calendar, Tag } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);

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

  const handleDelete = async (id: string) => {
    if (confirm("Remove this bookmark?")) {
      await api.delete(`/bookmarks/${id}`);
      setBookmarks(bookmarks.filter((b) => b.id !== id));
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      <Header title="Saved Research Bookmarks & Annotations" />

      <div className="flex-1 overflow-y-auto p-6 max-w-4xl mx-auto w-full space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-gray-100">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
            Saved Citations & Excerpts ({bookmarks.length})
          </h3>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
          </div>
        ) : bookmarks.length === 0 ? (
          <div className="py-16 text-center text-xs text-gray-400 space-y-2">
            <BookmarkIcon className="h-8 w-8 mx-auto text-gray-300" />
            <p>No bookmarked evidence yet.</p>
            <p className="text-[11px] text-gray-400">
              Click the bookmark icon on any synthesis response or citation to save it here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {bookmarks.map((bm) => (
              <div
                key={bm.id}
                className="p-4 rounded-xl border border-gray-200/80 bg-white shadow-xs hover:border-gray-300 transition-all space-y-2"
              >
                <div className="flex items-start justify-between gap-3">
                  <h4 className="text-xs font-semibold text-gray-900 line-clamp-2">
                    {bm.title}
                  </h4>
                  <button
                    onClick={() => handleDelete(bm.id)}
                    className="p-1 text-gray-300 hover:text-red-500 rounded"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                {bm.note && (
                  <p className="text-xs text-gray-600 bg-gray-50/70 p-2.5 rounded-lg border border-gray-100 whitespace-pre-line leading-relaxed">
                    {bm.note}
                  </p>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-[11px] text-gray-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(bm.created_at)}
                  </span>

                  {bm.url && (
                    <a
                      href={bm.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-emerald-600 hover:underline font-medium"
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
