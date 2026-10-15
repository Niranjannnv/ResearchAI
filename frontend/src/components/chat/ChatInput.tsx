"use client";

import React, { useState, useRef, useEffect } from "react";
import { ArrowUp, Paperclip, Mic, MicOff, FileText, X, Loader2, Square } from "lucide-react";
import { api } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import { cn } from "@/lib/utils";

interface AttachedDoc {
  filename: string;
  size: number;
  word_count: number;
  page_count: number;
  text: string;
  preview: string;
}

interface ChatInputProps {
  onSendMessage: (displayText: string, apiText: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
  centered?: boolean;
}

export function ChatInput({
  onSendMessage,
  disabled,
  isStreaming = false,
  centered = false,
}: ChatInputProps) {
  const { stopStreaming } = useChatStore();
  const [content, setContent] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [attachedDoc, setAttachedDoc] = useState<AttachedDoc | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  // Clean up speech recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const baseTextRef = useRef<string>("");

  // en-IN = English (India): understands Indian names, places & accents in English

  // Voice speech-to-text handler
  const toggleVoiceInput = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        "Voice input is not supported in this browser. Please use Google Chrome, Edge, or Safari."
      );
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-IN";    // English (India) — understands Indian names & places
      recognition.maxAlternatives = 3;

      recognition.onstart = () => {
        baseTextRef.current = content.trim();
        setIsListening(true);
        textareaRef.current?.focus();
      };

      recognition.onresult = (event: any) => {
        let final = "";
        let interim = "";

        for (let i = 0; i < event.results.length; i++) {
          const item = event.results[i];
          const transcript = item[0].transcript;
          if (item.isFinal) {
            final += transcript + " ";
          } else {
            interim += transcript;
          }
        }

        const base = baseTextRef.current;
        const prefix = base ? `${base} ` : "";
        const fullText = (prefix + final + interim).trimStart();
        setContent(fullText);
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
        textareaRef.current?.focus();
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      setIsListening(false);
    }
  };

  // File upload handler
  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError(null);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await api.post("/chats/upload-document", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setAttachedDoc(data);
    } catch (err: any) {
      setUploadError(
        err.response?.data?.detail || "Failed to upload or parse document."
      );
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const removeAttachedDoc = () => {
    setAttachedDoc(null);
    setUploadError(null);
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if ((!content.trim() && !attachedDoc) || disabled) return;

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    const userQuestion = content.trim();

    // displayText: what appears in the chat bubble (clean, no document dump)
    const displayText = attachedDoc
      ? userQuestion
        ? userQuestion
        : `📄 Analyzing: ${attachedDoc.filename}`
      : userQuestion;

    // apiText: what is sent to the backend (includes full document context)
    let apiText = userQuestion;
    if (attachedDoc) {
      const docHeader = `[Attached Reference Document: ${attachedDoc.filename} (${attachedDoc.word_count} words)]\n--- Document Text ---\n${attachedDoc.text.slice(0, 15000)}\n--- End Document ---`;
      apiText = userQuestion
        ? `${userQuestion}\n\n${docHeader}`
        : `Please analyze, verify, and cross-reference the following attached research document with scholarly literature:\n\n${docHeader}`;
    }

    onSendMessage(displayText, apiText);
    setContent("");
    setAttachedDoc(null);
    setUploadError(null);

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className={cn(
        "mx-auto w-full transition-all",
        centered
          ? "max-w-2xl px-2 sm:px-0"
          : "max-w-3xl px-2.5 sm:px-4 pb-[env(safe-area-inset-bottom,0.5rem)] pt-1"
      )}
    >
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.docx,.txt,.md,.csv,.json"
        className="hidden"
      />

      <form
        onSubmit={handleSubmit}
        className={cn(
          "relative rounded-2xl border bg-white transition-all",
          centered
            ? "px-3.5 sm:px-5 py-3 sm:py-3.5 shadow-md sm:shadow-lg hover:shadow-xl focus-within:shadow-xl focus-within:border-emerald-600 focus-within:ring-4 focus-within:ring-emerald-500/10 border-slate-300/90"
            : "px-3 sm:px-4 py-2 sm:py-2.5 shadow-2xs focus-within:shadow-md focus-within:border-emerald-600 focus-within:ring-2 focus-within:ring-emerald-500/15 border-slate-300",
          isListening && "border-emerald-500 ring-2 ring-emerald-500/20"
        )}
      >
        {/* Attached Document Pill Card */}
        {attachedDoc && (
          <div className="mb-2 flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-300/80 px-2.5 py-2">
            <FileText className="h-4 w-4 shrink-0 text-emerald-700" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-emerald-950 truncate">{attachedDoc.filename}</p>
              <p className="text-[10px] text-emerald-700 font-medium mt-0.5">
                {attachedDoc.page_count > 1 ? `${attachedDoc.page_count} pages · ` : ""}
                {attachedDoc.word_count.toLocaleString()} words · Ready to analyze
              </p>
            </div>
            <button
              type="button"
              onClick={removeAttachedDoc}
              className="ml-1 rounded-md p-1 text-emerald-700 hover:bg-emerald-200/60 transition-colors shrink-0"
              title="Remove attached document"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Uploading indicator */}
        {isUploading && (
          <div className="mb-2 flex items-center gap-2.5 rounded-xl bg-slate-50 border border-slate-200 px-3 py-2.5">
            <Loader2 className="h-4 w-4 animate-spin text-emerald-600 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-800">Parsing document...</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Extracting text and structure</p>
            </div>
          </div>
        )}

        {/* Upload Error Banner */}
        {uploadError && (
          <div className="mb-2 flex items-start justify-between gap-2 rounded-xl bg-red-50 border border-red-200 px-3 py-2">
            <p className="text-xs text-red-700 flex-1">{uploadError}</p>
            <button type="button" onClick={() => setUploadError(null)} className="shrink-0 mt-0.5">
              <X className="h-3.5 w-3.5 text-red-500" />
            </button>
          </div>
        )}

        {/* Voice Listening Active Banner */}
        {isListening && (
          <div className="mb-2 flex items-center gap-2 text-xs text-emerald-800 font-semibold animate-pulse">
            <span className="h-2 w-2 rounded-full bg-emerald-600 animate-ping" />
            <span>Listening... Speak your research inquiry</span>
          </div>
        )}

        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            attachedDoc
              ? `Ask a question about ${attachedDoc.filename}...`
              : isListening
              ? "Listening to voice input..."
              : centered
              ? "Ask any research question, clinical hypothesis, or topic..."
              : "Ask any research question..."
          }
          disabled={disabled}
          rows={1}
          className={cn(
            "w-full resize-none bg-transparent px-1 py-0.5 text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 leading-relaxed font-normal",
            centered ? "text-sm sm:text-base min-h-[36px] sm:min-h-[44px]" : "text-sm min-h-[26px]"
          )}
        />

        <div className="flex items-center justify-between pt-1.5 mt-1 border-t border-slate-100">
          <div className="flex items-center gap-1 text-slate-500">
            {/* Attachment Button */}
            <button
              type="button"
              onClick={handleFileClick}
              disabled={isUploading || disabled}
              className={cn(
                "rounded-lg transition-colors",
                centered ? "p-2" : "p-1.5 sm:p-2",
                attachedDoc
                  ? "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                  : "hover:bg-slate-100 hover:text-slate-800"
              )}
              title="Upload reference files (.pdf, .docx, .txt, .md, .csv)"
            >
              <Paperclip className={centered ? "h-4 w-4 sm:h-5 sm:w-5" : "h-4 w-4"} />
            </button>

            {/* Voice Input Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={disabled}
              className={cn(
                "rounded-lg transition-all",
                centered ? "p-2" : "p-1.5 sm:p-2",
                isListening
                  ? "bg-red-50 text-red-600 ring-2 ring-red-400/50 scale-105"
                  : "hover:bg-slate-100 hover:text-slate-800"
              )}
              title={isListening ? "Stop listening" : "Voice input"}
            >
              {isListening ? (
                <MicOff className={cn("animate-pulse", centered ? "h-4 w-4 sm:h-5 sm:w-5" : "h-4 w-4")} />
              ) : (
                <Mic className={centered ? "h-4 w-4 sm:h-5 sm:w-5" : "h-4 w-4"} />
              )}
            </button>
          </div>

          {isStreaming ? (
            <button
              type="button"
              onClick={stopStreaming}
              className={cn(
                "rounded-full bg-slate-900 flex items-center justify-center text-white shadow-xs transition-all hover:bg-black hover:scale-105 active:scale-95",
                centered ? "h-8 w-8 sm:h-9 sm:w-9" : "h-7 w-7"
              )}
              title="Stop / Pause research"
            >
              <Square className={centered ? "h-3 w-3 fill-current" : "h-2.5 w-2.5 fill-current"} />
            </button>
          ) : (
            <button
              type="submit"
              disabled={(!content.trim() && !attachedDoc) || disabled}
              className={cn(
                "rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-xs transition-all hover:bg-emerald-700 disabled:opacity-30 disabled:cursor-not-allowed",
                centered ? "h-8 w-8 sm:h-9 sm:w-9" : "h-7 w-7"
              )}
            >
              <ArrowUp className={centered ? "h-4 w-4" : "h-3.5 w-3.5"} />
            </button>
          )}
        </div>
      </form>

      <div className="text-center pt-1.5 text-[10px] sm:text-[11px] text-slate-400 font-medium px-2 leading-tight">
        Searches OpenAlex · PubMed · arXiv · Semantic Scholar · CORE · Europe PMC
      </div>
    </div>
  );
}
