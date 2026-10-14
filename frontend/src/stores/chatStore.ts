import { create } from "zustand";
import { Chat, Message, SourceResult, CitationItem, ReportContent, AgentStreamEvent } from "@/types";
import { api } from "@/lib/api";

interface ChatState {
  chats: Chat[];
  currentChat: Chat | null;
  messages: Message[];
  isLoadingChats: boolean;
  isStreaming: boolean;
  streamingChatId: string | null;
  streamStatus: string | null;
  activeAgents: string[];
  liveSources: SourceResult[];
  liveCitations: CitationItem[];
  liveReport: ReportContent | null;
  abortController: AbortController | null;

  fetchChats: () => Promise<void>;
  createChat: (title?: string) => Promise<string>;
  selectChat: (chatId: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
  renameChat: (chatId: string, title: string) => Promise<void>;
  sendMessage: (chatId: string, content: string, displayContent?: string) => Promise<void>;
  stopStreaming: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  currentChat: null,
  messages: [],
  isLoadingChats: false,
  isStreaming: false,
  streamingChatId: null,
  streamStatus: null,
  activeAgents: [],
  liveSources: [],
  liveCitations: [],
  liveReport: null,
  abortController: null,

  stopStreaming: () => {
    const { abortController, streamingChatId, currentChat } = get();
    if (abortController) {
      abortController.abort();
    }
    const stoppedChatId = streamingChatId || currentChat?.id || "new";
    const stoppedMsg: Message = {
      id: "stopped-" + Date.now(),
      chat_id: stoppedChatId,
      role: "assistant",
      content: "_Research paused by user._",
      metadata_: { stopped: true },
      created_at: new Date().toISOString(),
    };
    set((state) => ({
      messages: state.currentChat?.id === stoppedChatId
        ? [...state.messages, stoppedMsg]
        : state.messages,
      isStreaming: false,
      streamingChatId: null,
      streamStatus: null,
      abortController: null,
    }));
  },

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
    try {
      const { data } = await api.post("/chats", { title });
      set((state) => ({
        chats: [data, ...state.chats],
        currentChat: data,
        messages: [],
        ...(state.streamingChatId === data.id ? {} : {
          streamStatus: null,
          liveSources: [],
          liveCitations: [],
          liveReport: null,
        }),
      }));
      return data.id;
    } catch (err) {
      console.error("Failed to create chat on server:", err);
      const fallbackChat: Chat = {
        id: `local-${Date.now()}`,
        title,
        is_archived: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      set((state) => ({
        chats: [fallbackChat, ...state.chats],
        currentChat: fallbackChat,
        messages: [],
      }));
      return fallbackChat.id;
    }
  },

  selectChat: async (chatId: string) => {
    try {
      const isThisChatStreaming = get().streamingChatId === chatId;
      const { data } = await api.get(`/chats/${chatId}`);
      set({
        currentChat: data,
        messages: data.messages || [],
        ...(isThisChatStreaming ? {} : {
          streamStatus: null,
          liveSources: [],
          liveCitations: [],
          liveReport: null,
        }),
      });
    } catch (e) {
      console.error("Failed to fetch chat detail", e);
    }
  },

  deleteChat: async (chatId: string) => {
    set((state) => ({
      chats: state.chats.filter((c) => c.id !== chatId),
      currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
      messages: state.currentChat?.id === chatId ? [] : state.messages,
      streamingChatId: state.streamingChatId === chatId ? null : state.streamingChatId,
      isStreaming: state.streamingChatId === chatId ? false : state.isStreaming,
    }));
    try {
      await api.delete(`/chats/${chatId}`);
    } catch (err) {
      console.error("Failed to delete chat on server:", err);
    }
  },

  renameChat: async (chatId: string, title: string) => {
    // Optimistic update
    set((state) => ({
      chats: state.chats.map((c) => (c.id === chatId ? { ...c, title } : c)),
      currentChat: state.currentChat?.id === chatId ? { ...state.currentChat, title } : state.currentChat,
    }));
    try {
      const { data } = await api.patch(`/chats/${chatId}`, { title });
      if (data?.title) {
        set((state) => ({
          chats: state.chats.map((c) => (c.id === chatId ? { ...c, title: data.title } : c)),
          currentChat: state.currentChat?.id === chatId ? { ...state.currentChat, title: data.title } : state.currentChat,
        }));
      }
    } catch (err) {
      console.error("Failed to rename chat on server:", err);
    }
  },

  sendMessage: async (chatId: string, content: string, displayContent?: string) => {
    let targetChatId = chatId;
    if (targetChatId === "new" || !targetChatId) {
      try {
        targetChatId = await get().createChat(content.slice(0, 80).trim());
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
      // Show the clean display text in the bubble; fall back to content if no displayContent
      content: displayContent || content,
      created_at: new Date().toISOString(),
    };

    const controller = new AbortController();

    set((state) => ({
      messages: state.currentChat?.id === targetChatId || targetChatId === "new"
        ? [...state.messages, userMsg]
        : state.messages,
      isStreaming: true,
      streamingChatId: targetChatId,
      streamStatus: "Understanding research inquiry",
      activeAgents: [],
      liveSources: [],
      liveCitations: [],
      liveReport: null,
      abortController: controller,
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
        signal: controller.signal,
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
              const isViewing = get().currentChat?.id === targetChatId;
              set({ isStreaming: false, streamingChatId: null, streamStatus: null, abortController: null });
              // Refresh chat to get persistent IDs & metadata if user is on this chat
              if (isViewing && targetChatId !== "new") {
                get().selectChat(targetChatId);
              }
              get().fetchChats();
              return;
            }

            try {
              const event: AgentStreamEvent = JSON.parse(jsonStr);
              if (event.type === "status") {
                if (get().streamingChatId === targetChatId) {
                  set({
                    streamStatus: event.message || "Synthesizing research...",
                    activeAgents: event.data?.active_agents || get().activeAgents,
                  });
                }
              } else if (event.type === "complete") {
                if (event.chat_id && event.chat_id !== targetChatId) {
                  targetChatId = event.chat_id;
                  if (get().streamingChatId !== null) {
                    set({ streamingChatId: targetChatId });
                  }
                  if (typeof window !== "undefined" && window.location.pathname.includes("/chat/new")) {
                    window.history.replaceState(null, "", `/chat/${targetChatId}`);
                  }
                }

                // Update chat title in sidebar if backend renamed it
                const newChatTitle = event.chat_title?.trim();
                if (newChatTitle) {
                  set((s) => ({
                    chats: s.chats.map((c) =>
                      c.id === targetChatId ? { ...c, title: newChatTitle } : c
                    ),
                    currentChat:
                      s.currentChat?.id === targetChatId
                        ? { ...s.currentChat, title: newChatTitle }
                        : s.currentChat,
                  }));
                }

                const isViewing = get().currentChat?.id === targetChatId;
                if (isViewing) {
                  if (event.content && !event.report) {
                    const assistantMsg: Message = {
                      id: "msg-" + Date.now(),
                      chat_id: targetChatId,
                      role: "assistant",
                      content: event.content,
                      created_at: new Date().toISOString(),
                    };
                    set((s) => ({
                      messages: [...s.messages, assistantMsg],
                      liveReport: null,
                      liveSources: [],
                      liveCitations: [],
                      isStreaming: false,
                      streamingChatId: null,
                      streamStatus: null,
                      abortController: null,
                    }));
                  } else {
                    set({
                      liveReport: event.report || null,
                      liveSources: event.sources || [],
                      liveCitations: event.citations || [],
                      isStreaming: false,
                      streamingChatId: null,
                      streamStatus: null,
                      abortController: null,
                    });
                  }
                } else {
                  set({
                    isStreaming: false,
                    streamingChatId: null,
                    streamStatus: null,
                    abortController: null,
                  });
                }
              }
            } catch (err) {
              // Ignore non-json lines
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name === "AbortError") {
        set({ isStreaming: false, streamingChatId: null, streamStatus: null, abortController: null });
        return;
      }
      console.error("Stream failed", e);
      set({
        isStreaming: false,
        streamingChatId: null,
        streamStatus: "Research encountered an issue. Please try again.",
        abortController: null,
      });
    }
  },
}));
