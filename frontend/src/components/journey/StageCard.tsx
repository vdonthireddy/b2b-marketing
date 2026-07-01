import React from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Stage } from "@/types/journey";
import { GripVertical } from "lucide-react";

interface StageCardProps {
  stage: Stage;
  isSelected: boolean;
  onClick: () => void;
  onNameChange: (name: string) => void;
  isFlowMode?: boolean;
}

export function StageCard({ stage, isSelected, onClick, onNameChange, isFlowMode = false }: StageCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: stage.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const handleNameSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    (e.target as HTMLFormElement).querySelector("input")?.blur();
  };

  const name = stage.name.toLowerCase();
  const icon = stage.icon;
  let variant: "normal" | "split" | "wait" = "normal";
  if (icon === "💎" || icon === "🔶" || name.includes("split") || name.includes("?")) {
    variant = "split";
  } else if (icon === "⏳" || icon === "⏱️" || name.includes("wait")) {
    variant = "wait";
  }

  // If in Flow Mode, render specialized visual nodes without sortable behavior
  if (isFlowMode) {
    if (variant === "split") {
      return (
        <div 
          onClick={onClick}
          className={`relative w-40 h-40 flex items-center justify-center cursor-pointer transition-all duration-200 group flex-shrink-0 ${
            isSelected ? "scale-105" : "hover:scale-105"
          }`}
        >
          {/* Diamond shape container */}
          <div 
            className={`absolute inset-0 rotate-45 border-2 rounded-xl backdrop-blur-md transition-all duration-200 bg-[var(--card)] ${
              isSelected ? "shadow-lg" : "border-border group-hover:border-gray-500"
            }`}
            style={{
              borderColor: stage.color,
              boxShadow: isSelected ? `0 0 20px -2px ${stage.color}60` : undefined,
            }}
          />
          {/* Content (No rotation to keep text straight) */}
          <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center select-none z-10">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center text-lg mb-1.5 shadow-sm"
              style={{ backgroundColor: `${stage.color}20` }}
            >
              {stage.icon}
            </div>
            <h4 className="text-xs font-heading font-bold text-white max-w-[100px] line-clamp-2 leading-tight">
              {stage.name}
            </h4>
            <p className="text-[9px] text-gray-500 mt-1 max-w-[90px] line-clamp-1">
              {stage.description}
            </p>
          </div>
          {/* Input/Output Ports */}
          <div className="absolute left-0 top-1/2 -translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20 animate-pulse" />
          <div className="absolute right-0 top-1/2 translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20 animate-pulse" />
        </div>
      );
    }

    if (variant === "wait") {
      return (
        <div 
          onClick={onClick}
          className={`relative w-48 h-28 flex flex-col items-center justify-center rounded-full border-2 bg-[var(--card)] backdrop-blur-md p-4 text-center cursor-pointer transition-all duration-200 hover:scale-105 flex-shrink-0 ${
            isSelected ? "shadow-lg border-primary" : "border-dashed border-border hover:border-gray-500"
          }`}
          style={{
            borderColor: stage.color,
            boxShadow: isSelected ? `0 0 20px -2px ${stage.color}60` : undefined,
          }}
        >
          <div className="flex items-center gap-2 mb-1 z-10">
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
              style={{ backgroundColor: `${stage.color}20` }}
            >
              {stage.icon}
            </div>
            <h4 className="text-sm font-heading font-bold text-white">
              {stage.name.replace("[Branch B] ", "").replace("[Branch A] ", "")}
            </h4>
          </div>
          <p className="text-[10px] text-gray-400 max-w-[150px] line-clamp-2 leading-tight z-10">
            {stage.description}
          </p>
          {/* Input/Output Ports */}
          <div className="absolute left-0 top-1/2 -translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20" />
          <div className="absolute right-0 top-1/2 translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20" />
        </div>
      );
    }

    // Normal Node in Flow Mode
    return (
      <div 
        onClick={onClick}
        className={`relative w-56 h-36 flex flex-col justify-between rounded-xl border bg-[var(--card)] backdrop-blur-md p-4 cursor-pointer transition-all duration-200 hover:scale-105 flex-shrink-0 ${
          isSelected ? "border-2 shadow-lg" : "border-border hover:border-gray-500"
        }`}
        style={{
          borderColor: isSelected ? stage.color : undefined,
          boxShadow: isSelected ? `0 0 20px -5px ${stage.color}80` : undefined,
        }}
      >
        <div 
          className="absolute top-0 left-0 right-0 h-1 rounded-t-xl" 
          style={{ backgroundColor: stage.color }}
        />
        <div className="flex items-center gap-3 mt-1">
          <div 
            className="w-8 h-8 rounded-lg flex items-center justify-center text-lg"
            style={{ backgroundColor: `${stage.color}20` }}
          >
            {stage.icon}
          </div>
          <h4 className="text-sm font-heading font-bold text-white line-clamp-1">
            {stage.name.replace("[Branch A] ", "").replace("[Branch B] ", "")}
          </h4>
        </div>
        <p className="text-[10px] text-gray-400 line-clamp-2 leading-relaxed mt-2 flex-1">
          {stage.description}
        </p>
        <div className="mt-2 flex gap-1.5 text-[9px] font-medium text-gray-400">
          <span className="px-1.5 py-0.5 rounded bg-secondary">{stage.goals?.length || 0} Goals</span>
          <span className="px-1.5 py-0.5 rounded bg-secondary">{stage.touchpoints?.length || 0} Touchpoints</span>
        </div>
        {/* Input/Output Ports */}
        <div className="absolute left-0 top-1/2 -translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20" />
        <div className="absolute right-0 top-1/2 translate-x-1.5 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-border bg-[var(--background)] z-20" />
      </div>
    );
  }

  // Standard Linear Kanban Mode (Sortable)
  return (
    <div
      ref={setNodeRef}
      className={`relative flex-shrink-0 w-64 bg-[var(--card)] backdrop-blur-md rounded-xl p-5 cursor-pointer transition-all duration-200 ${
        isSelected 
          ? "border-2 shadow-[0_0_15px_rgba(var(--accent-rgb),0.3)]" 
          : "border border-border hover:border-gray-500 hover:shadow-lg"
      }`}
      style={{
        ...style,
        borderColor: isSelected ? stage.color : undefined,
        boxShadow: isSelected ? `0 0 20px -5px ${stage.color}80` : undefined,
      }}
      onClick={onClick}
      data-testid="stage-card"
    >
      <div 
        className="absolute top-0 left-0 right-0 h-1 rounded-t-xl" 
        style={{ backgroundColor: stage.color }}
      />
      <div className="flex items-start justify-between mb-4 mt-2">
        <div 
          className="w-10 h-10 rounded-lg flex items-center justify-center text-xl shadow-sm"
          style={{ backgroundColor: `${stage.color}20` }}
        >
          {stage.icon}
        </div>
        <div 
          {...attributes} 
          {...listeners}
          className="text-gray-500 hover:text-white cursor-grab active:cursor-grabbing p-1"
          onClick={(e) => e.stopPropagation()}
        >
          <GripVertical size={18} />
        </div>
      </div>
      <form onSubmit={handleNameSubmit} onClick={(e) => e.stopPropagation()}>
        <input
          type="text"
          className="w-full bg-transparent border border-transparent hover:border-border focus:border-primary focus:bg-[var(--background)] rounded px-1 py-0.5 text-lg font-heading font-bold text-white mb-2 outline-none transition-colors"
          value={stage.name}
          onChange={(e) => onNameChange(e.target.value)}
        />
      </form>
      <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed h-8">
        {stage.description}
      </p>
      <div className="mt-4 flex gap-2">
        <div className="text-[10px] font-medium px-2 py-1 rounded bg-secondary text-gray-300 border border-border">
          {stage.goals?.length || 0} Goals
        </div>
        <div className="text-[10px] font-medium px-2 py-1 rounded bg-secondary text-gray-300 border border-border">
          {stage.touchpoints?.length || 0} Touchpoints
        </div>
      </div>
    </div>
  );
}
