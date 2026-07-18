"use client";

import { useEffect, useState } from "react";
import {
  Cpu,
  Inbox,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Clock,
  Sparkles,
  Radio,
  Check,
  X,
  Loader2,
  Building2,
  ArrowRight,
  AlertCircle
} from "lucide-react";

interface NewsSignal {
  id: string;
  workspace_id: string;
  account_id: string;
  headline: string;
  summary: string | null;
  source_url: string | null;
  published_at: string | null;
  signal_type: string | null;
  status: "pending" | "approved" | "rejected";
  created_at: string;
}

interface Toast {
  id: string;
  message: string;
  type: "success" | "error";
}

export default function WorkforceConsolePage() {
  const [signals, setSignals] = useState<NewsSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"pending" | "approved" | "rejected">("pending");
  const [triggeringScraper, setTriggeringScraper] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Action pending IDs to show loading spinner per-card
  const [actioningId, setActioningId] = useState<string | null>(null);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/api/v1/news/", {
        headers: { Authorization: "Bearer mock-token-teguh" }
      });
      if (!res.ok) throw new Error("Could not load corporate AI discoveries.");
      const data = await res.json();
      setSignals(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to sync digital discoveries.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  const addToast = (message: string, type: "success" | "error" = "success") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleUpdateStatus = async (id: string, newStatus: "approved" | "rejected") => {
    try {
      setActioningId(id);
      const res = await fetch(`http://localhost:8000/api/v1/news/${id}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer mock-token-teguh"
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!res.ok) throw new Error("Failed to register decision in backend.");

      const updatedSignal = await res.json();

      // UI Micro-Animation: Fade and update
      setSignals((prev) =>
        prev.map((sig) => (sig.id === id ? { ...sig, status: newStatus } : sig))
      );

      addToast(
        newStatus === "approved"
          ? "Corporate intelligence approved & stored to episodic memory."
          : "Signal rejected & muted.",
        "success"
      );
    } catch (err: any) {
      addToast(err.message || "Could not save verification decision.", "error");
    } finally {
      setActioningId(null);
    }
  };

  const handleTriggerScraper = async () => {
    try {
      setTriggeringScraper(true);
      const res = await fetch("http://localhost:8000/api/v1/monitoring/trigger", {
        method: "POST",
        headers: { Authorization: "Bearer mock-token-teguh" }
      });

      if (!res.ok) throw new Error("Failed to trigger NATS scrapers.");

      addToast("NATS Event Broadcasted! Scraper worker is actively running.", "success");
      
      // Delay fetching to let workers process first batches
      setTimeout(fetchSignals, 3000);
    } catch (err: any) {
      addToast(err.message || "Failed to trigger on-demand scraping.", "error");
    } finally {
      setTriggeringScraper(false);
    }
  };

  // Group signals by status for badges and listings
  const grouped = {
    pending: signals.filter((s) => s.status === "pending"),
    approved: signals.filter((s) => s.status === "approved"),
    rejected: signals.filter((s) => s.status === "rejected")
  };

  const currentTabSignals = grouped[activeTab];

  // Map category to aesthetic CSS badges
  const getCategoryStyles = (category: string | null) => {
    const cat = (category || "general").toLowerCase();
    if (cat.includes("expansion") || cat.includes("growth")) {
      return "bg-purple-100 text-purple-700 border-purple-200";
    }
    if (cat.includes("leadership") || cat.includes("people") || cat.includes("hire")) {
      return "bg-blue-100 text-blue-700 border-blue-200";
    }
    if (cat.includes("funding") || cat.includes("financial") || cat.includes("investment")) {
      return "bg-emerald-100 text-emerald-700 border-emerald-200";
    }
    if (cat.includes("tech") || cat.includes("vendor") || cat.includes("product")) {
      return "bg-amber-100 text-amber-700 border-amber-200";
    }
    return "bg-slate-100 text-slate-700 border-slate-200";
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Area */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-200 pb-5 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Digital Workforce Console
            </h1>
            <span className="flex items-center gap-1 bg-blue-50 text-blue-600 border border-blue-100 font-bold px-2 py-0.5 rounded text-[10px] uppercase">
              <Radio className="w-3 h-3 animate-pulse" /> Active Agent
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Verify automated corporate trigger discoveries. Approved intelligence increments account completeness.
          </p>
        </div>

        <button
          onClick={handleTriggerScraper}
          disabled={triggeringScraper}
          className="flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-700 text-white font-semibold text-xs px-4 py-2.5 rounded-lg shadow-sm transition-colors shrink-0"
        >
          {triggeringScraper ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Scraping Web...
            </>
          ) : (
            <>
              <Cpu className="w-4 h-4" />
              Run Daily Scraper Now
            </>
          )}
        </button>
      </div>

      {/* Error state alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Inbox Tabs Bar */}
      <div className="flex border-b border-slate-200 gap-1 bg-slate-100/50 p-1 rounded-xl">
        <button
          onClick={() => setActiveTab("pending")}
          className={`flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold tracking-wide transition-all ${
            activeTab === "pending"
              ? "bg-white text-blue-600 shadow-xs font-extrabold border border-slate-200/50"
              : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
          }`}
        >
          <Inbox className="w-4 h-4" />
          <span>Pending Review</span>
          <span
            className={`font-semibold px-2 py-0.5 rounded-full text-[10px] ${
              activeTab === "pending"
                ? "bg-blue-100 text-blue-600"
                : "bg-slate-200 text-slate-600"
            }`}
          >
            {grouped.pending.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("approved")}
          className={`flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold tracking-wide transition-all ${
            activeTab === "approved"
              ? "bg-white text-emerald-600 shadow-xs font-extrabold border border-slate-200/50"
              : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Approved</span>
          <span
            className={`font-semibold px-2 py-0.5 rounded-full text-[10px] ${
              activeTab === "approved"
                ? "bg-emerald-100 text-emerald-600"
                : "bg-slate-200 text-slate-600"
            }`}
          >
            {grouped.approved.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("rejected")}
          className={`flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-bold tracking-wide transition-all ${
            activeTab === "rejected"
              ? "bg-white text-red-600 shadow-xs font-extrabold border border-slate-200/50"
              : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
          }`}
        >
          <XCircle className="w-4 h-4" />
          <span>Rejected</span>
          <span
            className={`font-semibold px-2 py-0.5 rounded-full text-[10px] ${
              activeTab === "rejected"
                ? "bg-red-100 text-red-600"
                : "bg-slate-200 text-slate-600"
            }`}
          >
            {grouped.rejected.length}
          </span>
        </button>
      </div>

      {/* Main Discoveries Feed */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-3 bg-white border border-slate-200 rounded-2xl shadow-sm">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          <span className="text-sm font-semibold text-slate-400">Syncing workforce console...</span>
        </div>
      ) : currentTabSignals.length === 0 ? (
        /* Empty State */
        <div className="bg-white border border-slate-200 rounded-2xl p-16 text-center shadow-sm">
          <div className="w-16 h-16 bg-slate-50 border border-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Inbox className="w-8 h-8 text-slate-300" />
          </div>
          <h3 className="font-bold text-slate-800 text-base mb-1">
            {activeTab === "pending"
              ? "Your Inbox is Clean!"
              : activeTab === "approved"
              ? "No Approved Discoveries Yet"
              : "No Rejected Discoveries"}
          </h3>
          <p className="text-xs text-slate-400 max-w-xs mx-auto mb-6">
            {activeTab === "pending"
              ? "Our daily scrapers are currently monitoring all active target corporate profiles. When trigger signals are detected, they appear here."
              : "Your team has not made verification decisions under this filter status."}
          </p>
          {activeTab === "pending" && (
            <button
              onClick={handleTriggerScraper}
              disabled={triggeringScraper}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-500 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-xs transition-colors"
            >
              Trigger Scraper On-Demand
            </button>
          )}
        </div>
      ) : (
        /* Interactive Cards List */
        <div className="space-y-4">
          {currentTabSignals.map((sig) => (
            <div
              key={sig.id}
              className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row justify-between gap-6 hover:shadow-md hover:border-slate-300 transition-all duration-200 group relative overflow-hidden"
            >
              {/* Highlight ribbon based on status */}
              <div
                className={`absolute top-0 bottom-0 left-0 w-1.5 ${
                  sig.status === "approved"
                    ? "bg-emerald-500"
                    : sig.status === "rejected"
                    ? "bg-red-500"
                    : "bg-blue-500"
                }`}
              ></div>

              {/* Feed Card Content */}
              <div className="space-y-4 flex-1 pl-1">
                {/* Meta details */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-500 text-xs font-mono">
                    <Building2 className="w-4 h-4 text-slate-400" />
                  </div>
                  
                  {/* Category Signal Badge */}
                  {sig.signal_type && (
                    <span
                      className={`text-[9px] font-bold uppercase tracking-wider border px-2 py-0.5 rounded-full ${getCategoryStyles(
                        sig.signal_type
                      )}`}
                    >
                      {sig.signal_type}
                    </span>
                  )}

                  {/* Relative Clock Time */}
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-medium">
                    <Clock className="w-3.5 h-3.5" />
                    <span>
                      {new Date(sig.created_at).toLocaleDateString("id-ID", {
                        day: "numeric",
                        month: "short",
                        year: "numeric"
                      })}
                    </span>
                  </div>
                </div>

                {/* News details */}
                <div className="space-y-2">
                  <h3 className="font-bold text-slate-800 text-base leading-tight group-hover:text-blue-600 transition-colors">
                    {sig.headline}
                  </h3>
                  {sig.summary && (
                    <div className="text-xs text-slate-600 bg-slate-50 p-3.5 rounded-xl border border-slate-100 leading-relaxed font-medium flex gap-2.5 items-start">
                      <Sparkles className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                      <p>{sig.summary}</p>
                    </div>
                  )}
                </div>

                {/* External link to source */}
                {sig.source_url && (
                  <a
                    href={sig.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-blue-500 hover:text-blue-700 font-bold tracking-wide"
                  >
                    <span>Read Full Coverage</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>

              {/* Action buttons area (Only on Pending tab) */}
              <div className="flex flex-row md:flex-col justify-end items-end gap-2.5 shrink-0 self-start md:self-center w-full md:w-auto pt-4 md:pt-0 border-t md:border-t-0 border-slate-100">
                {sig.status === "pending" ? (
                  <>
                    <button
                      onClick={() => handleUpdateStatus(sig.id, "approved")}
                      disabled={actioningId === sig.id}
                      className="w-1/2 md:w-28 flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2 px-3 rounded-lg shadow-xs transition-colors"
                    >
                      {actioningId === sig.id ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <>
                          <Check className="w-3.5 h-3.5" /> Approve
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(sig.id, "rejected")}
                      disabled={actioningId === sig.id}
                      className="w-1/2 md:w-28 flex items-center justify-center gap-1.5 border border-slate-200 hover:bg-slate-50 text-slate-600 font-bold text-xs py-2 px-3 rounded-lg transition-colors"
                    >
                      {actioningId === sig.id ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <>
                          <X className="w-3.5 h-3.5" /> Mute
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  /* Decided state capsule badge */
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg">
                    {sig.status === "approved" ? (
                      <>
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                          Episodic Saved
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                          Muted
                        </span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Floating Premium Toast Notifications Container */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`p-4 rounded-xl border shadow-lg flex items-start gap-3 animate-in slide-in-from-bottom-5 fade-in duration-200 bg-white ${
              toast.type === "success"
                ? "border-emerald-100 bg-emerald-50/10"
                : "border-red-100 bg-red-50/10"
            }`}
          >
            {toast.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            )}
            <div className="flex-1 text-xs font-semibold leading-relaxed text-slate-700">
              {toast.message}
            </div>
            <button
              onClick={() => setToasts((prev) => prev.filter((t) => t.id !== toast.id))}
              className="text-slate-400 hover:text-slate-600 shrink-0"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
