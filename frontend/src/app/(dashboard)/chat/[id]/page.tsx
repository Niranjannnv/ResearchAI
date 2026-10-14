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
    streamingChatId,
    streamStatus,
    activeAgents,
    liveReport,
    selectChat,
    sendMessage,
  } = useChatStore();

  const isCurrentChatStreaming = isStreaming && (streamingChatId === chatId || (chatId === "new" && streamingChatId === "new"));

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatId && chatId !== "new") {
      selectChat(chatId);
    }
  }, [chatId, selectChat]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isCurrentChatStreaming, liveReport]);

  const handleSend = (displayText: string, apiText: string) => {
    if (chatId) {
      sendMessage(chatId, apiText, displayText);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-full flex-col bg-slate-50/40 min-w-0 max-w-full overflow-hidden">
      <Header title={currentChat?.title || "ResearchAI"} />

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden min-w-0 max-w-full">
        {!hasMessages && !isCurrentChatStreaming ? (
          /* Clean & High-Contrast Empty State with Prompt Suggestions */
          <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center px-4 text-center space-y-6">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100/80 text-emerald-700 border border-emerald-300 shadow-xs">
              <Sparkles className="h-7 w-7" />
            </div>

            <div className="space-y-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-900">
                What would you like to research today?
              </h2>
              <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
                Enter any scientific inquiry, clinical hypothesis, or multidisciplinary query to synthesize verified literature.
              </p>
            </div>
          </div>

        ) : (
          <div className="mx-auto max-w-4xl w-full px-2 sm:px-4 pb-12 min-w-0 max-w-full overflow-hidden">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {isCurrentChatStreaming && (
              <StreamingMessage
                status={streamStatus}
                activeAgents={activeAgents}
              />
            )}

            {/* Live Generated Report Preview */}
            {isCurrentChatStreaming && liveReport && (
              <div className="p-1.5 sm:p-6 min-w-0 max-w-full overflow-hidden">
                <ReportPreview content={liveReport} />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <ChatInput
        onSendMessage={handleSend}
        disabled={isCurrentChatStreaming}
        isStreaming={isCurrentChatStreaming}
      />
    </div>
  );
}
