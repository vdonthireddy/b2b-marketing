"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Lead } from "@/types/lead";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Briefcase, ChevronLeft, ChevronRight, Search, DollarSign } from "lucide-react";

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const pageSize = 20;

  useEffect(() => {
    const fetchLeads = async () => {
      setIsLoading(true);
      try {
        const res = await api.get(`/api/leads?page=${page}&page_size=${pageSize}`);
        setLeads(res.data.items);
        setTotalPages(res.data.total_pages);
        setTotalItems(res.data.total);
      } catch (err) {
        console.error("Failed to fetch leads", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLeads();
  }, [page]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case "new":
        return "bg-blue-500/10 text-blue-400 border border-blue-500/20";
      case "contacted":
        return "bg-purple-500/10 text-purple-400 border border-purple-500/20";
      case "qualified":
        return "bg-green-500/10 text-green-400 border border-green-500/20";
      case "nurturing":
        return "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20";
      case "converted":
        return "bg-teal-500/10 text-teal-400 border border-teal-500/20";
      case "closed_lost":
        return "bg-red-500/10 text-red-400 border border-red-500/20";
      default:
        return "bg-gray-500/10 text-gray-400 border border-gray-500/20";
    }
  };

  const filteredLeads = leads.filter(
    (l) =>
      l.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-white flex items-center gap-2">
            <Briefcase className="text-primary h-8 w-8" /> Leads
          </h1>
          <p className="text-gray-400 mt-1">Track high-value prospects moving through journey stages.</p>
        </div>
      </div>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-500" />
        </div>
        <input
          type="text"
          placeholder="Search leads by name, email, or company..."
          className="block w-full pl-10 pr-3 py-2 border border-border rounded-md leading-5 bg-secondary text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-gray-400">Loading leads...</div>
      ) : filteredLeads.length === 0 ? (
        <Card className="p-12 text-center">
          <Briefcase className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white">No leads found</h3>
          <p className="text-gray-400 mt-2">
            {searchQuery ? "Try adjusting your search query." : "No leads exist in the database."}
          </p>
        </Card>
      ) : (
        <Card className="overflow-hidden border border-border">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-secondary-hover/50">
                <tr>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Lead Info
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Company / Title
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Journey Stage
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Deal Value
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {filteredLeads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-secondary-hover/20 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm font-semibold text-white">
                          {lead.first_name} {lead.last_name}
                        </span>
                        <span className="text-xs text-gray-500">{lead.email}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-300">{lead.company}</span>
                        <span className="text-xs text-gray-500">{lead.job_title || "N/A"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {lead.stage ? (
                        <div 
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border"
                          style={{
                            backgroundColor: `${lead.stage.color}15`,
                            color: lead.stage.color,
                            borderColor: `${lead.stage.color}30`
                          }}
                        >
                          <span>{lead.stage.icon}</span>
                          <span>{lead.stage.name}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-500">No Stage Linked</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm font-semibold text-white">
                        <DollarSign size={14} className="text-gray-500 mr-0.5" />
                        {formatCurrency(lead.value).replace("$", "")}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusBadgeClass(lead.status)}`}>
                        {lead.status.replace("_", " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="bg-secondary-hover/30 px-6 py-4 flex items-center justify-between border-t border-border">
              <div className="text-xs text-gray-500">
                Showing <span className="font-semibold text-white">{(page - 1) * pageSize + 1}</span> to{" "}
                <span className="font-semibold text-white">
                  {Math.min(page * pageSize, totalItems)}
                </span>{" "}
                of <span className="font-semibold text-white">{totalItems}</span> leads
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(p - 1, 1))}
                  disabled={page === 1}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft size={16} /> Prev
                </Button>
                <div className="text-xs text-gray-400 px-2">
                  Page <span className="text-white font-medium">{page}</span> of {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                  disabled={page === totalPages}
                  className="flex items-center gap-1"
                >
                  Next <ChevronRight size={16} />
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
