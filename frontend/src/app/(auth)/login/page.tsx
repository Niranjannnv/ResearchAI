"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { GoogleAuthButton } from "@/components/auth/GoogleAuthButton";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const registered = searchParams.get("registered") === "1";
  const cancelled = searchParams.get("cancelled") === "1";
  const { setAuth, fetchMe } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && window.location.hash) {
      const p = new URLSearchParams(window.location.hash.substring(1));
      const at = p.get("access_token"), rt = p.get("refresh_token");
      if (at && rt) {
        setAuth({ access_token: at, refresh_token: rt, token_type: "bearer", expires_in: 3600 });
        fetchMe().then(() => router.push("/chat/new"));
      }
    }
  }, [setAuth, fetchMe, router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email, password });
      setAuth(data);
      await fetchMe();
      router.push("/chat/new");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-8">

        {/* Brand */}
        <div className="space-y-1">
          <div className="h-8 w-8 rounded-lg bg-emerald-600 flex items-center justify-center mb-4">
            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Sign in</h1>
          <p className="text-sm text-gray-500">to ResearchAI</p>
        </div>

        {/* Registration success */}
        {registered && (
          <div className="flex items-center gap-2 text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2.5">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>Account created! Sign in to continue.</span>
          </div>
        )}

        {/* Google sign-in cancelled */}
        {cancelled && (
          <p className="text-xs text-gray-400 text-center">
            Google sign-in was cancelled. You can try again or sign in with email.
          </p>
        )}

        {/* Error */}
        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        {/* Google */}
        <GoogleAuthButton mode="signin" />

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-600">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-3 py-2.5 rounded-lg border border-gray-200 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-gray-400 transition-colors bg-white"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="text-xs font-medium text-gray-600">Password</label>
              <a href="#" className="text-xs text-gray-400 hover:text-gray-600 transition-colors">Forgot?</a>
            </div>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2.5 pr-10 rounded-lg border border-gray-200 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-gray-400 transition-colors bg-white"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 active:scale-[0.99] disabled:opacity-40 transition-all"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400">
          No account?{" "}
          <Link href="/register" className="text-gray-900 font-medium hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
