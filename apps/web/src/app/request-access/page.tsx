"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Send, CheckCircle2, ShieldCheck, HelpCircle } from "lucide-react";

export default function RequestAccessPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [industry, setIndustry] = useState("");
  const [reason, setReason] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setErrorMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/workspaces/request-access", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          full_name: fullName,
          company_name: companyName,
          industry: industry || null,
          reason: reason || null,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus("success");
      } else {
        setStatus("error");
        setErrorMessage(data.detail || "Terjadi kesalahan saat mengirimkan permohonan.");
      }
    } catch (err) {
      console.error("request_access_error", err);
      setStatus("error");
      setErrorMessage("Koneksi gagal. Pastikan server backend Anda aktif.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="absolute top-6 left-6">
        <Link
          href="/login"
          className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Kembali ke Login
        </Link>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-50 text-blue-600 mb-4 border border-blue-100">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          AccountAI
        </h2>
        <p className="mt-2 text-sm text-slate-500 max-w-sm mx-auto">
          Aplikasi internal eksklusif. Silakan ajukan permohonan akses gabung untuk organisasi Anda.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-slate-100 sm:px-10">
          {status === "success" ? (
            <div className="text-center py-6">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-green-50 text-green-500 mb-4">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Permohonan Dikirim!</h3>
              <p className="mt-3 text-sm text-slate-500 leading-relaxed">
                Terima kasih, <strong>{fullName}</strong>. Permohonan untuk <strong>{companyName}</strong> telah berhasil kami catat.
              </p>
              <div className="mt-6 bg-slate-50 p-4 rounded-xl text-left border border-slate-100">
                <p className="text-xs text-slate-500 leading-relaxed">
                  💡 <strong>Langkah Selanjutnya:</strong> Tim administrator kami akan meninjau kelayakan email bisnis Anda. Jika disetujui, email konfirmasi registrasi akan dikirim ke <strong>{email}</strong> dalam waktu 24 jam.
                </p>
              </div>
              <div className="mt-8">
                <Link
                  href="/login"
                  className="w-full inline-flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-xs text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-hidden transition-all duration-150"
                >
                  Kembali ke Dashboard Login
                </Link>
              </div>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              {status === "error" && (
                <div className="bg-red-50 border border-red-100 p-4 rounded-xl">
                  <p className="text-sm text-red-600 font-medium">{errorMessage}</p>
                </div>
              )}

              <div>
                <label htmlFor="full-name" className="block text-sm font-semibold text-slate-700">
                  Nama Lengkap
                </label>
                <div className="mt-1">
                  <input
                    id="full-name"
                    name="full_name"
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Contoh: Teguh Pratama"
                    className="appearance-none block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl shadow-xs placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-slate-700">
                  Email Bisnis
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Contoh: teguh@perusahaan.com"
                    className="appearance-none block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl shadow-xs placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="company-name" className="block text-sm font-semibold text-slate-700">
                    Nama Kantor/Tim
                  </label>
                  <div className="mt-1">
                    <input
                      id="company-name"
                      name="company_name"
                      type="text"
                      required
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="Contoh: PT Teguh Jaya"
                      className="appearance-none block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl shadow-xs placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="industry" className="block text-sm font-semibold text-slate-700">
                    Sektor Industri
                  </label>
                  <div className="mt-1">
                    <input
                      id="industry"
                      name="industry"
                      type="text"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      placeholder="Contoh: FinTech"
                      className="appearance-none block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl shadow-xs placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="reason" className="block text-sm font-semibold text-slate-700">
                  Mengapa Anda membutuhkan akses ini?
                </label>
                <div className="mt-1">
                  <textarea
                    id="reason"
                    name="reason"
                    rows={3}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Jelaskan kebutuhan operasional akun Anda..."
                    className="appearance-none block w-full px-3.5 py-2.5 border border-slate-200 rounded-xl shadow-xs placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
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
                    <>Mengirimkan...</>
                  ) : (
                    <>
                      Kirim Permohonan <Send className="w-4 h-4" />
                    </>
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
