"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { supabase } from "../lib/supabase";
import { Session, User } from "@supabase/supabase-js";

// Define local DB user model response
export interface DbUser {
  id: string;
  workspace_id: string;
  email: string;
  full_name: string | null;
  role: "administrator" | "account_manager" | "sales_manager";
  status: "active" | "inactive" | "pending";
}

interface AuthContextType {
  session: Session | null;
  user: User | null;
  dbUser: DbUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ error: string | null }>;
  logout: () => Promise<void>;
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = "http://localhost:8000";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [dbUser, setDbUser] = useState<DbUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Helper: Centralized Fetcher with Bearer Token Injection
  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const activeSession = session || (await supabase.auth.getSession()).data.session;
    const token = activeSession?.access_token || "mock-token-teguh"; // Smart dev fallback

    const headers: Record<string, string> = {};
    if (!(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    // Assign custom headers and authorization
    if (options.headers) {
      Object.assign(headers, options.headers);
    }
    headers["Authorization"] = `Bearer ${token}`;


    const targetUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`;
    
    try {
      const response = await fetch(targetUrl, { ...options, headers });
      if (response.status === 401 && pathname !== "/login" && pathname !== "/register" && pathname !== "/request-access") {
        // Token invalid or expired, log out on frontend
        await logout();
      }
      return response;
    } catch (err) {
      console.error("fetchWithAuth_network_error", err);
      throw err;
    }
  };

  // Fetch local DB user profile associated with verified Supabase Auth
  const fetchDbProfile = async (currentSession: Session) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workspaces/users/me`, {
        headers: {
          Authorization: `Bearer ${currentSession.access_token}`,
        },
      });
      if (response.ok) {
        const profile: DbUser = await response.json();
        setDbUser(profile);
      } else {
        console.warn("fetchDbProfile_not_found_locally");
        setDbUser(null);
      }
    } catch (err) {
      console.error("fetchDbProfile_failed", err);
      setDbUser(null);
    }
  };

  // Sync Supabase Auth sessions
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const { data: { session: initialSession } } = await supabase.auth.getSession();
        setSession(initialSession);
        setUser(initialSession?.user ?? null);
        
        if (initialSession) {
          await fetchDbProfile(initialSession);
        }
      } catch (err) {
        console.error("auth_init_error", err);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();

    // Subscribe to session changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, newSession) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);
        
        if (newSession) {
          await fetchDbProfile(newSession);
          if (pathname === "/login" || pathname === "/register" || pathname === "/request-access") {
            router.push("/");
          }
        } else {
          setDbUser(null);
          if (pathname !== "/login" && pathname !== "/register" && pathname !== "/request-access") {
            router.push("/login");
          }
        }
        setLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [pathname, router]);

  // Route protection redirect checks
  useEffect(() => {
    if (!loading) {
      const publicRoutes = ["/login", "/register", "/request-access"];
      if (!session && !publicRoutes.includes(pathname)) {
        router.push("/login");
      }
    }
  }, [session, loading, pathname, router]);

  // Sign In using Email & Password
  const login = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) return { error: error.message };
      return { error: null };
    } catch (err: any) {
      return { error: err.message || "An unexpected error occurred." };
    }
  };

  // Sign Out
  const logout = async () => {
    setLoading(true);
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    setDbUser(null);
    router.push("/login");
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ session, user, dbUser, loading, login, logout, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
