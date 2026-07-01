import React from "react";
import { Stage, StageItem } from "@/types/journey";
import { Plus, X, Sparkles, Check, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DetailPanelProps {
  stage: Stage | null;
  activeTab: string;
  onTabChange: (tab: string) => void;
  onClose: () => void;
  onAddItem: (stageId: string, type: string, text: string) => void;
  onUpdateItem: (stageId: string, type: string, itemId: string, text: string) => void;
  onDeleteItem: (stageId: string, type: string, itemId: string) => void;
  onAiSuggest?: (stageId: string, type: string) => void;
  aiSuggestions?: string[];
  isAiLoading?: boolean;
}

export function DetailPanel({
  stage,
  activeTab,
  onTabChange,
  onClose,
  onAddItem,
  onUpdateItem,
  onDeleteItem,
  onAiSuggest,
  aiSuggestions = [],
  isAiLoading = false,
}: DetailPanelProps) {
  const [newItemText, setNewItemText] = React.useState("");

  if (!stage) return null;

  const items = 
    activeTab === "Goals" ? stage.goals :
    activeTab === "Touchpoints" ? stage.touchpoints :
    stage.content;
    
  const typeKey = activeTab.toLowerCase().replace(/s$/, ""); // goal, touchpoint, content

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemText.trim()) return;
    onAddItem(stage.id, typeKey, newItemText);
    setNewItemText("");
  };

  return (
    <div className="absolute bottom-0 left-0 right-0 h-1/3 min-h-[300px] bg-secondary border-t border-border shadow-2xl flex flex-col z-20 transition-transform duration-300">
      <div className="flex items-center justify-between px-6 py-3 border-b border-border bg-[var(--background)]">
        <div className="flex items-center gap-4">
          <h3 className="font-heading font-semibold text-lg text-white flex items-center gap-2">
            <span>{stage.icon}</span> {stage.name}
          </h3>
          <div className="flex bg-secondary rounded-md p-1">
            {["Goals", "Touchpoints", "Content"].map((tab) => (
              <button
                key={tab}
                onClick={() => onTabChange(tab)}
                className={`px-4 py-1 text-sm font-medium rounded transition-colors ${
                  activeTab === tab ? "bg-primary/20 text-primary" : "text-gray-400 hover:text-white"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white p-1 rounded-md hover:bg-secondary-hover transition-colors">
          <X size={20} />
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            <ul className="space-y-3 mb-6">
              {items.map((item) => (
                <li key={item.id} className="flex items-center gap-3 bg-[var(--background)] border border-border p-3 rounded-lg group hover:border-primary/50 transition-colors">
                  <div className="flex-1">
                    <input
                      type="text"
                      className="w-full bg-transparent border-none focus:outline-none text-white text-sm"
                      value={item.text}
                      onChange={(e) => onUpdateItem(stage.id, typeKey, item.id, e.target.value)}
                    />
                  </div>
                  <button 
                    onClick={() => onDeleteItem(stage.id, typeKey, item.id)}
                    className="text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1"
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>

            <form onSubmit={handleAdd} className="flex gap-2">
              <input
                type="text"
                placeholder={`Add a new ${typeKey}...`}
                className="flex-1 bg-[var(--background)] border border-border rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
              />
              <Button type="submit" variant="secondary" className="px-4">
                <Plus size={18} />
              </Button>
            </form>
          </div>
        </div>

        {/* AI Suggestions Panel */}
        <div className="w-80 border-l border-border bg-[var(--background)] p-6 overflow-y-auto flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles size={18} className="text-accent" />
            <h4 className="font-medium text-white text-sm">AI Suggestions</h4>
          </div>
          
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full mb-4 border-accent/30 text-accent hover:bg-accent/10"
            onClick={() => onAiSuggest?.(stage.id, typeKey)}
            isLoading={isAiLoading}
          >
            Generate {activeTab}
          </Button>
          
          {aiSuggestions.length > 0 && (
            <ul className="space-y-3 flex-1">
              {aiSuggestions.map((suggestion, idx) => (
                <li key={idx} className="bg-secondary p-3 rounded-lg border border-border text-sm text-gray-300">
                  <p className="mb-3 leading-relaxed">{suggestion}</p>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full h-8 text-primary hover:text-primary-hover hover:bg-primary/10 border border-primary/20"
                    onClick={() => onAddItem(stage.id, typeKey, suggestion)}
                  >
                    <Check size={14} className="mr-1" /> Add to {activeTab}
                  </Button>
                </li>
              ))}
            </ul>
          )}
          
          {!isAiLoading && aiSuggestions.length === 0 && (
            <div className="text-center text-sm text-gray-500 mt-10">
              Click generate to get smart suggestions for this stage based on industry best practices.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
