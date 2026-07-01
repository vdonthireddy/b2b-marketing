"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { User } from "@/types/user";

export default function Login() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const res = await api.post("/api/auth/login", { email, password });
      const { access_token, refresh_token, user } = res.data;
      setAuth(access_token, refresh_token, user as User);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during login.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8 glass-card p-8">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent font-heading text-2xl font-bold text-secondary">
            J
          </div>
          <h2 className="mt-6 text-3xl font-heading font-bold text-white tracking-tight">
            Sign in to JourneyForge
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            Enterprise customer journey mapping
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-500/10 p-4 border border-red-500/20">
              <div className="text-sm text-red-400">{error}</div>
            </div>
          )}
          
          <div className="space-y-4 rounded-md shadow-sm">
            <Input
              id="email"
              name="email"
              type="text"
              autoComplete="email"
              required
              label="Email address"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              label="Password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            size="lg"
            isLoading={isLoading}
          >
            Sign in
          </Button>
        </form>
        
        <div className="text-center text-sm text-gray-400">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-primary hover:text-primary-hover">
            Create a team
          </Link>
        </div>
      </div>
    </div>
  );
}
