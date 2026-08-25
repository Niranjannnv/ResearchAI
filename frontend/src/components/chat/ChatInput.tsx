"use client";

import React, { useState, useRef, useEffect } from "react";
import { ArrowUp, Paperclip, Mic } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || disabled) return;
    onSendMessage(content.trim());
    setContent("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-6">
      <form
        onSubmit={handleSubmit}
        className="relative rounded-2xl border border-gray-200/90 bg-white p-3 shadow-subtle transition-all focus-within:border-gray-300 focus-within:shadow-float"
      >
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask any research question or topic..."
          disabled={disabled}
          rows={1}
          className="w-full resize-none bg-transparent px-2 py-1 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none disabled:opacity-50 min-h-[44px]"
        />

        <div className="flex items-center justify-between pt-2 border-t border-gray-100 mt-2">
          <div className="flex items-center gap-1 text-gray-400">
            <button
              type="button"
              onClick={() => alert("Document upload will parse and cross-reference with backend scholarly databases.")}
              className="p-2 hover:bg-gray-100 hover:text-gray-700 rounded-lg transition-colors"
              title="Upload reference files"
            >
              <Paperclip className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={() => alert("Voice input listening activated...")}
              className="p-2 hover:bg-gray-100 hover:text-gray-700 rounded-lg transition-colors"
              title="Voice input"
            >
              <Mic className="h-4 w-4" />
            </button>
          </div>

          <button
            type="submit"
            disabled={!content.trim() || disabled}
            className="h-8 w-8 rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-xs transition-all hover:bg-emerald-700 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </div>
      </form>
      <div className="text-center pt-2 text-[11px] text-gray-400">
        ResearchAI generates comprehensive, verified intelligence reports from scholarly databases.
      </div>
    </div>
  );
}
