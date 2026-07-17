"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Building2, 
  Settings, 
  Users, 
  Radio, 
  Cpu, 
  Database 
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Accounts", href: "/accounts", icon: Building2 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0">
      {/* Platform Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200 bg-white">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
            A
          </div>
          <span className="font-bold text-lg text-slate-800 tracking-tight">AccountAI</span>
        </Link>
      </div>

      {/* Active Workspace Selector */}
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
          Active Workspace
        </label>
        <div className="flex items-center justify-between p-2 bg-white rounded-lg border border-slate-200 shadow-sm cursor-pointer hover:bg-slate-50 transition-colors">
          <div className="flex flex-col">
            <span className="font-semibold text-xs text-slate-700 truncate max-w-[150px]">
              Enterprise AM Team
            </span>
            <span className="text-[10px] text-slate-400">ES Global Corp</span>
          </div>
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-600 font-semibold"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-500"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* AI Systems Integration Indicators (SaaS Style) */}
      <div className="p-4 border-t border-slate-200 bg-white space-y-3">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
          AI Status Indicators
        </span>
        <div className="space-y-2">
          {/* NATS Event Broker Indicator */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-600">
              <Radio className="w-3.5 h-3.5 text-blue-500" />
              <span>NATS Event Bus</span>
            </div>
            <span className="font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[10px]">
              Active
            </span>
          </div>
          
          {/* Temporal Workflows Indicator */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-600">
              <Cpu className="w-3.5 h-3.5 text-indigo-500" />
              <span>Temporal Engines</span>
            </div>
            <span className="font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[10px]">
              Online
            </span>
          </div>

          {/* Supabase Connection Indicator */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-600">
              <Database className="w-3.5 h-3.5 text-emerald-500" />
              <span>Supabase Cloud</span>
            </div>
            <span className="font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[10px]">
              Synced
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
