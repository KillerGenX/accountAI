"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";
import { LogOut, User as UserIcon, Loader2 } from "lucide-react";

export default function MainLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { dbUser, user, loading, logout } = useAuth();

  const isPublicRoute = ["/login", "/register", "/request-access"].includes(pathname);

  if (loading) {
    return (
      <div className="min-h-screen w-full bg-slate-50 flex flex-col justify-center items-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
        <p className="text-sm text-slate-500 font-semibold">Memasuki gerbang sistem keamanan...</p>
      </div>
    );
  }

  // If it's an auth page, render without sidebar and header
  if (isPublicRoute) {
    return <div className="w-full min-h-screen">{children}</div>;
  }

  // Generate initials for the user avatar
  const displayName = dbUser?.full_name || user?.email || "User";
  const userInitials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const userRole = dbUser?.role === "administrator" 
    ? "Administrator" 
    : dbUser?.role === "account_manager" 
    ? "Account Manager" 
    : "Sales Manager";

  return (
    <div className="min-h-full flex w-full">
      {/* Persistent Sidebar */}
      <Sidebar />

      {/* Main Content Pane */}
      <div className="flex-1 pl-64 min-h-screen flex flex-col">
        {/* Header Bar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-500">
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* User profile capsule */}
            <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200 shadow-2xs">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center border border-blue-700">
                {userInitials}
              </div>
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold text-slate-700 leading-none">{displayName}</span>
                <span className="text-[10px] text-slate-500 leading-none mt-0.5">{userRole}</span>
              </div>
            </div>

            {/* Logout button */}
            <button
              onClick={logout}
              title="Keluar"
              className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl border border-slate-200 hover:border-red-100 transition-all cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Page Routing Container */}
        <main className="flex-1 p-8 bg-slate-50">
          {children}
        </main>
      </div>
    </div>
  );
}
