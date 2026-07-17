import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "../components/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AccountAI - Enterprise Account Intelligence Platform",
  description: "AI-powered living account intelligence platform for enterprise Account Managers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex bg-slate-50">
        {/* Persistent Workspace Sidebar */}
        <Sidebar />
        
        {/* Main Content Pane */}
        <div className="flex-1 pl-64 min-h-screen flex flex-col">
          {/* Header Bar */}
          <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-800">
                Workspace Dashboard
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              {/* User profile capsule */}
              <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200">
                <div className="w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[10px] flex items-center justify-center">
                  T
                </div>
                <span className="text-xs font-semibold text-slate-700">Teguh Sales Manager</span>
              </div>
            </div>
          </header>
          
          {/* Page Routing Container */}
          <main className="flex-1 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
