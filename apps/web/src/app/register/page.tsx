"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "../../lib/supabase";
import { ShieldAlert, KeyRound, Loader2, Compass, UserPlus, CheckCircle2 } from "lucide-react";

function RegisterContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const emailParam = searchParams.get("email") || "";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [invitedName, setInvitedName] = useState("");
  const [companyName, setCompanyName] = useState("");
  
  const [verifying, setVerifying] = useState(true);
  const [isInviteValid, setIsInviteValid] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  // Step 1: Verify the invitation on page load
  useEffect(() => {
    const verifyInvite = async () => {
      if (!emailParam) {
        setVerifying(false);
        setIsInviteValid(false);
        return;
      }

      setEmail(emailParam);

      try {
        const response = await fetch(`http://localhost:8000/api/v1/workspaces/verify-invite?email=${encodeURIComponent(emailParam)}`);
        const data = await response.json();

        if (response.ok && data.is_valid) {
          setIsInviteValid(true);
          setInvitedName(data.full_name || "");
          setCompanyName(data.company_name || "");
        } else {
          setIsInviteValid(false);
        }
      } catch (err) {
        console.error("verify_invite_network_error", err);
        setIsInviteValid(false);
      } finally {
        setVerifying(false);
      }
    };

    verifyInvite();
  }, [emailParam]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setErrorMessage("");

    if (password !== confirmPassword) {
      setStatus("error");
      setErrorMessage("Konfirmasi kata sandi tidak cocok.");
      return;
    }

    if (password.length < 6) {
      setStatus("error");
      setErrorMessage("Kata sandi harus minimal 6 karakter.");
      return;
    }

    try {
      // 1. Sign up the user in Supabase Auth Cloud
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email,
        password,
      });

      if (authError) {
        setStatus("error");
        setErrorMessage(authError.message);
        return;
      }

      const supabaseUser = authData.user;
      if (!supabaseUser) {
        setStatus("error");
        setErrorMessage("Gagal membuat kredensial keamanan di Supabase.");
        return;
      }

      // 2. Claim the invite in FastAPI to synchronize local DB users
      const claimResponse = await fetch("http://localhost:8000/api/v1/workspaces/claim-invite", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          supabase_user_id: supabaseUser.id,
          full_name: invitedName || email.split("@")[0],
        }),
      });

      const claimData = await claimResponse.json();

      if (claimResponse.ok) {
        setStatus("success");
      } else {
        setStatus("error");
        setErrorMessage(claimData.detail || "Gagal menyinkronkan profil database lokal Anda.");
      }
    } catch (err: any) {
      console.error("register_e2e_error", err);
      setStatus("error");
      setErrorMessage("Koneksi gagal. Hubungi administrator sistem.");
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center py-12 px-4">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
        <p className="text-sm text-slate-500 font-medium">Memverifikasi tautan undangan Anda...</p>
      </div>
    );
  }

  // If the invite is invalid or missing, block access and render uninvited template
  if (!isInviteValid) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-red-50 text-red-600 mb-4 border border-red-100">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Registrasi Terbatas (Invite-Only)
          </h2>
          <p className="mt-2 text-sm text-slate-500 max-w-sm mx-auto leading-relaxed">
            Maaf, pendaftaran akun di platform **Project Brain** hanya dibuka untuk pengguna yang memiliki undangan aktif dari tim administrator.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-slate-100 sm:px-10 text-center">
            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              Jika organisasi Anda belum terdaftar atau Anda membutuhkan akses baru, silakan ajukan permohonan gabung resmi di bawah ini.
            </p>
            <div className="space-y-3">
              <Link
                href="/request-access"
                className="w-full inline-flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-all cursor-pointer"
              >
                Minta Akses Gabung <UserPlus className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="w-full inline-flex justify-center py-2.5 px-4 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-all"
              >
                Kembali ke Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-50 text-blue-600 mb-4 border border-blue-100">
          <Compass className="w-6 h-6" />
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          AccountAI
        </h2>
        <p className="mt-2 text-sm text-slate-500">
          Selesaikan Pengesahan Akun Keanggotaan Anda
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-slate-100 sm:px-10">
          {status === "success" ? (
            <div className="text-center py-6">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-green-50 text-green-500 mb-4">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Registrasi Berhasil!</h3>
              <p className="mt-3 text-sm text-slate-500 leading-relaxed">
                Akun untuk <strong>{email}</strong> telah berhasil dibuat dan terikat dengan workspace <strong>{companyName}</strong> secara aman.
              </p>
              <div className="mt-8">
                <Link
                  href="/login"
                  className="w-full inline-flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-xs text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-all duration-150"
                >
                  Masuk Sekarang
                </Link>
              </div>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl text-left">
                <p className="text-xs text-blue-700 leading-relaxed">
                  👋 Halo <strong>{invitedName || "Rekan"}</strong>, Anda diundang untuk bergabung dengan workspace <strong>{companyName || "tim Anda"}</strong>. Silakan buat kata sandi baru untuk mengamankan akun Anda.
                </p>
              </div>

              {status === "error" && (
                <div className="bg-red-50 border border-red-100 p-4 rounded-xl">
                  <p className="text-sm text-red-600 font-medium leading-relaxed">{errorMessage}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-slate-500">
                  Alamat Email (Terkunci)
                </label>
                <div className="mt-1">
                  <input
                    type="email"
                    disabled
                    value={email}
                    className="block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-400 text-sm cursor-not-allowed"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-slate-700">
                  Buat Kata Sandi
                </label>
                <div className="mt-1 relative rounded-xl shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    <KeyRound className="h-4.5 w-4.5 text-slate-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimal 6 karakter"
                    className="appearance-none block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="confirm-password" className="block text-sm font-semibold text-slate-700">
                  Ulangi Kata Sandi
                </label>
                <div className="mt-1 relative rounded-xl shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    <KeyRound className="h-4.5 w-4.5 text-slate-400" />
                  </div>
                  <input
                    id="confirm-password"
                    name="confirm_password"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="appearance-none block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={status === "submitting"}
                  className="w-full inline-flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-hidden disabled:opacity-50 transition-all duration-150 cursor-pointer"
                >
                  {status === "submitting" ? (
                    <>
                      <Loader2 className="w-4.5 h-4.5 animate-spin" /> Mendaftarkan Akun...
                    </>
                  ) : (
                    <>Verifikasi & Aktivasi Akun</>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center py-12 px-4">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
        <p className="text-sm text-slate-500 font-medium">Memuat halaman registrasi...</p>
      </div>
    }>
      <RegisterContent />
    </Suspense>
  );
}
