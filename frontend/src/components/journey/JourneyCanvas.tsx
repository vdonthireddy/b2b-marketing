"use client";

import React, { useState } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Stage } from "@/types/journey";
import { StageCard } from "./StageCard";
import { StageConnector } from "./StageConnector";
import { Plus } from "lucide-react";

interface JourneyCanvasProps {
  stages: Stage[];
  selectedStageId: string | null;
  onSelectStage: (id: string | null) => void;
  onReorderStages: (stages: Stage[]) => void;
  onUpdateStageName: (id: string, name: string) => void;
  onAddStage: () => void;
}

export function JourneyCanvas({
  stages,
  selectedStageId,
  onSelectStage,
  onReorderStages,
  onUpdateStageName,
  onAddStage,
}: JourneyCanvasProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = stages.findIndex((s) => s.id === active.id);
      const newIndex = stages.findIndex((s) => s.id === over.id);
      
      const newStages = arrayMove(stages, oldIndex, newIndex).map((s, index) => ({
        ...s,
        position: index,
      }));
      
      onReorderStages(newStages);
    }
  };

  return (
    <div 
      className="flex-1 overflow-x-auto overflow-y-hidden bg-[var(--background)] p-8 flex items-center"
      onClick={() => onSelectStage(null)} // Deselect when clicking canvas background
    >
      <div className="flex items-center min-w-max pb-8" onClick={(e) => e.stopPropagation()}>
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={stages.map(s => s.id)}
            strategy={horizontalListSortingStrategy}
          >
            {stages.map((stage, index) => (
              <React.Fragment key={stage.id}>
                <StageCard
                  stage={stage}
                  isSelected={selectedStageId === stage.id}
                  onClick={() => onSelectStage(stage.id)}
                  onNameChange={(name) => onUpdateStageName(stage.id, name)}
                />
                {/* Don't show connector after the last stage if not dragging, but since we add a Plus button, always show it except after the Plus */}
                <StageConnector />
              </React.Fragment>
            ))}
          </SortableContext>
        </DndContext>
        
        {/* Add Stage Button */}
        <button
          onClick={onAddStage}
          className="w-16 h-16 rounded-xl border-2 border-dashed border-border flex items-center justify-center text-gray-500 hover:text-primary hover:border-primary hover:bg-primary/5 transition-all flex-shrink-0 cursor-pointer"
        >
          <Plus size={24} />
        </button>
      </div>
    </div>
  );
}
