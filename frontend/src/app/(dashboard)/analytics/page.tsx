"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { CheckCircle, AlertCircle, Clock } from "lucide-react";

export default function AnalyticsPage() {
  const [completionData, setCompletionData] = useState<any[]>([]);
  const [activityData, setActivityData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [completionRes, activityRes] = await Promise.all([
          api.get("/api/analytics/journey-completion"),
          api.get("/api/analytics/activity?limit=10"),
        ]);
        setCompletionData(completionRes.data.journeys);
        setActivityData(activityRes.data.activities);
      } catch (error) {
        console.error("Failed to fetch analytics", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading) {
    return <div className="flex h-full items-center justify-center text-gray-400">Loading analytics...</div>;
  }

  // Calculate average completion
  const avgCompletion = completionData.length 
    ? Math.round(completionData.reduce((acc, curr) => acc + curr.completeness_pct, 0) / completionData.length)
    : 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-heading font-bold text-white">Analytics</h1>
        <p className="text-gray-400 mt-1">Measure the completeness and activity of your journey maps.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="text-green-400" size={20} />
            <h3 className="font-heading font-semibold text-lg text-white">Avg. Completion</h3>
          </div>
          <p className="text-4xl font-bold text-white">{avgCompletion}%</p>
          <p className="text-sm text-gray-400 mt-2">Across all journeys</p>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="text-orange-400" size={20} />
            <h3 className="font-heading font-semibold text-lg text-white">Empty Stages</h3>
          </div>
          <p className="text-4xl font-bold text-white">
            {completionData.reduce((acc, curr) => acc + (curr.total_stages - (curr.stages_with_goals || 0)), 0)}
          </p>
          <p className="text-sm text-gray-400 mt-2">Needs attention</p>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="text-blue-400" size={20} />
            <h3 className="font-heading font-semibold text-lg text-white">Recent Updates</h3>
          </div>
          <p className="text-4xl font-bold text-white">{activityData.length}</p>
          <p className="text-sm text-gray-400 mt-2">In the last 7 days</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="p-6 lg:col-span-2">
          <h3 className="font-heading font-semibold text-lg text-white mb-6">Journey Completeness</h3>
          <div className="h-80 w-full">
            {completionData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={completionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#233554" vertical={false} />
                  <XAxis 
                    dataKey="journey_name" 
                    stroke="#8892b0" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#8892b0" 
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip 
                    cursor={{ fill: '#112240' }}
                    contentStyle={{ backgroundColor: '#112240', borderColor: '#233554', color: '#fff' }}
                  />
                  <Bar dataKey="completeness_pct" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-gray-500">
                Not enough data to display chart.
              </div>
            )}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-heading font-semibold text-lg text-white mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {activityData.length > 0 ? (
              activityData.map((activity, idx) => (
                <div key={idx} className="flex gap-3 text-sm">
                  <div className="w-2 h-2 mt-1.5 rounded-full bg-primary flex-shrink-0"></div>
                  <div>
                    <p className="text-white">
                      <span className="font-medium text-gray-300">{activity.user_name}</span>{" "}
                      {activity.action} {activity.entity_type}
                    </p>
                    <p className="text-xs text-gray-500">{new Date(activity.created_at).toLocaleString()}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No recent activity.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
