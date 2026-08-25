"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Plus,
  MessageSquare,
  FileText,
  Briefcase,
  Bookmark as BookmarkIcon,
  Settings as SettingsIcon,
  LogOut,
  Trash2,
  Edit2,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useChatStore } from "@/stores/chatStore";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { chats, fetchChats, createChat, deleteChat, renameChat, currentChat } = useChatStore();
  
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleNewChat = async () => {
    const id = await createChat();
    router.push(`/chat/${id}`);
  };

  const handleStartRename = (id: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const handleSaveRename = async (id: string, e: React.FormEvent) => {
    e.preventDefault();
    if (editTitle.trim()) {
      await renameChat(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Delete this research chat?")) {
      await deleteChat(id);
      if (pathname.includes(id)) {
        router.push("/chat/new");
      }
    }
  };

  const navItems = [
    { label: "Reports", href: "/reports", icon: FileText },
    { label: "Workspace", href: "/workspace", icon: Briefcase },
    { label: "Bookmarks", href: "/bookmarks", icon: BookmarkIcon },
    { label: "Settings", href: "/settings", icon: SettingsIcon },
  ];

  return (
    <aside className="flex h-screen w-72 flex-col border-r border-gray-100 bg-[#fbfbfb] text-gray-800 select-none">
      {/* Brand Header & New Chat Button */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between px-2">
          <Link href="/" className="flex items-center gap-2 font-semibold text-gray-900 tracking-tight">
            <div className="h-7 w-7 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="text-base font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              ResearchAI
            </span>
          </Link>
          <span className="text-[10px] font-medium uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/50">
            Enterprise
          </span>
        </div>

        <button
          onClick={handleNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm font-medium text-gray-800 shadow-sm transition-all hover:bg-gray-50 hover:border-gray-300 active:scale-[0.99]"
        >
          <Plus className="h-4 w-4 text-emerald-600" />
          <span>New Research Chat</span>
        </button>
      </div>

      {/* Primary Navigation */}
      <div className="px-3 py-1 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-white text-gray-900 font-semibold shadow-xs border border-gray-200/60"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Icon className={cn("h-4 w-4", isActive ? "text-emerald-600" : "text-gray-400")} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>

      <div className="mx-4 my-2 border-t border-gray-200/60" />

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto px-3 py-1">
        <div className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
          Research History
        </div>
        
        {chats.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-gray-400">
            No research chats yet.
          </div>
        ) : (
          <div className="space-y-1">
            {chats.map((chat) => {
              const isActive = pathname === `/chat/${chat.id}`;
              const isEditing = editingId === chat.id;

              return (
                <div
                  key={chat.id}
                  onClick={() => router.push(`/chat/${chat.id}`)}
                  className={cn(
                    "group relative flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-all cursor-pointer",
                    isActive
                      ? "bg-white text-gray-900 font-medium shadow-xs border border-gray-200/60"
                      : "text-gray-600 hover:bg-gray-100/80 hover:text-gray-900"
                  )}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                    <MessageSquare className={cn("h-4 w-4 shrink-0", isActive ? "text-emerald-600" : "text-gray-400")} />
                    
                    {isEditing ? (
                      <form onSubmit={(e) => handleSaveRename(chat.id, e)} className="flex-1" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onBlur={() => setEditingId(null)}
                          autoFocus
                          className="w-full bg-white px-1.5 py-0.5 text-xs border border-emerald-500 rounded outline-none"
                        />
                      </form>
                    ) : (
                      <span className="truncate text-xs font-normal">
                        {chat.title}
                      </span>
                    )}
                  </div>

                  {!isEditing && (
                    <div className="hidden group-hover:flex items-center gap-1 shrink-0">
                      <button
                        onClick={(e) => handleStartRename(chat.id, chat.title, e)}
                        className="p-1 text-gray-400 hover:text-gray-700 rounded"
                        title="Rename"
                      >
                        <Edit2 className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(chat.id, e)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Delete"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* User Profile Footer */}
      <div className="border-t border-gray-200/60 p-3">
        <div className="flex items-center justify-between rounded-xl p-2 hover:bg-gray-100/80 transition-colors">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="h-8 w-8 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center font-semibold text-emerald-800 text-xs shrink-0">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email ? user.email.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium text-gray-900">
                {user?.full_name || user?.username || "Researcher"}
              </p>
              <p className="truncate text-[11px] text-gray-400">
                {user?.email || "user@researchai.com"}
              </p>
            </div>
          </div>

          <button
            onClick={() => logout()}
            className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-200/60 transition-colors"
            title="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
