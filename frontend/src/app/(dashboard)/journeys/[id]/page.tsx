"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Journey, Stage } from "@/types/journey";
import { JourneyCanvas } from "@/components/journey/JourneyCanvas";
import { DetailPanel } from "@/components/journey/DetailPanel";
import { PersonaWidget } from "@/components/persona/PersonaWidget";
import { ActiveUsers } from "@/components/collaboration/ActiveUsers";
import { ArrowLeft, Cloud, CloudUpload, Download, FileJson, FileText, FileSpreadsheet } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { debounce } from "lodash";

export default function JourneyBuilder() {
  const params = useParams();
  const router = useRouter();
  const journeyId = params.id as string;
  const token = useAuthStore((state) => state.accessToken);

  const [journey, setJourney] = useState<Journey | null>(null);
  const [selectedStageId, setSelectedStageId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("Goals");
  
  const [onlineUsers, setOnlineUsers] = useState<any[]>([]);
  const [saveState, setSaveState] = useState<"saved" | "saving">("saved");
  const [showExportMenu, setShowExportMenu] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load journey data
  useEffect(() => {
    const fetchJourney = async () => {
      try {
        const res = await api.get(`/api/journeys/${journeyId}`);
        setJourney(res.data);
      } catch (err) {
        console.error("Failed to load journey", err);
      }
    };
    fetchJourney();
  }, [journeyId]);

  // Setup WebSocket connection
  useEffect(() => {
    if (!token || !journeyId) return;

    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000").replace("http", "ws");
    const ws = new WebSocket(`${wsUrl}/ws/journey/${journeyId}?token=${token}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "user_joined" || data.type === "user_left") {
        setOnlineUsers(data.online_users || []);
      } else if (data.type === "stage_updated") {
        // Handle stage name updates from others
        setJourney((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            stages: prev.stages.map((s) => 
              s.id === data.stage_id ? { ...s, [data.field]: data.value } : s
            )
          };
        });
      }
      // TODO: Handle item_updated (goals, etc) for complete real-time sync
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, [journeyId, token]);

  const debouncedSaveName = useCallback(
    debounce(async (id: string, name: string) => {
      setSaveState("saving");
      try {
        await api.put(`/api/journeys/stages/${id}`, { name });
        setSaveState("saved");
      } catch (err) {
        console.error(err);
      }
    }, 500),
    []
  );

  const handleUpdateStageName = (id: string, name: string) => {
    // Optimistic UI update
    setJourney((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        stages: prev.stages.map((s) => (s.id === id ? { ...s, name } : s)),
      };
    });
    
    // Broadcast via WS
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "stage_update", stage_id: id, field: "name", value: name }));
    }

    // Save to DB
    debouncedSaveName(id, name);
  };

  const handleReorderStages = async (newStages: Stage[]) => {
    setJourney((prev) => prev ? { ...prev, stages: newStages } : prev);
    
    setSaveState("saving");
    try {
      await api.put(`/api/journeys/${journeyId}/stages/reorder`, {
        stage_ids: newStages.map(s => s.id)
      });
      setSaveState("saved");
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddStage = async () => {
    setSaveState("saving");
    try {
      const pos = journey?.stages.length || 0;
      const res = await api.post(`/api/journeys/${journeyId}/stages`, {
        name: "New Stage",
        position: pos,
      });
      const newStage = { ...res.data, goals: [], touchpoints: [], content: [] };
      setJourney((prev) => prev ? { ...prev, stages: [...prev.stages, newStage] } : prev);
      setSaveState("saved");
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddItem = async (stageId: string, type: string, text: string) => {
    try {
      const res = await api.post(`/api/journeys/stages/${stageId}/${type}`, { text });
      const newItem = res.data;
      
      setJourney((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          stages: prev.stages.map(s => {
            if (s.id === stageId) {
              const key = type === 'goal' ? 'goals' : type === 'touchpoint' ? 'touchpoints' : 'content';
              return { ...s, [key]: [...(s[key as keyof Stage] as any), newItem] };
            }
            return s;
          })
        };
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteItem = async (stageId: string, type: string, itemId: string) => {
    try {
      await api.delete(`/api/journeys/stages/items/${itemId}/${type}`);
      
      setJourney((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          stages: prev.stages.map(s => {
            if (s.id === stageId) {
              const key = type === 'goal' ? 'goals' : type === 'touchpoint' ? 'touchpoints' : 'content';
              return { ...s, [key]: (s[key as keyof Stage] as any).filter((i: any) => i.id !== itemId) };
            }
            return s;
          })
        };
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateItem = async (stageId: string, type: string, itemId: string, text: string) => {
    // Optimistic update
    setJourney((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        stages: prev.stages.map(s => {
          if (s.id === stageId) {
            const key = type === 'goal' ? 'goals' : type === 'touchpoint' ? 'touchpoints' : 'content';
            return {
              ...s, 
              [key]: (s[key as keyof Stage] as any).map((i: any) => i.id === itemId ? { ...i, text } : i)
            };
          }
          return s;
        })
      };
    });

    // Debounced API call would go here in production
  };

  const handleExport = async (format: "json" | "csv" | "pdf") => {
    try {
      const res = await api.get(`/api/export/${journeyId}/${format}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `journey-${journeyId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      setShowExportMenu(false);
    } catch (err) {
      console.error("Export failed", err);
    }
  };

  if (!journey) {
    return <div className="flex h-full items-center justify-center text-gray-400">Loading builder...</div>;
  }

  const selectedStage = selectedStageId ? journey.stages.find(s => s.id === selectedStageId) || null : null;

  return (
    <div className="flex flex-col h-full -m-8">
      {/* Top Toolbar */}
      <div className="h-14 bg-[var(--background)] border-b border-border flex items-center justify-between px-4 flex-shrink-0 z-10">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => router.push("/journeys")}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <input
            type="text"
            className="bg-transparent border border-transparent hover:border-border focus:border-primary focus:bg-secondary rounded px-2 py-1 text-lg font-heading font-semibold text-white outline-none w-64"
            value={journey.name}
            onChange={(e) => setJourney({...journey, name: e.target.value})}
            onBlur={() => api.put(`/api/journeys/${journeyId}`, { name: journey.name })}
          />
        </div>
        
        <div className="flex items-center gap-6">
          <ActiveUsers users={onlineUsers} />
          
          <div className="relative">
            <button 
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="flex items-center gap-2 text-sm text-gray-400 hover:text-white px-3 py-1.5 rounded-md hover:bg-secondary-hover transition-colors border border-border"
            >
              <Download size={16} /> Export
            </button>
            
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-secondary border border-border overflow-hidden z-50">
                <button 
                  onClick={() => handleExport("pdf")}
                  className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-primary/10 hover:text-white flex items-center gap-3 border-b border-border/50"
                >
                  <FileText size={16} className="text-red-400" /> Export as PDF
                </button>
                <button 
                  onClick={() => handleExport("csv")}
                  className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-primary/10 hover:text-white flex items-center gap-3 border-b border-border/50"
                >
                  <FileSpreadsheet size={16} className="text-green-400" /> Export as CSV
                </button>
                <button 
                  onClick={() => handleExport("json")}
                  className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-primary/10 hover:text-white flex items-center gap-3"
                >
                  <FileJson size={16} className="text-blue-400" /> Export as JSON
                </button>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-400">
            {saveState === "saving" ? (
              <><CloudUpload size={16} /> Saving...</>
            ) : (
              <><Cloud size={16} className="text-primary" /> Saved</>
            )}
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        <PersonaWidget 
          linkedPersonas={journey.personas as any} 
          allPersonas={[]} 
          onLinkPersona={() => {}} 
          onUnlinkPersona={() => {}} 
        />
        
        <div className="flex-1 flex flex-col relative overflow-hidden">
          <JourneyCanvas 
            stages={journey.stages}
            selectedStageId={selectedStageId}
            onSelectStage={setSelectedStageId}
            onReorderStages={handleReorderStages}
            onUpdateStageName={handleUpdateStageName}
            onAddStage={handleAddStage}
          />
          
          {selectedStage && (
            <DetailPanel
              stage={selectedStage}
              activeTab={activeTab}
              onTabChange={setActiveTab}
              onClose={() => setSelectedStageId(null)}
              onAddItem={handleAddItem}
              onDeleteItem={handleDeleteItem}
              onUpdateItem={handleUpdateItem}
            />
          )}
        </div>
      </div>
    </div>
  );
}
