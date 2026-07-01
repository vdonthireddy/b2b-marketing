"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuthStore } from "@/stores/authStore";
import { Sparkles, Loader2, CheckCircle, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";

interface AgentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AgentModal({ isOpen, onClose }: AgentModalProps) {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState<"idle" | "generating" | "success" | "error">("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setStatus("generating");
    setErrorMessage("");
    setStatusMessage("Agent is drafting journey structure...");
    
    // Simulate some progress updates since it's a long-polling request
    const interval = setInterval(() => {
      setStatusMessage(prev => {
        if (prev === "Agent is drafting journey structure...") return "Validating output against schema...";
        if (prev === "Validating output against schema...") return "Fixing structural errors (if any)...";
        if (prev === "Fixing structural errors (if any)...") return "Finalizing journey components...";
        return prev;
      });
    }, 3000);

    try {
      const response = await api.post("/api/ai/generate-journey", 
        { prompt },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      
      clearInterval(interval);
      setStatus("success");
      setStatusMessage("Journey generated successfully!");
      
      // Redirect after a short delay
      setTimeout(() => {
        onClose();
        router.push(`/journeys/${response.data.id}`);
        // Reset state for next time
        setTimeout(() => {
          setStatus("idle");
          setPrompt("");
        }, 500);
      }, 1500);
      
    } catch (err: any) {
      clearInterval(interval);
      setStatus("error");
      setErrorMessage(err.response?.data?.detail || err.message || "Failed to generate journey.");
    }
  };

  const handleClose = () => {
    if (status !== "generating") {
      onClose();
      // Reset after animation
      setTimeout(() => {
        setStatus("idle");
        setPrompt("");
        setErrorMessage("");
      }, 200);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="✨ Generate Journey with AI">
      <div className="space-y-4">
        {status === "idle" && (
          <form onSubmit={handleGenerate} className="space-y-4">
            <p className="text-sm text-gray-400">
              Describe your target audience and goal. Our AI agent will design a complete, multi-stage customer journey with goals, touchpoints, and content.
            </p>
            
            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-foreground mb-1">
                Your Prompt
              </label>
              <textarea
                id="prompt"
                className="flex w-full rounded-md border border-border bg-secondary/50 px-3 py-2 text-sm text-foreground ring-offset-[var(--background)] placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                rows={4}
                placeholder="e.g. Create a B2B SaaS onboarding journey for enterprise Marketing Managers, focused on product adoption and upselling."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
                autoFocus
              />
            </div>
            
            <div className="pt-4 flex justify-end gap-3">
              <Button type="button" variant="ghost" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" className="bg-gradient-to-r from-purple-600 to-primary hover:from-purple-700 hover:to-primary/90 flex items-center gap-2">
                <Sparkles size={16} /> Generate
              </Button>
            </div>
          </form>
        )}

        {status === "generating" && (
          <div className="py-8 flex flex-col items-center justify-center text-center space-y-4">
            <Loader2 className="h-10 w-10 text-primary animate-spin" />
            <h3 className="text-lg font-medium text-white">Agent is Working...</h3>
            <p className="text-sm text-primary font-medium animate-pulse">{statusMessage}</p>
            <p className="text-xs text-gray-500 max-w-sm mt-2">
              This process involves generating JSON, validating it against our database models, and autonomously fixing any schema errors. It may take 15-30 seconds.
            </p>
          </div>
        )}

        {status === "success" && (
          <div className="py-8 flex flex-col items-center justify-center text-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-500" />
            <h3 className="text-lg font-medium text-white">Success!</h3>
            <p className="text-sm text-gray-400">Redirecting to your new journey...</p>
          </div>
        )}

        {status === "error" && (
          <div className="py-6 flex flex-col items-center text-center space-y-4">
            <AlertTriangle className="h-10 w-10 text-red-500" />
            <h3 className="text-lg font-medium text-white">Generation Failed</h3>
            <div className="text-sm text-red-400 bg-red-500/10 p-3 rounded border border-red-500/20 max-w-md break-words">
              {errorMessage}
            </div>
            <Button onClick={() => setStatus("idle")} variant="outline" className="mt-4">
              Try Again
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
}
