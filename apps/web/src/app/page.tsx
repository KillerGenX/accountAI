"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";
import { 
  Building2, 
  Percent, 
  Bot, 
  Plus, 
  ArrowUpRight, 
  TrendingUp, 
  Loader2 
} from "lucide-react";

interface Account {
  id: string;
  company_name: string;
  industry: string;
  completeness_score: number;
  status: string;
}

interface Workspace {
  id: string;
  name: string;
  company_name: string;
  industry: string;
}

interface NewsSignal {
  id: string;
  headline: string;
  summary: string | null;
  status: "pending" | "approved" | "rejected";
  created_at: string;
}

const DEFAULT_WORKSPACE_ID = "348ea7c6-11f3-4589-9518-e567c0958b7f";

export default function Dashboard() {
  const { fetchWithAuth, dbUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [pendingSignals, setPendingSignals] = useState<NewsSignal[]>([]);
  const [error, setError] = useState<string | null>(null);

  const activeWorkspaceId = dbUser?.workspace_id || DEFAULT_WORKSPACE_ID;

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // 1. Fetch Workspace Profile
        const wsRes = await fetchWithAuth(`/api/v1/workspaces/${activeWorkspaceId}`);
        if (!wsRes.ok) throw new Error("API Server is offline or default workspace has not been created.");
        const wsData = await wsRes.json();
        setWorkspace(wsData);

        // 2. Fetch Accounts
        const accRes = await fetchWithAuth(`/api/v1/accounts/`);
        if (accRes.ok) {
          const accData = await accRes.json();
          setAccounts(accData);
        }

        // 3. Fetch Pending Signals
        const newsRes = await fetchWithAuth(`/api/v1/news/`);
        if (newsRes.ok) {
          const newsData = await newsRes.json();
          const pending = newsData.filter((s: NewsSignal) => s.status === "pending");
          setPendingSignals(pending);
        }
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to connect to API Gateway");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [activeWorkspaceId]);

  // Compute aggregated stats
  const totalAccounts = accounts.length;
  const avgCompleteness = totalAccounts > 0 
    ? Math.round(accounts.reduce((sum, acc) => sum + acc.completeness_score, 0) / totalAccounts)
    : 0;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <span className="text-sm font-medium text-slate-500">Loading your brief...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-xl mx-auto mt-12 text-center">
        <h2 className="text-red-800 font-bold text-lg mb-2">Platform Connection Offline</h2>
        <p className="text-red-600 text-sm mb-6">{error}</p>
        <div className="text-xs text-slate-500 leading-relaxed bg-white/60 p-4 rounded-lg border border-red-100 text-left space-y-1">
          <p className="font-semibold text-slate-700">How to fix this:</p>
          <p>1. Make sure the FastAPI API Gateway is running on port 8000.</p>
          <p>2. Verify if you have seeded the database or registered a workspace with ID: <code className="bg-slate-100 px-1 rounded font-mono select-all">{DEFAULT_WORKSPACE_ID}</code></p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Morning Brief Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Good morning, {dbUser?.full_name ? dbUser.full_name.split(' ')[0] : 'User'}!
          </h1>
          <p className="text-sm text-slate-500 max-w-xl leading-relaxed">
            Here is your account intelligence overview for the <span className="font-semibold text-slate-700">{workspace?.name || "Workspace"}</span> workspace. Digital Employees are active and listening to event signals.
          </p>
        </div>
        
        <Link 
          href="/accounts" 
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-4 py-2.5 rounded-lg shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Accounts Metric */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex items-center justify-between">
          <div className="space-y-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Managed Accounts
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-800">{totalAccounts}</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
            <Building2 className="w-6 h-6" />
          </div>
        </div>

        {/* Avg Completeness Metric */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex items-center justify-between">
          <div className="space-y-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Avg Completeness
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-800">{avgCompleteness}%</span>
              <span className="text-xs text-slate-400">Target &gt;80%</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
            <Percent className="w-5 h-5" />
          </div>
        </div>

        {/* Active AI Agents Metric */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex items-center justify-between">
          <div className="space-y-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              AI Employees Active
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-800">3</span>
              <span className="text-xs text-slate-400">Digital Workforce</span>
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <Bot className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Accounts & Workforce Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Accounts Panel */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm lg:col-span-2">
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
              Recent Enterprise Accounts
            </h2>
            <Link 
              href="/accounts" 
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-0.5"
            >
              View All <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          
          <div className="divide-y divide-slate-100">
            {accounts.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">
                No accounts registered yet. Click &quot;Add Account&quot; to begin.
              </div>
            ) : (
              accounts.slice(0, 5).map((acc) => (
                <div key={acc.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="space-y-1">
                    <Link 
                      href={`/accounts/${acc.id}`} 
                      className="font-semibold text-sm text-slate-800 hover:text-blue-600 block"
                    >
                      {acc.company_name}
                    </Link>
                    <span className="text-xs text-slate-400">{acc.industry || "General Industry"}</span>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {/* Completeness bar */}
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-xs font-semibold text-slate-600">
                        {acc.completeness_score}% Complete
                      </span>
                      <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-600 rounded-full" 
                          style={{ width: `${acc.completeness_score}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pending Signals Active Directory */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
              Pending Signals Awaiting Review
            </h2>
            <span className="text-xs font-bold text-white bg-red-500 px-2 py-0.5 rounded-full">
              {pendingSignals.length}
            </span>
          </div>
          <div className="p-6 space-y-4">
            {pendingSignals.length === 0 ? (
              <div className="text-center text-slate-400 text-xs py-4">
                All caught up! No pending signals to review.
              </div>
            ) : (
              pendingSignals.slice(0, 3).map(sig => (
                <div key={sig.id} className="flex items-start gap-3 p-3 bg-slate-50 border border-slate-100 rounded-lg hover:border-slate-200 transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-red-50 border border-red-100 text-red-600 flex items-center justify-center text-xs font-bold">
                    !
                  </div>
                  <div className="flex-1 space-y-1">
                    <p className="text-xs font-bold text-slate-700 line-clamp-1" title={sig.headline}>{sig.headline}</p>
                    <p className="text-[10px] text-slate-400">
                      {new Date(sig.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link href="/monitoring" className="text-[9px] font-bold text-blue-700 bg-blue-100 hover:bg-blue-200 px-2 py-1 rounded transition-colors whitespace-nowrap">
                    Review
                  </Link>
                </div>
              ))
            )}
            {pendingSignals.length > 3 && (
              <Link href="/monitoring" className="block text-center text-xs font-semibold text-blue-600 hover:text-blue-700 pt-2">
                View {pendingSignals.length - 3} more...
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
