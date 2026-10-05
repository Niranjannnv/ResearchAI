"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { User, Key, Sliders, Shield, Check, Save } from "lucide-react";

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [citationStyle, setCitationStyle] = useState("apa");
  const [defaultExport, setDefaultExport] = useState("pdf");
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.patch("/settings", {
        full_name: fullName,
      });
      if (user) {
        setUser({ ...user, full_name: fullName });
      }
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2500);
    } catch (e) {
      alert("Failed to update settings");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-50/40">
      <Header title="Account & Research Preferences" />

      <div className="flex-1 overflow-y-auto p-6 max-w-3xl mx-auto w-full space-y-8">
        <form onSubmit={handleSave} className="space-y-6">
          {/* Profile Section */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <User className="h-4 w-4 text-emerald-600" />
              Researcher Profile
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700">Full Name</label>
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Dr. Jane Doe"
                  className="border-slate-300 text-slate-900"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700">Email Address</label>
                <Input
                  value={user?.email || ""}
                  disabled
                  className="bg-slate-100 text-slate-600 border-slate-200 cursor-not-allowed font-medium"
                />
              </div>
            </div>
          </div>

          {/* Research Engine Configuration */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="h-4 w-4 text-emerald-600" />
              Citation & Report Defaults
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700">Default Citation Format</label>
                <select
                  value={citationStyle}
                  onChange={(e) => setCitationStyle(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-emerald-500 focus:outline-none"
                >
                  <option value="apa">APA 7th Edition (Recommended)</option>
                  <option value="mla">MLA 9th Edition</option>
                  <option value="chicago">Chicago Manual of Style (Author-Date)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700">Preferred Export Format</label>
                <select
                  value={defaultExport}
                  onChange={(e) => setDefaultExport(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-emerald-500 focus:outline-none"
                >
                  <option value="pdf">PDF (Print Executive Layout)</option>
                  <option value="docx">Word (.docx)</option>
                  <option value="markdown">Markdown (.md)</option>
                  <option value="html">Interactive HTML</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security & Authentication Details */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Shield className="h-4 w-4 text-emerald-600" />
              Security & Access Control
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed font-normal">
              Authenticated via <strong className="capitalize text-slate-900 font-semibold">{user?.auth_provider || "email"}</strong> with secure HTTP-only sessions, JWT rotation, and sliding rate limits.
            </p>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            {isSaved && (
              <span className="text-xs font-bold text-emerald-700 flex items-center gap-1">
                <Check className="h-4 w-4" /> Preferences saved!
              </span>
            )}
            <Button type="submit" disabled={saving} className="gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold">
              <Save className="h-4 w-4" />
              <span>{saving ? "Saving..." : "Save Preferences"}</span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
