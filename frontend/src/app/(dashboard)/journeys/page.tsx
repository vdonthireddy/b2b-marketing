"use client";

import { useEffect, useState } from "react";
import { useJourneyStore } from "@/stores/journeyStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Route, Plus, Search } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AgentModal } from "@/components/journey/AgentModal";

export default function JourneysList() {
  const router = useRouter();
  const { journeys, fetchJourneys, createJourney, isLoading } = useJourneyStore();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  
  const [newJourneyName, setNewJourneyName] = useState("");
  const [newJourneyDesc, setNewJourneyDesc] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState("");

  useEffect(() => {
    fetchJourneys();
  }, [fetchJourneys]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setCreateError("");
    
    try {
      const journey = await createJourney(newJourneyName, newJourneyDesc);
      setIsModalOpen(false);
      setNewJourneyName("");
      setNewJourneyDesc("");
      router.push(`/journeys/${journey.id}`);
    } catch (err: any) {
      setCreateError(err.message);
    } finally {
      setIsCreating(false);
    }
  };

  const filteredJourneys = journeys.filter(j => 
    j.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (j.description && j.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white">Journeys</h1>
          <p className="text-gray-400 mt-1">Manage your customer journey maps.</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setIsAgentModalOpen(true)} variant="outline" className="border-primary text-primary hover:bg-primary/10 flex items-center gap-2">
            ✨ Generate with AI
          </Button>
          <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
            <Plus size={18} /> New Journey
          </Button>
        </div>
      </div>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-500" />
        </div>
        <input
          type="text"
          placeholder="Search journeys..."
          className="block w-full pl-10 pr-3 py-2 border border-border rounded-md leading-5 bg-secondary text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-gray-400">Loading journeys...</div>
      ) : filteredJourneys.length === 0 ? (
        <Card className="p-12 text-center">
          <Route className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white">No journeys found</h3>
          <p className="text-gray-400 mt-2 mb-6">
            {searchQuery ? "Try adjusting your search query." : "Create your first customer journey map to get started."}
          </p>
          {!searchQuery && (
            <Button onClick={() => setIsModalOpen(true)}>Create Journey</Button>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredJourneys.map((journey) => (
            <Link key={journey.id} href={`/journeys/${journey.id}`}>
              <Card className="p-6 hover:border-primary transition-colors cursor-pointer h-full flex flex-col group relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-accent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-heading font-semibold text-xl text-white group-hover:text-primary transition-colors">{journey.name}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${journey.status === 'active' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'}`}>
                    {journey.status}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-6 flex-1 line-clamp-2">
                  {journey.description || "No description provided."}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500 mt-auto pt-4 border-t border-border">
                  <div className="flex gap-4">
                    <span>{journey.stage_count || 8} Stages</span>
                    <span>{journey.persona_count || 0} Personas</span>
                  </div>
                  <span>{new Date(journey.updated_at).toLocaleDateString()}</span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={() => !isCreating && setIsModalOpen(false)} title="Create New Journey">
        <form onSubmit={handleCreate} className="space-y-4">
          {createError && (
            <div className="text-sm text-red-500 bg-red-500/10 p-3 rounded border border-red-500/20">
              {createError}
            </div>
          )}
          
          <Input
            id="journeyName"
            label="Journey Name"
            placeholder="e.g. Enterprise Onboarding"
            value={newJourneyName}
            onChange={(e) => setNewJourneyName(e.target.value)}
            required
            autoFocus
          />
          
          <div>
            <label htmlFor="journeyDesc" className="block text-sm font-medium text-foreground mb-1">
              Description (Optional)
            </label>
            <textarea
              id="journeyDesc"
              className="flex w-full rounded-md border border-border bg-secondary/50 px-3 py-2 text-sm text-foreground ring-offset-[var(--background)] placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              rows={3}
              placeholder="What is the goal of this journey?"
              value={newJourneyDesc}
              onChange={(e) => setNewJourneyDesc(e.target.value)}
            />
          </div>
          
          <div className="pt-4 flex justify-end gap-3">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)} disabled={isCreating}>
              Cancel
            </Button>
            <Button type="submit" isLoading={isCreating}>
              Create Journey
            </Button>
          </div>
        </form>
      </Modal>
      <AgentModal isOpen={isAgentModalOpen} onClose={() => setIsAgentModalOpen(false)} />
    </div>
  );
}
