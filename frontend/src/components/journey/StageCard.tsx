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
}

export function StageCard({ stage, isSelected, onClick, onNameChange }: StageCardProps) {
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
    >
      {/* Top accent line */}
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
        
        {/* Drag handle */}
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
