"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { useAuthStore } from "@/stores/authStore";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, fetchMe } = useAuthStore();

  useEffect(() => {
    fetchMe().then(() => {
      const token = localStorage.getItem("researchai_access_token");
      if (!token) {
        router.push("/login");
      }
    });
  }, [fetchMe, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-white">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="fixed inset-0 flex h-[100dvh] w-full overflow-hidden bg-slate-50 select-none">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden bg-slate-50/60 min-w-0 h-full relative">
        {children}
      </main>
    </div>
  );
}


