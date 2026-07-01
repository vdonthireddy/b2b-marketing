import { Persona } from "@/stores/personaStore";
import { User as UserIcon, Plus } from "lucide-react";

interface PersonaWidgetProps {
  linkedPersonas: Persona[];
  allPersonas: Persona[];
  onLinkPersona: (personaId: string) => void;
  onUnlinkPersona: (personaId: string) => void;
}

export function PersonaWidget({ linkedPersonas, allPersonas, onLinkPersona, onUnlinkPersona }: PersonaWidgetProps) {
  // Simple implementation for now. You can expand it with a dropdown to link personas.
  return (
    <div className="w-64 border-r border-border bg-secondary/30 flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h3 className="font-heading font-medium text-white text-sm uppercase tracking-wider">Personas</h3>
        <button className="text-gray-400 hover:text-white transition-colors">
          <Plus size={16} />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {linkedPersonas.length === 0 ? (
          <div className="text-center p-4 text-xs text-gray-500">
            No personas linked to this journey.
          </div>
        ) : (
          linkedPersonas.map((p) => (
            <div key={p.id} className="flex items-center gap-3 p-2 rounded-lg bg-[var(--card)] border border-border group">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs text-white"
                style={{ backgroundColor: p.avatar_color || "#6366f1" }}
              >
                {p.name.substring(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{p.name}</p>
                <p className="text-xs text-gray-400 truncate">{p.role_title || "No Role"}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
