"use client";

import React, { useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { StreamingMessage } from "@/components/chat/StreamingMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { ReportPreview } from "@/components/reports/ReportPreview";
import { useChatStore } from "@/stores/chatStore";
import { Sparkles } from "lucide-react";

export default function ChatPage() {
  const params = useParams();
  const chatId = params?.id as string;

  const {
    currentChat,
    messages,
    isStreaming,
    streamStatus,
    activeAgents,
    liveReport,
    selectChat,
    sendMessage,
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatId && chatId !== "new") {
      selectChat(chatId);
    }
  }, [chatId, selectChat]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming, liveReport]);

  const handleSend = (text: string) => {
    if (chatId) {
      sendMessage(chatId, text);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-full flex-col bg-white">
      <Header title={currentChat?.title || "ResearchAI"} />

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto">
        {!hasMessages && !isStreaming ? (
          /* Clean & Minimal Empty State */
          <div className="mx-auto flex h-full max-w-lg flex-col items-center justify-center px-4 text-center space-y-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200/50 shadow-xs">
              <Sparkles className="h-6 w-6" />
            </div>

            <div className="space-y-1">
              <h2 className="text-lg font-bold tracking-tight text-gray-900">
                What would you like to research today?
              </h2>
              <p className="text-xs text-gray-400 max-w-sm">
                Ask any complex research question or topic to generate a comprehensive verified report.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-4xl pb-12">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {isStreaming && (
              <StreamingMessage
                status={streamStatus}
                activeAgents={activeAgents}
              />
            )}

            {/* Live Generated Report Preview */}
            {liveReport && (
              <div className="p-6">
                <ReportPreview content={liveReport} />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <ChatInput onSendMessage={handleSend} disabled={isStreaming} />
    </div>
  );
}
