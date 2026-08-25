import { create } from "zustand";
import { User, AuthTokens } from "@/types";
import { api } from "@/lib/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (tokens: AuthTokens) => void;
  setUser: (user: User | null) => void;
  fetchMe: () => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: typeof window !== "undefined" && !!localStorage.getItem("researchai_access_token"),
  isLoading: true,

  setAuth: (tokens: AuthTokens) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("researchai_access_token", tokens.access_token);
      localStorage.setItem("researchai_refresh_token", tokens.refresh_token);
    }
    set({ isAuthenticated: true });
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user, isLoading: false });
  },

  fetchMe: async () => {
    try {
      set({ isLoading: true });
      const { data } = await api.get<User>("/auth/me");
      set({ user: data, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  logout: async () => {
    try {
      await api.post("/auth/logout");
    } catch (e) {
      // ignore
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("researchai_access_token");
        localStorage.removeItem("researchai_refresh_token");
        set({ user: null, isAuthenticated: false, isLoading: false });
        window.location.href = "/login";
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    }
  },
}));
