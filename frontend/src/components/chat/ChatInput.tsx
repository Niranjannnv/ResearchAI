"use client";

import React, { useState, useRef, useEffect } from "react";
import { ArrowUp, Paperclip, Mic, MicOff, FileText, X, Loader2, Square } from "lucide-react";
import { api } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";

interface AttachedDoc {
  filename: string;
  size: number;
  word_count: number;
  page_count: number;
  text: string;
  preview: string;
}

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
}

export function ChatInput({ onSendMessage, disabled, isStreaming = false }: ChatInputProps) {
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

    let finalPrompt = content.trim();

    // If a document is attached, bind it into the research query
    if (attachedDoc) {
      const docHeader = `[Attached Reference Document: ${attachedDoc.filename} (${attachedDoc.word_count} words)]\n--- Document Text Excerpt ---\n${attachedDoc.text.slice(0, 15000)}\n--- End Document ---`;
      finalPrompt = finalPrompt
        ? `${finalPrompt}\n\n${docHeader}`
        : `Please analyze, verify, and cross-reference the following attached research document with scholarly literature:\n\n${docHeader}`;
    }

    onSendMessage(finalPrompt);
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
    <div className="mx-auto w-full max-w-3xl px-4 pb-4">
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
        className={`relative rounded-2xl border bg-white px-4 py-2.5 shadow-sm transition-all focus-within:shadow-md ${
          isListening
            ? "border-emerald-500 ring-2 ring-emerald-500/20"
            : "border-slate-300 focus-within:border-emerald-600 focus-within:ring-2 focus-within:ring-emerald-500/15"
        }`}
      >
        {/* Attached Document Pill Card */}
        {attachedDoc && (
          <div className="mb-2.5 flex items-center justify-between rounded-xl bg-emerald-50 border border-emerald-300/80 px-3 py-2 text-xs text-emerald-950 font-medium">
            <div className="flex items-center gap-2 overflow-hidden">
              <FileText className="h-4 w-4 shrink-0 text-emerald-700" />
              <div className="truncate">
                <span className="font-semibold">{attachedDoc.filename}</span>
                <span className="ml-2 text-[11px] text-emerald-700 font-normal">
                  ({attachedDoc.page_count > 1 ? `${attachedDoc.page_count} pages, ` : ""}
                  {attachedDoc.word_count.toLocaleString()} words)
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={removeAttachedDoc}
              className="ml-2 rounded-md p-1 text-emerald-700 hover:bg-emerald-200/60 transition-colors"
              title="Remove attached document"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Uploading indicator */}
        {isUploading && (
          <div className="mb-2.5 flex items-center gap-2 rounded-xl bg-slate-50 border border-slate-300 px-3 py-2 text-xs text-slate-800 font-medium">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-600" />
            <span>Parsing document text and extracting structure...</span>
          </div>
        )}

        {/* Upload Error Banner */}
        {uploadError && (
          <div className="mb-2.5 flex items-center justify-between rounded-xl bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
            <span>{uploadError}</span>
            <button type="button" onClick={() => setUploadError(null)}>
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Voice Listening Active Banner */}
        {isListening && (
          <div className="mb-2 flex items-center gap-2 text-xs text-emerald-800 font-semibold animate-pulse">
            <span className="h-2 w-2 rounded-full bg-emerald-600 animate-ping" />
            <span>Listening... Speak your research inquiry clearly</span>
          </div>
        )}

        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            attachedDoc
              ? `Ask a question about ${attachedDoc.filename} or press Enter to synthesize...`
              : isListening
              ? "Listening to voice input..."
              : "Ask any research question or topic..."
          }
          disabled={disabled}
          rows={1}
          className="w-full resize-none bg-transparent px-1 py-0.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 min-h-[26px] leading-relaxed font-normal"
        />

        <div className="flex items-center justify-between pt-1.5 mt-1 border-t border-slate-100">
          <div className="flex items-center gap-1 text-slate-500">
            {/* Attachment Button */}
            <button
              type="button"
              onClick={handleFileClick}
              disabled={isUploading || disabled}
              className={`p-1.5 rounded-lg transition-colors ${
                attachedDoc
                  ? "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                  : "hover:bg-slate-100 hover:text-slate-800"
              }`}
              title="Upload reference files (.pdf, .docx, .txt, .md, .csv)"
            >
              <Paperclip className="h-4 w-4" />
            </button>

            {/* Voice Input Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={disabled}
              className={`p-1.5 rounded-lg transition-all ${
                isListening
                  ? "bg-red-50 text-red-600 ring-2 ring-red-400/50 scale-105"
                  : "hover:bg-slate-100 hover:text-slate-800"
              }`}
              title={isListening ? "Stop listening" : "Voice input (recognizes names & places)"}
            >
              {isListening ? (
                <MicOff className="h-4 w-4 animate-pulse" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </button>
          </div>

          {isStreaming ? (
            <button
              type="button"
              onClick={stopStreaming}
              className="h-7 w-7 rounded-full bg-slate-900 flex items-center justify-center text-white shadow-xs transition-all hover:bg-black hover:scale-105 active:scale-95"
              title="Stop / Pause research"
            >
              <Square className="h-2.5 w-2.5 fill-current" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={(!content.trim() && !attachedDoc) || disabled}
              className="h-7 w-7 rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-xs transition-all hover:bg-emerald-700 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ArrowUp className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </form>

      <div className="text-center pt-2 text-[11px] text-slate-500 font-medium">
        ResearchAI searches OpenAlex, PubMed, arXiv, Semantic Scholar, CORE, Europe PMC, and Books.
      </div>
    </div>
  );
}
