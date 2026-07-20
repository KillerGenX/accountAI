"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "../../context/AuthContext";
import { 
  Building2, 
  Plus, 
  X, 
  Loader2, 
  MapPin, 
  Layers, 
  Globe, 
  AlertCircle 
} from "lucide-react";

interface Account {
  id: string;
  company_name: string;
  company_url: string;
  industry: string;
  sub_industry: string;
  headquarters: string;
  completeness_score: number;
  status: string;
}

const DEFAULT_WORKSPACE_ID = "348ea7c6-11f3-4589-9518-e567c0958b7f";
const DEFAULT_USER_ID = "5651b60c-a77f-4037-a190-f9e9a7c6eb02";

export default function AccountsPage() {
  const { fetchWithAuth, dbUser, user } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [companyName, setCompanyName] = useState("");
  const [companyUrl, setCompanyUrl] = useState("");
  const [industry, setIndustry] = useState("");
  const [subIndustry, setSubIndustry] = useState("");
  const [headquarters, setHeadquarters] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function fetchAccounts() {
    try {
      setLoading(true);
      const res = await fetchWithAuth(`/api/v1/accounts/`);
      if (!res.ok) throw new Error("Could not fetch accounts from API server.");
      const data = await res.json();
      setAccounts(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load accounts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAccounts();
  }, [dbUser?.workspace_id]);

  async function handleAddAccount(e: React.FormEvent) {
    e.preventDefault();
    if (!companyName.trim()) return;

    try {
      setSubmitting(true);
      const body = {
        workspace_id: dbUser?.workspace_id || DEFAULT_WORKSPACE_ID,
        company_name: companyName,
        company_url: companyUrl || null,
        industry: industry || null,
        sub_industry: subIndustry || null,
        company_size: "Enterprise",
        headquarters: headquarters || null,
        assigned_to: dbUser?.id || user?.id || DEFAULT_USER_ID
      };

      const res = await fetchWithAuth("/api/v1/accounts/", {
        method: "POST",
        body: JSON.stringify(body)
      });

      if (!res.ok) throw new Error("Failed to register corporate account.");

      // Reset form and reload
      setCompanyName("");
      setCompanyUrl("");
      setIndustry("");
      setSubIndustry("");
      setHeadquarters("");
      setShowAddForm(false);
      
      // Reload accounts. Give it a tiny delay so the background worker has finished updating the db summary!
      setTimeout(fetchAccounts, 1000);
    } catch (err: any) {
      alert(err.message || "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Corporate Accounts</h1>
          <p className="text-xs text-slate-500">Manage target companies and view AI enriched intelligence profiles.</p>
        </div>
        
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-4 py-2.5 rounded-lg shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Add Account Modal Overlay */}
      {showAddForm && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-slate-200 rounded-xl shadow-lg w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                Add New Corporate Account
              </h2>
              <button 
                onClick={() => setShowAddForm(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleAddAccount} className="p-6 space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Telkom Indonesia"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Website URL
                </label>
                <input
                  type="url"
                  placeholder="e.g. https://telkom.co.id"
                  value={companyUrl}
                  onChange={(e) => setCompanyUrl(e.target.value)}
                  className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                    Industry
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Telecommunications"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                    Sub-Industry
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Mobile Carrier"
                    value={subIndustry}
                    onChange={(e) => setSubIndustry(e.target.value)}
                    className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Headquarters Location
                </label>
                <input
                  type="text"
                  placeholder="e.g. Jakarta, Indonesia"
                  value={headquarters}
                  onChange={(e) => setHeadquarters(e.target.value)}
                  className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                />
              </div>

              <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 font-semibold shadow-sm transition-colors flex items-center gap-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                    </>
                  ) : (
                    "Save Account"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Main Grid Accounts Display */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-2">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          <span className="text-sm font-semibold text-slate-500">Syncing database entries...</span>
        </div>
      ) : accounts.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-blue-100">
            <Building2 className="w-8 h-8" />
          </div>
          <h3 className="font-bold text-slate-800 text-lg mb-1">No Accounts Registered</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto mb-6">
            Register your target enterprise companies so our AI worker can begin researching them immediately.
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-4 py-2.5 rounded-lg shadow-sm transition-colors"
          >
            Add First Account
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((acc) => (
            <div 
              key={acc.id}
              className="bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md hover:border-slate-300 p-6 flex flex-col justify-between gap-6 transition-all duration-200"
            >
              {/* Account Header */}
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-500 font-mono text-sm shrink-0">
                    {acc.company_name.slice(0, 2).toUpperCase()}
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                    {acc.status}
                  </span>
                </div>
                
                <div className="space-y-1">
                  <Link 
                    href={`/accounts/${acc.id}`}
                    className="font-bold text-slate-800 hover:text-blue-600 text-base leading-tight block"
                  >
                    {acc.company_name}
                  </Link>
                  
                  {acc.company_url && (
                    <a 
                      href={acc.company_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-slate-400 hover:underline flex items-center gap-1"
                    >
                      <Globe className="w-3.5 h-3.5 text-slate-400" />
                      <span>{acc.company_url.replace("https://", "").replace("http://", "")}</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Account Details Block */}
              <div className="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-4">
                <div className="flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-slate-400" />
                  <span>{acc.industry || "General Industry"}</span>
                </div>
                {acc.headquarters && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{acc.headquarters}</span>
                  </div>
                )}
              </div>

              {/* Progress Completeness */}
              <div className="space-y-1 border-t border-slate-100 pt-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium">Completeness score</span>
                  <span className="font-semibold text-slate-700">{acc.completeness_score}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 rounded-full" 
                    style={{ width: `${acc.completeness_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-2">
                <Link
                  href={`/accounts/${acc.id}`}
                  className="w-full flex items-center justify-center gap-2 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs py-2 rounded-lg transition-colors"
                >
                  View Profile
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
