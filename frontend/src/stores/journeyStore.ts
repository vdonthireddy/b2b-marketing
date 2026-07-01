import { create } from "zustand";
import { Journey } from "@/types/journey";
import { api } from "@/lib/api";

interface JourneyState {
  journeys: Journey[];
  isLoading: boolean;
  error: string | null;
  fetchJourneys: () => Promise<void>;
  createJourney: (name: string, description?: string) => Promise<Journey>;
}

export const useJourneyStore = create<JourneyState>((set) => ({
  journeys: [],
  isLoading: false,
  error: null,
  fetchJourneys: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await api.get("/api/journeys");
      set({ journeys: res.data.items, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },
  createJourney: async (name: string, description?: string) => {
    try {
      const res = await api.post("/api/journeys", { name, description });
      set((state) => ({ journeys: [res.data, ...state.journeys] }));
      return res.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || "Failed to create journey");
    }
  },
}));
