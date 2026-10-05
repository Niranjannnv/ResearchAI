"use client";

import React, { useEffect, useRef } from "react";
import { AlertTriangle, X } from "lucide-react";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "warning";
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  variant = "danger",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  // Focus cancel button on open & trap Escape key
  useEffect(() => {
    if (!open) return;
    cancelRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  if (!open) return null;

  const isDanger = variant === "danger";

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ animation: "fadeIn 0.15s ease" }}
      aria-modal="true"
      role="dialog"
      aria-labelledby="confirm-title"
    >
      {/* Blurred overlay */}
      <div
        className="absolute inset-0 bg-gray-950/40 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Panel */}
      <div
        className="relative w-full max-w-sm rounded-2xl bg-white shadow-2xl ring-1 ring-gray-200/80 overflow-hidden"
        style={{ animation: "scaleIn 0.18s cubic-bezier(.34,1.56,.64,1)" }}
      >
        {/* Top accent bar */}
        <div
          className={`h-1 w-full ${
            isDanger
              ? "bg-gradient-to-r from-red-500 via-rose-500 to-red-400"
              : "bg-gradient-to-r from-amber-400 via-orange-400 to-amber-300"
          }`}
        />

        {/* Content */}
        <div className="px-6 pt-5 pb-6">
          {/* Icon + Title row */}
          <div className="flex items-start gap-4">
            <div
              className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                isDanger
                  ? "bg-red-50 text-red-600"
                  : "bg-amber-50 text-amber-600"
              }`}
            >
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <h2
                id="confirm-title"
                className="text-base font-semibold text-gray-900 leading-tight"
              >
                {title}
              </h2>
              <p className="mt-1.5 text-sm text-gray-500 leading-relaxed">
                {message}
              </p>
            </div>
            {/* Close X */}
            <button
              onClick={onCancel}
              className="shrink-0 p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Divider */}
          <div className="my-5 border-t border-gray-100" />

          {/* Actions */}
          <div className="flex items-center justify-end gap-2.5">
            <button
              ref={cancelRef}
              onClick={onCancel}
              className="px-4 py-2 rounded-xl text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
            >
              {cancelLabel}
            </button>
            <button
              onClick={onConfirm}
              className={`px-4 py-2 rounded-xl text-sm font-semibold text-white shadow-sm transition-all focus:outline-none focus-visible:ring-2 active:scale-[0.97] ${
                isDanger
                  ? "bg-red-600 hover:bg-red-700 focus-visible:ring-red-500 shadow-red-200"
                  : "bg-amber-500 hover:bg-amber-600 focus-visible:ring-amber-400 shadow-amber-200"
              }`}
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>

      {/* Keyframe animations injected once */}
      <style>{`
        @keyframes fadeIn  { from { opacity: 0 } to { opacity: 1 } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(.92) } to { opacity: 1; transform: scale(1) } }
      `}</style>
    </div>
  );
}
