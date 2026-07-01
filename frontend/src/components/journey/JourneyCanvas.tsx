"use client";

import React from "react";
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

  const isBranching = stages.some(
    (s) => s.name.toLowerCase().includes("branch a") || s.name.toLowerCase().includes("branch b")
  );

  const getLayoutCoordinates = (stages: Stage[]) => {
    return stages.map((stage) => {
      const name = stage.name.toLowerCase();
      const pos = stage.position;
      
      let row = 1; // Middle
      let col = pos;
      
      if (name.includes("branch a")) {
        row = 0; // Top
        col = pos - 1;
      } else if (name.includes("branch b")) {
        row = 2; // Bottom
        col = pos - 3;
      } else if (pos >= 7) {
        col = pos - 3; // Shift post-branch
      }
      
      return { stage, row, col };
    });
  };

  const getPort = (item: { stage: Stage; row: number; col: number }, portName: "left" | "right" | "top" | "bottom") => {
    const name = item.stage.name.toLowerCase();
    const icon = item.stage.icon;
    const isSplit = icon === "💎" || icon === "🔶" || name.includes("split") || name.includes("?");
    const isWait = icon === "⏳" || icon === "⏱️" || name.includes("wait");

    const cellX = item.col * 300;
    const cellY = item.row * 170;

    if (isSplit) {
      const leftOffset = 32;
      switch (portName) {
        case "left": return { x: cellX + leftOffset, y: cellY + 80 };
        case "right": return { x: cellX + leftOffset + 160, y: cellY + 80 };
        case "top": return { x: cellX + leftOffset + 80, y: cellY };
        case "bottom": return { x: cellX + leftOffset + 80, y: cellY + 160 };
      }
    } else if (isWait) {
      const leftOffset = 16;
      switch (portName) {
        case "left": return { x: cellX + leftOffset, y: cellY + 56 };
        case "right": return { x: cellX + leftOffset + 192, y: cellY + 56 };
        case "top": return { x: cellX + leftOffset + 96, y: cellY };
        case "bottom": return { x: cellX + leftOffset + 96, y: cellY + 112 };
      }
    } else {
      switch (portName) {
        case "left": return { x: cellX, y: cellY + 72 };
        case "right": return { x: cellX + 224, y: cellY + 72 };
        case "top": return { x: cellX + 112, y: cellY };
        case "bottom": return { x: cellX + 112, y: cellY + 144 };
      }
    }
  };

  const getPortCoordinates = (
    from: { stage: Stage; row: number; col: number },
    to: { stage: Stage; row: number; col: number }
  ) => {
    if (from.col === to.col) {
      // Vertical flow
      if (from.row > to.row) {
        // UP
        return {
          start: getPort(from, "top"),
          end: getPort(to, "bottom")
        };
      } else {
        // DOWN
        return {
          start: getPort(from, "bottom"),
          end: getPort(to, "top")
        };
      }
    } else {
      // Horizontal / Diagonal flow
      return {
        start: getPort(from, "right"),
        end: getPort(to, "left")
      };
    }
  };

  const getConnections = (layoutItems: { stage: Stage; row: number; col: number }[]) => {
    const connections: { from: { col: number; row: number }; to: { col: number; row: number } }[] = [];
    
    // Dynamic lookup by position index of the stages
    const findCoordsByPos = (pos: number) => {
      const item = layoutItems.find((it) => it.stage.position === pos);
      return item ? { col: item.col, row: item.row } : null;
    };

    const pos0 = findCoordsByPos(0);
    const pos1 = findCoordsByPos(1);
    const pos2 = findCoordsByPos(2);
    const pos3 = findCoordsByPos(3);
    const pos4 = findCoordsByPos(4);
    const pos5 = findCoordsByPos(5);
    const pos6 = findCoordsByPos(6);
    const pos7 = findCoordsByPos(7);
    const pos8 = findCoordsByPos(8);

    if (pos0 && pos1) connections.push({ from: pos0, to: pos1 });
    if (pos1 && pos2) connections.push({ from: pos1, to: pos2 });
    
    // Split branches
    if (pos2 && pos3) connections.push({ from: pos2, to: pos3 }); // Split to Branch A (Discovery Call)
    if (pos2 && pos5) connections.push({ from: pos2, to: pos5 }); // Split to Branch B (Wait 7 Days)
    
    // Inside branches
    if (pos3 && pos4) connections.push({ from: pos3, to: pos4 }); // Discovery -> Proposal
    if (pos5 && pos6) connections.push({ from: pos5, to: pos6 }); // Wait -> Nurturing Email
    
    // Merges
    if (pos4 && pos7) connections.push({ from: pos4, to: pos7 }); // Proposal -> Conversion
    if (pos6 && pos7) connections.push({ from: pos6, to: pos7 }); // Nurturing Email -> Conversion
    
    // End
    if (pos7 && pos8) connections.push({ from: pos7, to: pos8 }); // Conversion -> Customer Advocacy
    
    return connections;
  };

  const drawBezier = (start: { x: number; y: number }, end: { x: number; y: number }) => {
    if (start.y === end.y) {
      return `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
    }
    const controlX = start.x + (end.x - start.x) / 2;
    return `M ${start.x} ${start.y} C ${controlX} ${start.y}, ${controlX} ${end.y}, ${end.x} ${end.y}`;
  };

  if (isBranching) {
    const layoutItems = getLayoutCoordinates(stages);
    const connections = getConnections(layoutItems);

    return (
      <div 
        className="flex-1 overflow-auto bg-[var(--background)] p-8 relative min-h-[580px]"
        onClick={() => onSelectStage(null)}
      >
        <div className="relative w-[2100px] h-[520px]">
          {/* SVG Connection curves */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            <defs>
              <marker
                id="arrow"
                viewBox="0 0 10 10"
                refX="6"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--border)" />
              </marker>
            </defs>
            {connections.map((conn, idx) => {
              const fromItem = layoutItems.find((item) => item.col === conn.from.col && item.row === conn.from.row);
              const toItem = layoutItems.find((item) => item.col === conn.to.col && item.row === conn.to.row);
              if (!fromItem || !toItem) return null;

              const { start, end } = getPortCoordinates(fromItem, toItem);

              return (
                <path
                  key={idx}
                  d={drawBezier(start, end)}
                  stroke="var(--border)"
                  strokeWidth="2"
                  fill="none"
                  markerEnd="url(#arrow)"
                  className="opacity-60 hover:opacity-100 transition-opacity"
                />
              );
            })}
          </svg>

          {/* Node cards layer */}
          {layoutItems.map((item) => (
            <div
              key={item.stage.id}
              className="absolute z-10"
              style={{
                left: item.col * 300,
                top: item.row * 170,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <StageCard
                stage={item.stage}
                isSelected={selectedStageId === item.stage.id}
                onClick={() => onSelectStage(item.stage.id)}
                onNameChange={(name) => onUpdateStageName(item.stage.id, name)}
                isFlowMode={true}
              />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Fallback default Linear scrollable Kanban view
  return (
    <div 
      className="flex-1 overflow-x-auto overflow-y-hidden bg-[var(--background)] p-8 flex items-center"
      onClick={() => onSelectStage(null)}
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
                <StageConnector />
              </React.Fragment>
            ))}
          </SortableContext>
        </DndContext>
        
        <button
          onClick={onAddStage}
          aria-label="Add Stage"
          title="Add Stage"
          data-testid="add-stage-button"
          className="w-16 h-16 rounded-xl border-2 border-dashed border-border flex items-center justify-center text-gray-500 hover:text-primary hover:border-primary hover:bg-primary/5 transition-all flex-shrink-0 cursor-pointer"
        >
          <Plus size={24} />
        </button>
      </div>
    </div>
  );
}
