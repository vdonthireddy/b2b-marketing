"use client";

import { useEffect, useState } from "react";
import { usePersonaStore, Persona } from "@/stores/personaStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Users, Plus, Search } from "lucide-react";
import { api } from "@/lib/api";

export default function PersonasPage() {
  const { personas, fetchPersonas, createPersona, isLoading } = usePersonaStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  
  const [newPersona, setNewPersona] = useState({
    name: "",
    role_title: "",
    company_size: "",
    goals: "",
    pain_points: "",
    motivations: "",
    avatar_color: "#6366f1",
  });
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  
  const colors = ["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#10b981", "#06b6d4", "#3b82f6", "#6366f1", "#8b5cf6", "#d946ef"];

  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setCreateError("");
    
    try {
      await createPersona(newPersona);
      setIsModalOpen(false);
      setNewPersona({
        name: "", role_title: "", company_size: "",
        goals: "", pain_points: "", motivations: "", avatar_color: "#6366f1"
      });
    } catch (err: any) {
      setCreateError(err.message);
    } finally {
      setIsCreating(false);
    }
  };
  
  const handleAiSuggest = async () => {
    setIsCreating(true);
    try {
      const res = await api.post("/api/ai/suggest/persona", { industry: "SaaS", role: newPersona.role_title || "Decision Maker" });
      const data = res.data.suggestion;
      // Depending on AI response structure, fill the fields
      if (typeof data === "string") {
         // Simple fallback if AI just returns text
         setNewPersona(prev => ({...prev, pain_points: data}));
      } else {
         setNewPersona(prev => ({
           ...prev,
           name: data.name || prev.name,
           goals: data.goals?.join("\n") || prev.goals,
           pain_points: data.pain_points?.join("\n") || prev.pain_points,
           motivations: data.motivations?.join("\n") || prev.motivations,
         }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsCreating(false);
    }
  };

  const filteredPersonas = personas.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (p.role_title && p.role_title.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white">Personas</h1>
          <p className="text-gray-400 mt-1">Manage target audience segments for your journeys.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
          <Plus size={18} /> New Persona
        </Button>
      </div>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-500" />
        </div>
        <input
          type="text"
          placeholder="Search personas..."
          className="block w-full pl-10 pr-3 py-2 border border-border rounded-md leading-5 bg-secondary text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-gray-400">Loading personas...</div>
      ) : filteredPersonas.length === 0 ? (
        <Card className="p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white">No personas found</h3>
          <p className="text-gray-400 mt-2 mb-6">
            {searchQuery ? "Try adjusting your search query." : "Create your first buyer persona to get started."}
          </p>
          {!searchQuery && (
            <Button onClick={() => setIsModalOpen(true)}>Create Persona</Button>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredPersonas.map((persona) => (
            <Card key={persona.id} className="p-6 hover:border-primary transition-colors h-full flex flex-col relative overflow-hidden">
               <div 
                  className="absolute top-0 left-0 right-0 h-1" 
                  style={{ backgroundColor: persona.avatar_color }}
               />
              <div className="flex items-start gap-4 mb-4 mt-2">
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg text-white"
                  style={{ backgroundColor: persona.avatar_color }}
                >
                  {persona.name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-heading font-semibold text-xl text-white">{persona.name}</h3>
                  <p className="text-sm text-gray-400">{persona.role_title}</p>
                </div>
              </div>
              
              <div className="space-y-4 flex-1 mt-4 text-sm text-gray-300">
                {persona.goals && (
                  <div>
                    <strong className="text-white block mb-1 text-xs uppercase tracking-wider">Key Goals</strong>
                    <p className="line-clamp-2">{persona.goals}</p>
                  </div>
                )}
                {persona.pain_points && (
                  <div>
                    <strong className="text-white block mb-1 text-xs uppercase tracking-wider">Pain Points</strong>
                    <p className="line-clamp-2">{persona.pain_points}</p>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={() => !isCreating && setIsModalOpen(false)} title="Create New Persona">
        <form onSubmit={handleCreate} className="space-y-4">
          {createError && (
            <div className="text-sm text-red-500 bg-red-500/10 p-3 rounded border border-red-500/20">
              {createError}
            </div>
          )}
          
          <div className="flex justify-between items-center pb-2">
            <span className="text-sm text-gray-400">Want some inspiration?</span>
            <Button type="button" variant="outline" size="sm" onClick={handleAiSuggest} isLoading={isCreating}>
              AI Generate Content
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              id="personaName"
              label="Persona Name"
              placeholder="e.g. Enterprise Emma"
              value={newPersona.name}
              onChange={(e) => setNewPersona({...newPersona, name: e.target.value})}
              required
            />
            <Input
              id="roleTitle"
              label="Role / Job Title"
              placeholder="e.g. VP of Marketing"
              value={newPersona.role_title}
              onChange={(e) => setNewPersona({...newPersona, role_title: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Avatar Color</label>
            <div className="flex gap-2 flex-wrap">
              {colors.map(c => (
                <button
                  key={c}
                  type="button"
                  className={`w-6 h-6 rounded-full transition-transform ${newPersona.avatar_color === c ? 'scale-125 ring-2 ring-white ring-offset-2 ring-offset-secondary' : 'hover:scale-110'}`}
                  style={{ backgroundColor: c }}
                  onClick={() => setNewPersona({...newPersona, avatar_color: c})}
                />
              ))}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Goals</label>
            <textarea
              className="flex w-full rounded-md border border-border bg-secondary/50 px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              rows={2}
              value={newPersona.goals}
              onChange={(e) => setNewPersona({...newPersona, goals: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Pain Points</label>
            <textarea
              className="flex w-full rounded-md border border-border bg-secondary/50 px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              rows={2}
              value={newPersona.pain_points}
              onChange={(e) => setNewPersona({...newPersona, pain_points: e.target.value})}
            />
          </div>
          
          <div className="pt-4 flex justify-end gap-3 border-t border-border mt-6">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)} disabled={isCreating}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isCreating}>
              Save Persona
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
