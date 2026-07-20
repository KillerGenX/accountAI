"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Search, Loader2, CheckCircle2, XCircle, Globe, Building2 } from "lucide-react";

export default function DiscoveryPage() {
  const { fetchWithAuth, dbUser } = useAuth();
  const [criteria, setCriteria] = useState("");
  const [loading, setLoading] = useState(false);
  const [triggerStatus, setTriggerStatus] = useState<string | null>(null);
  const [prospects, setProspects] = useState<any[]>([]);
  const [fetching, setFetching] = useState(true);

  const fetchProspects = async () => {
    if (!dbUser?.workspace_id) return;
    try {
      const res = await fetchWithAuth(`http://localhost:8000/api/v1/discovery/prospects?workspace_id=${dbUser.workspace_id}`);
      if (res.ok) {
        setProspects(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    fetchProspects();
    const interval = setInterval(fetchProspects, 10000); // poll every 10s
    return () => clearInterval(interval);
  }, [dbUser]);

  const handleTrigger = async () => {
    if (!criteria.trim() || !dbUser?.workspace_id) return;
    setLoading(true);
    setTriggerStatus(null);
    try {
      const res = await fetchWithAuth("http://localhost:8000/api/v1/discovery/trigger", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: dbUser.workspace_id,
          criteria: criteria
        })
      });
      if (res.ok) {
        setTriggerStatus("Prospecting worker started! The AI is now searching the web. Please wait a few minutes.");
        setCriteria("");
      } else {
        setTriggerStatus("Failed to trigger worker.");
      }
    } catch (err) {
      setTriggerStatus("Error triggering worker.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: string, action: "approve" | "reject") => {
    try {
      const res = await fetchWithAuth(`http://localhost:8000/api/v1/discovery/prospects/${id}/${action}`, {
        method: "POST",
        body: JSON.stringify({ workspace_id: dbUser?.workspace_id })
      });
      if (res.ok) {
        fetchProspects();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
          <Globe className="text-blue-600" /> Account Discovery & Prospecting
        </h1>
        <p className="text-slate-500 mt-2">
          Instruct the AI to search the internet for new high-potential companies matching your criteria.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Define Search Criteria</h2>
        <div className="flex gap-4">
          <input
            type="text"
            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. Perusahaan logistik di Indonesia yang baru melakukan ekspansi"
            value={criteria}
            onChange={(e) => setCriteria(e.target.value)}
          />
          <button
            onClick={handleTrigger}
            disabled={loading || !criteria.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Search className="w-5 h-5" />}
            Start Prospecting
          </button>
        </div>
        {triggerStatus && (
          <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 text-sm">
            {triggerStatus}
          </div>
        )}
      </div>

      <div className="mb-6 flex justify-between items-end">
        <h2 className="text-xl font-bold text-slate-800">Discovered Prospects</h2>
        <span className="text-sm text-slate-500">{prospects.length} pending review</span>
      </div>

      {fetching ? (
        <div className="flex justify-center p-12">
          <Loader2 className="animate-spin text-slate-400 w-8 h-8" />
        </div>
      ) : prospects.length === 0 ? (
        <div className="bg-slate-50 border border-dashed border-slate-300 rounded-xl p-12 text-center">
          <Globe className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-600 font-medium">No pending prospects</h3>
          <p className="text-slate-400 text-sm mt-1">Trigger a new search above to discover accounts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {prospects.map((p) => (
            <div key={p.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col hover:border-blue-300 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg">
                    <Building2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-800">{p.company_name}</h3>
                    <a href={p.source_url} target="_blank" rel="noreferrer" className="text-xs text-blue-500 hover:underline">
                      View Source
                    </a>
                  </div>
                </div>
              </div>
              
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-3">{p.description}</p>
                <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-lg">
                  <p className="text-xs font-semibold text-emerald-800 mb-1">Why it matches:</p>
                  <p className="text-sm text-emerald-700 leading-relaxed">{p.match_reason}</p>
                </div>
              </div>

              <div className="mt-6 flex gap-3 pt-4 border-t border-slate-100">
                <button
                  onClick={() => handleAction(p.id, "approve")}
                  className="flex-1 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-700 font-medium rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <CheckCircle2 className="w-4 h-4" /> Approve as Account
                </button>
                <button
                  onClick={() => handleAction(p.id, "reject")}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 font-medium rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <XCircle className="w-4 h-4" /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
