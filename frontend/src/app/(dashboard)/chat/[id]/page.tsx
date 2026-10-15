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

  const isCurrentChatStreaming =
    isStreaming &&
    (streamingChatId === chatId ||
      chatId === "new" ||
      Boolean(currentChat && streamingChatId === currentChat.id));

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

      {!hasMessages && !isCurrentChatStreaming ? (
        /* FIXED Centered Search Home on Main Page */
        <div className="flex-1 flex flex-col items-center justify-center px-3 sm:px-6 overflow-hidden select-none">
          <div className="w-full max-w-2xl flex flex-col items-center text-center my-auto">
            {/* Sparkle AI Icon */}
            <div className="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-2xl bg-emerald-100/90 text-emerald-700 border border-emerald-300 shadow-xs mb-3 sm:mb-4">
              <Sparkles className="h-6 w-6 sm:h-7 sm:w-7" />
            </div>

            {/* Title & Subtitle */}
            <div className="space-y-1.5 sm:space-y-2 max-w-md sm:max-w-lg mb-4 sm:mb-6">
              <h1 className="text-xl sm:text-3xl font-extrabold tracking-tight text-slate-900 leading-tight">
                What would you like to research today?
              </h1>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed px-2">
                Enter any scientific inquiry, clinical hypothesis, or multidisciplinary query to synthesize verified literature.
              </p>
            </div>

            {/* Front-and-Center Search Input */}
            <div className="w-full">
              <ChatInput
                onSendMessage={handleSend}
                disabled={isCurrentChatStreaming}
                isStreaming={isCurrentChatStreaming}
                centered={true}
              />
            </div>
          </div>
        </div>
      ) : (
        /* Active Research Chat Feed + Bottom Fixed Input Bar */
        <>
          <div className="flex-1 overflow-y-auto overflow-x-hidden min-w-0 max-w-full">
            <div className="mx-auto max-w-4xl w-full px-2 sm:px-4 pb-8 min-w-0 max-w-full overflow-hidden">
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
          </div>

          {/* Bottom Docked Input Bar during conversation */}
          <div className="shrink-0 w-full bg-slate-50/90 backdrop-blur-sm border-t border-slate-200/80 z-10">
            <ChatInput
              onSendMessage={handleSend}
              disabled={isCurrentChatStreaming}
              isStreaming={isCurrentChatStreaming}
              centered={false}
            />
          </div>
        </>
      )}
    </div>
  );
}
