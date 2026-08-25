"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, User, Mail, Lock, ShieldCheck, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { GoogleAuthButton } from "@/components/auth/GoogleAuthButton";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Password Security Checks
  const hasMinLength = password.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const isPasswordSecure = hasMinLength && hasLetter && hasNumber;

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isPasswordSecure) {
      setError("Please ensure your password meets all security requirements.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      await api.post("/auth/register", {
        email,
        username,
        full_name: fullName || undefined,
        password,
      });

      // Registration successful — send to login page
      router.push("/login?registered=1");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please check your inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#fcfdfc] px-4 py-12">
      <div className="w-full max-w-md space-y-6 rounded-3xl border border-gray-200/80 bg-white p-8 shadow-float">
        {/* Brand */}
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="h-10 w-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-sm">
            <Sparkles className="h-5 w-5" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900">
            Create ResearchAI Account
          </h1>
          <p className="text-xs text-gray-500 max-w-xs">
            Start producing verified, multi-agent scientific intelligence reports
          </p>
        </div>

        {error && (
          <div className="rounded-xl bg-red-50 border border-red-200 p-3 text-xs text-red-700">
            {error}
          </div>
        )}

        {/* Google One-Click Sign-Up */}
        <GoogleAuthButton mode="signup" />

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-700">Full Name</label>
            <div className="relative">
              <Input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Jane Doe"
                className="pl-9 text-xs"
              />
              <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-700">Username</label>
            <Input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="janedoe"
              className="text-xs"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-700">Email Address</label>
            <div className="relative">
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@institution.edu"
                className="pl-9 text-xs"
              />
              <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-700">Secure Password</label>
            <div className="relative">
              <Input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="pl-9 text-xs"
              />
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            </div>

            {/* Password Strength Checklist */}
            {password.length > 0 && (
              <div className="rounded-lg bg-gray-50 p-2.5 space-y-1 text-[11px] text-gray-600 border border-gray-100 mt-1.5">
                <div className="flex items-center gap-1.5">
                  {hasMinLength ? (
                    <Check className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                  ) : (
                    <X className="h-3.5 w-3.5 text-gray-400 shrink-0" />
                  )}
                  <span className={hasMinLength ? "text-emerald-800 font-medium" : ""}>
                    At least 8 characters
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {hasLetter ? (
                    <Check className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                  ) : (
                    <X className="h-3.5 w-3.5 text-gray-400 shrink-0" />
                  )}
                  <span className={hasLetter ? "text-emerald-800 font-medium" : ""}>
                    Contains letters (a-z, A-Z)
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {hasNumber ? (
                    <Check className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                  ) : (
                    <X className="h-3.5 w-3.5 text-gray-400 shrink-0" />
                  )}
                  <span className={hasNumber ? "text-emerald-800 font-medium" : ""}>
                    Contains numbers (0-9)
                  </span>
                </div>
              </div>
            )}
          </div>

          <Button
            type="submit"
            disabled={loading || (password.length > 0 && !isPasswordSecure)}
            className="w-full gap-2 text-xs font-semibold"
          >
            <span>{loading ? "Creating Secure Account..." : "Create Verified Account"}</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        {/* Security Assurance Badge */}
        <div className="rounded-xl bg-slate-50 border border-slate-100 p-3 flex items-center gap-2.5 text-[11px] text-slate-600">
          <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
          <span>Zero-Knowledge Password Hashing & Verified OAuth 2.0 Integration</span>
        </div>

        <div className="text-center pt-1 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-emerald-600 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
