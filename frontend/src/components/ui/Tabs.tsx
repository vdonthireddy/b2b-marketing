import React from "react";

export function Tabs({ tabs, activeTab, onChange }: { tabs: string[]; activeTab: string; onChange: (tab: string) => void }) {
  return (
    <div className="flex space-x-1 border-b border-border bg-secondary/50 p-1">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={`flex-1 rounded-sm px-3 py-1.5 text-sm font-medium transition-all ${
            activeTab === tab
              ? "bg-[var(--background)] text-primary shadow-sm"
              : "text-gray-400 hover:text-gray-200 hover:bg-[var(--card)]"
          }`}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}
