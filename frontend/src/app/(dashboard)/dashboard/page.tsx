"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Route, Users, BarChart3, Activity } from "lucide-react";
import Link from "next/link";
import { useJourneyStore } from "@/stores/journeyStore";

export default function Dashboard() {
  const { journeys, fetchJourneys, isLoading: isJourneysLoading } = useJourneyStore();
  const [stats, setStats] = useState({
    journey_count: 0,
    persona_count: 0,
    member_count: 0,
    stage_count: 0,
    recent_activity_count: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get("/api/analytics/dashboard");
        setStats(res.data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
    fetchJourneys();
  }, [fetchJourneys]);

  if (isLoading) {
    return <div className="flex h-full items-center justify-center">Loading dashboard...</div>;
  }

  const statCards = [
    { title: "Total Journeys", value: stats.journey_count, icon: Route, color: "text-primary" },
    { title: "Personas", value: stats.persona_count, icon: Users, color: "text-accent" },
    { title: "Team Members", value: stats.member_count, icon: Users, color: "text-blue-400" },
    { title: "Recent Activity", value: stats.recent_activity_count, icon: Activity, color: "text-orange-400" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Overview of your team's journey mapping activity.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">{stat.title}</p>
                <h3 className="text-3xl font-heading font-bold text-white mt-2">{stat.value}</h3>
              </div>
              <div className={`p-3 rounded-full bg-secondary-hover ${stat.color}`}>
                <Icon size={24} />
              </div>
            </Card>
          );
        })}
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-heading font-bold text-white">Recent Journeys</h2>
          <Link href="/journeys" className="text-sm text-primary hover:text-primary-hover">
            View all
          </Link>
        </div>
        
        {isJourneysLoading ? (
          <div>Loading journeys...</div>
        ) : journeys.length === 0 ? (
          <Card className="p-12 text-center">
            <Route className="mx-auto h-12 w-12 text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-white">No journeys yet</h3>
            <p className="text-gray-400 mt-2 mb-6">Create your first customer journey map to get started.</p>
            <Link href="/journeys" className="inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-[var(--background)] bg-primary text-secondary hover:bg-primary-hover h-10 px-4 py-2 text-sm">
              Create Journey
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {journeys.slice(0, 3).map((journey) => (
              <Link key={journey.id} href={`/journeys/${journey.id}`}>
                <Card className="p-6 hover:border-primary transition-colors cursor-pointer h-full flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-heading font-semibold text-lg text-white">{journey.name}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${journey.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-gray-500/10 text-gray-400'}`}>
                      {journey.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-6 flex-1 line-clamp-2">
                    {journey.description || "No description provided."}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500 mt-auto pt-4 border-t border-border">
                    <span>{new Date(journey.updated_at).toLocaleDateString()}</span>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
