"use client";

import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";
import { useRouter } from "next/navigation";
import { LogOut, User as UserIcon } from "lucide-react";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="h-16 bg-secondary border-b border-border flex items-center justify-between px-6 shrink-0 z-10 sticky top-0">
      <Link href="/dashboard" className="flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-primary to-accent flex items-center justify-center text-secondary font-heading font-bold text-lg">
          J
        </div>
        <span className="font-heading font-bold text-xl tracking-tight text-white">
          JourneyForge
        </span>
      </Link>

      {user && (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-300 bg-background rounded-full px-3 py-1 border border-border">
            <UserIcon size={14} />
            {user.name}
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-400 hover:text-red-400 transition-colors p-2 rounded-md hover:bg-red-400/10"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </header>
  );
}
