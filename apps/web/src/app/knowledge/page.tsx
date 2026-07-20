"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { 
  UploadCloud, 
  Trash2, 
  FileText, 
  Loader2,
  Cpu,
  MessageSquare,
  Send,
  Globe
} from "lucide-react";

export default function GlobalKnowledgePage() {
  const { fetchWithAuth } = useAuth();
  
  const [documents, setDocuments] = useState<any[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // Global Chat states
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<{role: "user" | "assistant"; content: string; citations?: any[]}[]>([
    {
      role: "assistant",
      content: "Halo! Saya adalah AI Global Workspace. Anda bisa menanyakan informasi seputar produk, playbook, atau katalog perusahaan yang telah diunggah ke Knowledge Base Global ini."
    }
  ]);

  async function fetchDocuments() {
    try {
      setLoadingDocs(true);
      // Fetch WITHOUT account_id -> will return Global Workspace Documents
      const docsRes = await fetchWithAuth(`http://localhost:8000/api/v1/documents/`);
      if (docsRes.ok) {
        const docsData = await docsRes.json();
        setDocuments(docsData);
      }
    } catch (err) {
      console.error("Failed to fetch global documents", err);
    } finally {
      setLoadingDocs(false);
    }
  }

  useEffect(() => {
    fetchDocuments();
  }, []);

  async function handleFileUpload(file: File) {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      alert("File size exceeds 10MB limit");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    // Notice: no account_id appended. It becomes a global document.

    try {
      const res = await fetchWithAuth(`http://localhost:8000/api/v1/documents/upload`, {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        await fetchDocuments();
      } else {
        const err = await res.json();
        alert(`Gagal unggah: ${err.detail || "Terjadi kesalahan"}`);
      }
    } catch (error) {
      alert("Koneksi gagal ke server");
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteDoc(docId: string) {
    if (!confirm("Hapus dokumen global ini? Seluruh agen AI tidak akan bisa membaca dokumen ini lagi.")) return;
    try {
      const res = await fetchWithAuth(`http://localhost:8000/api/v1/documents/${docId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setDocuments(documents.filter((d) => d.id !== docId));
      }
    } catch (error) {
      alert("Gagal menghapus dokumen");
    }
  }

  async function handleSendChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const query = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", content: query }]);
    setChatLoading(true);

    try {
      // NOTE: We don't send account_id to rag-query for global chat.
      const res = await fetchWithAuth(`http://localhost:8000/api/v1/documents/rag-query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query, account_id: null }),
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.answer, citations: data.citations }
        ]);
      } else {
        setChatMessages((prev) => [...prev, { role: "assistant", content: "Maaf, terjadi kesalahan saat menghubungi AI." }]);
      }
    } catch (error) {
      setChatMessages((prev) => [...prev, { role: "assistant", content: "Koneksi ke backend gagal." }]);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Globe className="w-6 h-6 text-blue-600" />
          Global Knowledge Hub
        </h1>
        <p className="text-sm text-slate-500 max-w-2xl leading-relaxed">
          Unggah dokumen perusahaan Anda (Layer 2 - Workspace Knowledge) seperti Katalog Produk, Pricelist, atau Playbook Penjualan di sini.
          Dokumen di sini akan digunakan oleh semua Digital Employee untuk memberikan rekomendasi penjualan ke SELURUH akun target Anda.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left side - Document manager */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
              <UploadCloud className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                Workspace Internal Documents (PDF)
              </h3>
            </div>

            {/* Drag & Drop uploader area */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileUpload(e.dataTransfer.files[0]);
                }
              }}
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all ${
                dragActive
                  ? "border-blue-500 bg-blue-50/50"
                  : "border-slate-200 hover:border-slate-300 bg-slate-50/30"
              }`}
            >
              <UploadCloud className={`w-10 h-10 mb-3 ${dragActive ? "text-blue-500" : "text-slate-400"}`} />
              <p className="text-sm font-semibold text-slate-700">
                Seret & letakkan berkas PDF Produk Anda di sini
              </p>
              <p className="text-xs text-slate-400 mt-1 mb-4">
                Atau klik tombol di bawah untuk memilih file (Maksimal 10MB)
              </p>

              <label className="relative cursor-pointer bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold px-4 py-2 rounded-lg shadow-xs transition-colors flex items-center gap-1">
                {uploading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" /> Mengindeks PDF Global...
                  </>
                ) : (
                  "Pilih File PDF Global"
                )}
                <input
                  type="file"
                  accept=".pdf"
                  disabled={uploading}
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                />
              </label>
            </div>

            {/* File list table */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Daftar Dokumen Global ({documents.length})
              </h4>

              {loadingDocs ? (
                <div className="flex items-center justify-center py-6 text-slate-400">
                  <Loader2 className="w-5 h-5 animate-spin" />
                </div>
              ) : documents.length === 0 ? (
                <div className="bg-slate-50/50 border border-slate-100 rounded-lg p-6 text-center text-slate-400 text-xs">
                  Belum ada dokumen global (Brosur, Pricelist) yang diunggah.
                </div>
              ) : (
                <div className="border border-slate-100 rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-100 text-slate-500 font-bold">
                        <th className="p-3">Nama Berkas</th>
                        <th className="p-3">Ukuran</th>
                        <th className="p-3">Tanggal Unggah</th>
                        <th className="p-3 text-right">Aksi</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50 text-slate-700">
                      {documents.map((doc) => (
                        <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                          <td className="p-3 font-semibold text-slate-800 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-red-500" />
                            {doc.filename}
                          </td>
                          <td className="p-3 text-slate-500">
                            {(doc.file_size / 1024).toFixed(1)} KB
                          </td>
                          <td className="p-3 text-slate-500">
                            {new Date(doc.created_at).toLocaleDateString()}
                          </td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => handleDeleteDoc(doc.id)}
                              className="text-slate-400 hover:text-red-600 p-1.5 rounded-md hover:bg-red-50 transition-colors"
                              title="Hapus dokumen"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right side - RAG chatbot console */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col h-[580px] justify-between">
          <div className="space-y-4 flex flex-col flex-1 min-h-0">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
              <MessageSquare className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                Uji Coba Global AI
              </h3>
            </div>

            {/* Scrollable conversation bubble */}
            <div className="flex-1 overflow-y-auto pr-1 space-y-4 text-xs scrollbar-thin">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex flex-col max-w-[85%] rounded-2xl p-4 gap-2 ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white ml-auto rounded-tr-none"
                      : "bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-none shadow-xs"
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-line">{msg.content}</p>
                  
                  {/* Citations block */}
                  {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 border-t border-slate-200/50 mt-1 flex flex-wrap gap-1 items-center">
                      <span className="text-[9px] text-slate-400 uppercase tracking-wider font-semibold mr-1">Referensi:</span>
                      {msg.citations.map((cite, cIdx) => (
                        <span
                          key={cIdx}
                          className="inline-flex items-center gap-1 bg-white border border-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-md text-[9px] font-bold shadow-2xs"
                        >
                          <Cpu className="w-2.5 h-2.5 text-indigo-500" />
                          {cite.source_name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              
              {chatLoading && (
                <div className="flex items-center gap-2 bg-slate-50 border border-slate-100 text-slate-500 rounded-2xl rounded-tl-none p-4 max-w-[40%] shadow-xs">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                  <span className="font-semibold text-[10px]">AI sedang menganalisis dokumen global...</span>
                </div>
              )}
            </div>
          </div>

          {/* Chat Input form */}
          <form onSubmit={handleSendChat} className="pt-4 border-t border-slate-100 flex gap-2">
            <input
              required
              type="text"
              placeholder="Tanyakan katalog produk, harga, panduan..."
              disabled={chatLoading}
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 border border-slate-200 px-3 py-2 rounded-lg text-xs focus:outline-hidden focus:border-indigo-500 transition-colors bg-slate-50 focus:bg-white"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatInput.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white p-2.5 rounded-lg transition-all shadow-xs flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
