import { create } from "zustand";
import { Chat, Message, SourceResult, CitationItem, ReportContent, AgentStreamEvent } from "@/types";
import { api } from "@/lib/api";

interface ChatState {
  chats: Chat[];
  currentChat: Chat | null;
  messages: Message[];
  isLoadingChats: boolean;
  isStreaming: boolean;
  streamStatus: string | null;
  activeAgents: string[];
  liveSources: SourceResult[];
  liveCitations: CitationItem[];
  liveReport: ReportContent | null;

  fetchChats: () => Promise<void>;
  createChat: (title?: string) => Promise<string>;
  selectChat: (chatId: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
  renameChat: (chatId: string, title: string) => Promise<void>;
  sendMessage: (chatId: string, content: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  currentChat: null,
  messages: [],
  isLoadingChats: false,
  isStreaming: false,
  streamStatus: null,
  activeAgents: [],
  liveSources: [],
  liveCitations: [],
  liveReport: null,

  fetchChats: async () => {
    try {
      set({ isLoadingChats: true });
      const { data } = await api.get("/chats");
      set({ chats: data.chats || [], isLoadingChats: false });
    } catch (e) {
      set({ isLoadingChats: false });
    }
  },

  createChat: async (title = "New Research Chat") => {
    const { data } = await api.post("/chats", { title });
    set((state) => ({ chats: [data, ...state.chats], currentChat: data, messages: [] }));
    return data.id;
  },

  selectChat: async (chatId: string) => {
    try {
      const { data } = await api.get(`/chats/${chatId}`);
      set({
        currentChat: data,
        messages: data.messages || [],
        streamStatus: null,
        liveSources: [],
        liveCitations: [],
        liveReport: null,
      });
    } catch (e) {
      console.error("Failed to fetch chat detail", e);
    }
  },

  deleteChat: async (chatId: string) => {
    await api.delete(`/chats/${chatId}`);
    set((state) => ({
      chats: state.chats.filter((c) => c.id !== chatId),
      currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
      messages: state.currentChat?.id === chatId ? [] : state.messages,
    }));
  },

  renameChat: async (chatId: string, title: string) => {
    const { data } = await api.patch(`/chats/${chatId}`, { title });
    set((state) => ({
      chats: state.chats.map((c) => (c.id === chatId ? { ...c, title: data.title } : c)),
      currentChat: state.currentChat?.id === chatId ? { ...state.currentChat, title: data.title } : state.currentChat,
    }));
  },

  sendMessage: async (chatId: string, content: string) => {
    let targetChatId = chatId;
    if (targetChatId === "new" || !targetChatId) {
      try {
        targetChatId = await get().createChat(content.slice(0, 50) + "...");
        if (typeof window !== "undefined") {
          window.history.replaceState(null, "", `/chat/${targetChatId}`);
        }
      } catch (err) {
        targetChatId = "new";
      }
    }

    const userMsg: Message = {
      id: "temp-" + Date.now(),
      chat_id: targetChatId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamStatus: "Initializing Mother Agent...",
      activeAgents: [],
      liveSources: [],
      liveCitations: [],
      liveReport: null,
    }));

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = typeof window !== "undefined" ? localStorage.getItem("researchai_access_token") : "";

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chats/${targetChatId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content, stream: true }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.replace("data: ", "").trim();
            if (jsonStr === "[DONE]") {
              set({ isStreaming: false, streamStatus: null });
              // Refresh chat to get persistent IDs & metadata
              if (targetChatId !== "new") {
                get().selectChat(targetChatId);
              }
              get().fetchChats();
              return;
            }

            try {
              const event: AgentStreamEvent = JSON.parse(jsonStr);
              if (event.type === "status") {
                set({
                  streamStatus: event.message || "Synthesizing research...",
                  activeAgents: event.data?.active_agents || get().activeAgents,
                });
              } else if (event.type === "complete") {
                if (event.chat_id && event.chat_id !== targetChatId) {
                  targetChatId = event.chat_id;
                  if (typeof window !== "undefined") {
                    window.history.replaceState(null, "", `/chat/${targetChatId}`);
                  }
                }
                set({
                  liveReport: event.report || null,
                  liveSources: event.sources || [],
                  liveCitations: event.citations || [],
                  isStreaming: false,
                  streamStatus: null,
                });
              }
            } catch (err) {
              // Ignore non-json lines
            }
          }
        }
      }
    } catch (e) {
      console.error("Stream failed", e);
      set({
        isStreaming: false,
        streamStatus: "Research encountered an issue. Please try again.",
      });
    }
  },
}));
