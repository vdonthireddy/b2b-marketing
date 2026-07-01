import { create } from "zustand";
import { PersonaBasic } from "@/types/journey";
import { api } from "@/lib/api";

export interface Persona extends PersonaBasic {
  team_id: string;
  company_size?: string;
  goals?: string;
  pain_points?: string;
  motivations?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface PersonaState {
  personas: Persona[];
  isLoading: boolean;
  error: string | null;
  fetchPersonas: () => Promise<void>;
  createPersona: (data: Partial<Persona>) => Promise<Persona>;
}

export const usePersonaStore = create<PersonaState>((set) => ({
  personas: [],
  isLoading: false,
  error: null,
  fetchPersonas: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await api.get("/api/personas");
      set({ personas: res.data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },
  createPersona: async (data: Partial<Persona>) => {
    try {
      const res = await api.post("/api/personas", data);
      set((state) => ({ personas: [res.data, ...state.personas] }));
      return res.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || "Failed to create persona");
    }
  },
}));
