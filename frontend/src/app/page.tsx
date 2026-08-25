"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { useChatStore } from "@/stores/chatStore";

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, fetchMe } = useAuthStore();
  const { createChat } = useChatStore();

  useEffect(() => {
    fetchMe().then(() => {
      const token = localStorage.getItem("researchai_access_token");
      if (token) {
        createChat().then((id) => router.push(`/chat/${id}`));
      } else {
        router.push("/login");
      }
    });
  }, [fetchMe, createChat, router]);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
        <p className="text-xs text-gray-500 font-medium tracking-wide">Loading ResearchAI Platform...</p>
      </div>
    </div>
  );
}
