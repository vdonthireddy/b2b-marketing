"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Route, Users, BarChart3, Settings, Briefcase } from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Journeys", href: "/journeys", icon: Route },
    { name: "Personas", href: "/personas", icon: Users },
    { name: "Leads", href: "/leads", icon: Briefcase },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-secondary border-r border-border h-[calc(100vh-64px)] flex flex-col">
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-foreground hover:bg-secondary-hover hover:text-white"
              }`}
            >
              <Icon size={18} className={isActive ? "text-primary" : "text-gray-400"} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
