"use client";

import { useEffect, useState, use } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Building2, 
  MapPin, 
  Layers, 
  Globe, 
  ChevronLeft, 
  Briefcase, 
  UserPlus, 
  BookOpen, 
  FileText, 
  Calendar,
  Send,
  Loader2,
  X,
  Mail,
  Phone
} from "lucide-react";
// @ts-ignore
import { Linkedin } from "lucide-react";

interface Account {
  id: string;
  company_name: string;
  company_url: string;
  industry: string;
  sub_industry: string;
  headquarters: string;
  founded_year: number;
  company_size: string;
  employee_count_min: number;
  employee_count_max: number;
  business_summary: string;
  completeness_score: number;
}

interface Contact {
  id: string;
  full_name: string;
  title: string;
  department: string;
  seniority: string;
  buying_role: string;
  email: string;
  phone: string;
  linkedin_url: string;
  is_primary: boolean;
}

interface Note {
  id: string;
  content: string;
  created_at: string;
}

const DEFAULT_WORKSPACE_ID = "348ea7c6-11f3-4589-9518-e567c0958b7f";
const DEFAULT_USER_ID = "5651b60c-a77f-4037-a190-f9e9a7c6eb02";

export default function AccountDetailPage() {
  const params = useParams();
  const router = useRouter();
  const accountId = params.id as string;

  const [account, setAccount] = useState<Account | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "contacts" | "notes">("overview");

  // Sub-states
  const [showAddContact, setShowAddContact] = useState(false);
  const [newNote, setNewNote] = useState("");
  const [submittingNote, setSubmittingNote] = useState(false);

  // New Contact form states
  const [fullName, setFullName] = useState("");
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("");
  const [seniority, setSeniority] = useState("manager");
  const [buyingRole, setBuyingRole] = useState("influencer");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isPrimary, setIsPrimary] = useState(false);
  const [submittingContact, setSubmittingContact] = useState(false);

  async function fetchAccountDetails() {
    try {
      setLoading(true);
      // 1. Fetch main account profile
      const accRes = await fetch(`http://localhost:8000/api/v1/accounts/${accountId}`);
      if (!accRes.ok) throw new Error("Account not found");
      const accData = await accRes.json();
      setAccount(accData);

      // 2. Fetch contacts
      const contactRes = await fetch(`http://localhost:8000/api/v1/accounts/${accountId}/contacts`);
      if (contactRes.ok) {
        const contactData = await contactRes.json();
        setContacts(contactData);
      }

      // 3. Fetch notes
      const notesRes = await fetch(`http://localhost:8000/api/v1/accounts/${accountId}/notes?user_id=${DEFAULT_USER_ID}`);
      if (notesRes.ok) {
        const notesData = await notesRes.json();
        setNotes(notesData);
      }
    } catch (err) {
      console.error(err);
      router.push("/accounts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (accountId) {
      fetchAccountDetails();
    }
  }, [accountId]);

  async function handleAddNote(e: React.FormEvent) {
    e.preventDefault();
    if (!newNote.trim()) return;

    try {
      setSubmittingNote(true);
      const res = await fetch(`http://localhost:8000/api/v1/accounts/${accountId}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: DEFAULT_USER_ID,
          content: newNote
        })
      });

      if (!res.ok) throw new Error("Failed to add note");
      
      setNewNote("");
      // Reload details
      fetchAccountDetails();
    } catch (err: any) {
      alert(err.message || "Failed to save note");
    } finally {
      setSubmittingNote(false);
    }
  }

  async function handleAddContact(e: React.FormEvent) {
    e.preventDefault();
    if (!fullName.trim()) return;

    try {
      setSubmittingContact(true);
      const body = {
        full_name: fullName,
        title: title || null,
        department: department || null,
        seniority,
        buying_role: buyingRole,
        linkedin_url: linkedinUrl || null,
        email: email || null,
        phone: phone || null,
        is_primary: isPrimary
      };

      const res = await fetch(`http://localhost:8000/api/v1/accounts/${accountId}/contacts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (!res.ok) throw new Error("Failed to add contact");

      // Reset form
      setFullName("");
      setTitle("");
      setDepartment("");
      setSeniority("manager");
      setBuyingRole("influencer");
      setLinkedinUrl("");
      setEmail("");
      setPhone("");
      setIsPrimary(false);
      setShowAddContact(false);

      // Reload
      fetchAccountDetails();
    } catch (err: any) {
      alert(err.message || "Failed to add contact");
    } finally {
      setSubmittingContact(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <span className="text-sm font-medium text-slate-500">Loading intelligence profile...</span>
      </div>
    );
  }

  if (!account) return null;

  return (
    <div className="space-y-6">
      {/* Back button link */}
      <div>
        <Link 
          href="/accounts" 
          className="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-xs font-semibold"
        >
          <ChevronLeft className="w-4 h-4" /> Back to Accounts
        </Link>
      </div>

      {/* Account Profile Header card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 text-xl font-bold font-mono">
            {account.company_name.slice(0, 2).toUpperCase()}
          </div>
          
          <div className="space-y-1">
            <h1 className="text-xl font-bold text-slate-900 leading-tight">
              {account.company_name}
            </h1>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Layers className="w-3.5 h-3.5 text-slate-400" /> {account.industry || "General"}
              </span>
              {account.headquarters && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" /> {account.headquarters}
                </span>
              )}
              {account.company_url && (
                <a 
                  href={account.company_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="flex items-center gap-1 text-blue-600 hover:underline"
                >
                  <Globe className="w-3.5 h-3.5" /> Website
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Completeness score circle indicator */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end gap-0.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Profile Score
            </span>
            <span className="text-sm font-extrabold text-slate-800">
              {account.completeness_score}% Complete
            </span>
          </div>
          
          {/* Progress bar */}
          <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
            <div 
              className="h-full bg-blue-600 rounded-full" 
              style={{ width: `${account.completeness_score}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Tabs navigation panel */}
      <div className="border-b border-slate-200 flex gap-6">
        {(["overview", "contacts", "notes"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 text-sm font-bold capitalize transition-colors border-b-2 px-1 ${
              activeTab === tab
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content area */}
      <div className="space-y-6">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* AI Summary card */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm lg:col-span-2 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <FileText className="w-4 h-4 text-blue-600" />
                <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                  AI Generated Intelligence Overview
                </h3>
              </div>
              
              <div className="text-slate-700 text-sm leading-relaxed whitespace-pre-line">
                {account.business_summary || (
                  <div className="py-6 text-center text-slate-400 italic">
                    AI research employee is currently profiling this account. Please refresh in a moment.
                  </div>
                )}
              </div>
            </div>

            {/* Profile specifications sidebar card */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4 h-fit">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <Building2 className="w-4 h-4 text-indigo-600" />
                <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                  Company Info
                </h3>
              </div>
              
              <div className="space-y-3 text-xs text-slate-700">
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-400 font-medium">Segment</span>
                  <span className="font-semibold text-slate-800">{account.company_size || "Enterprise"}</span>
                </div>
                {account.employee_count_min && (
                  <div className="flex justify-between py-1 border-b border-slate-50">
                    <span className="text-slate-400 font-medium">Employees</span>
                    <span className="font-semibold text-slate-800">
                      {account.employee_count_min.toLocaleString()} - {account.employee_count_max?.toLocaleString()}
                    </span>
                  </div>
                )}
                {account.founded_year && (
                  <div className="flex justify-between py-1 border-b border-slate-50">
                    <span className="text-slate-400 font-medium">Founded Year</span>
                    <span className="font-semibold text-slate-800">{account.founded_year}</span>
                  </div>
                )}
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-400 font-medium">AI Update Schedule</span>
                  <span className="font-semibold text-slate-800">Daily Overnight</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CONTACTS TAB */}
        {activeTab === "contacts" && (
          <div className="space-y-6">
            {/* Action Header */}
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                Mapped Key Contacts ({contacts.length})
              </h3>
              <button
                onClick={() => setShowAddContact(true)}
                className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-3 py-2 rounded-lg transition-colors shadow-xs"
              >
                <UserPlus className="w-3.5 h-3.5" /> Add Contact
              </button>
            </div>

            {/* Contact list cards */}
            {contacts.length === 0 ? (
              <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-400 text-sm">
                No contacts mapped for this account. Click &quot;Add Contact&quot; to register decision makers.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {contacts.map((contact) => (
                  <div 
                    key={contact.id}
                    className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4 flex flex-col justify-between"
                  >
                    <div className="space-y-3">
                      {/* Name & Badge */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <p className="font-bold text-slate-800 text-sm leading-tight">
                            {contact.full_name}
                          </p>
                          <p className="text-xs text-slate-500 font-medium">{contact.title}</p>
                        </div>
                        {contact.is_primary && (
                          <span className="text-[9px] font-bold text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded">
                            Primary
                          </span>
                        )}
                      </div>

                      {/* Details row */}
                      <div className="space-y-1.5 text-xs text-slate-600">
                        {contact.department && (
                          <div className="flex items-center gap-1.5">
                            <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                            <span>{contact.department} ({contact.seniority.replace("_", "-").toUpperCase()})</span>
                          </div>
                        )}
                        {contact.email && (
                          <div className="flex items-center gap-1.5">
                            <Mail className="w-3.5 h-3.5 text-slate-400" />
                            <a href={`mailto:${contact.email}`} className="hover:underline hover:text-blue-600">{contact.email}</a>
                          </div>
                        )}
                        {contact.phone && (
                          <div className="flex items-center gap-1.5">
                            <Phone className="w-3.5 h-3.5 text-slate-400" />
                            <span>{contact.phone}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Footer linkedin icons */}
                    <div className="border-t border-slate-100 pt-3 flex justify-between items-center text-xs">
                      <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider">
                        {contact.buying_role.replace("_", " ")}
                      </span>
                      {contact.linkedin_url && (
                        <a 
                          href={contact.linkedin_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-slate-400 hover:text-blue-600 transition-colors"
                        >
                          <Linkedin className="w-4 h-4 fill-current" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Add Contact Modal Panel */}
            {showAddContact && (
              <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
                <div className="bg-white border border-slate-200 rounded-xl shadow-lg w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-150">
                  <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                    <h2 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                      Add Key Contact
                    </h2>
                    <button 
                      onClick={() => setShowAddContact(false)}
                      className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <form onSubmit={handleAddContact} className="p-6 space-y-4">
                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                        Full Name *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Budi Santoso"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Job Title
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. CTO"
                          value={title}
                          onChange={(e) => setTitle(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Department
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. IT & Network"
                          value={department}
                          onChange={(e) => setDepartment(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Seniority
                        </label>
                        <select
                          value={seniority}
                          onChange={(e) => setSeniority(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors bg-white"
                        >
                          <option value="c_level">C-Level</option>
                          <option value="vp">VP</option>
                          <option value="director">Director</option>
                          <option value="manager">Manager</option>
                          <option value="individual">Individual Contributor</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Buying Role
                        </label>
                        <select
                          value={buyingRole}
                          onChange={(e) => setBuyingRole(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors bg-white"
                        >
                          <option value="decision_maker">Decision Maker</option>
                          <option value="influencer">Influencer</option>
                          <option value="evaluator">Technical Evaluator</option>
                          <option value="procurement">Procurement</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Email
                        </label>
                        <input
                          type="email"
                          placeholder="cto@company.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Phone Number
                        </label>
                        <input
                          type="text"
                          placeholder="+62..."
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                        LinkedIn URL
                      </label>
                      <input
                        type="url"
                        placeholder="https://linkedin.com/..."
                        value={linkedinUrl}
                        onChange={(e) => setLinkedinUrl(e.target.value)}
                        className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors"
                      />
                    </div>

                    <div className="flex items-center gap-2 pt-2">
                      <input
                        type="checkbox"
                        id="isPrimaryContact"
                        checked={isPrimary}
                        onChange={(e) => setIsPrimary(e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                      />
                      <label htmlFor="isPrimaryContact" className="text-xs text-slate-700 font-semibold cursor-pointer">
                        Mark as Primary Contact for Account
                      </label>
                    </div>

                    <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => setShowAddContact(false)}
                        className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 font-semibold transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={submittingContact}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 font-semibold shadow-sm transition-colors flex items-center gap-2"
                      >
                        {submittingContact ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                          </>
                        ) : (
                          "Save Contact"
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        {/* NOTES TAB */}
        {activeTab === "notes" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Notes List area */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                Personal Notes Timeline
              </h3>
              
              {notes.length === 0 ? (
                <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400 text-sm">
                  No notes recorded yet. Write private notes below.
                </div>
              ) : (
                <div className="space-y-4">
                  {notes.map((note) => (
                    <div 
                      key={note.id}
                      className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-2"
                    >
                      <div className="flex items-center gap-2 text-slate-400 text-xs">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{new Date(note.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap">
                        {note.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Note Ingestion Panel */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm h-fit">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100 mb-4">
                <BookOpen className="w-4 h-4 text-blue-600" />
                <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
                  New Private Note
                </h3>
              </div>

              <form onSubmit={handleAddNote} className="space-y-4">
                <p className="text-[10px] leading-relaxed text-slate-400">
                  Notes entered here are private to your Account Manager identity and stored in Knowledge Layer 3. They are not shared across workspaces or used for global LLM training.
                </p>
                
                <textarea
                  required
                  rows={6}
                  placeholder="Type your notes here..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="w-full border border-slate-200 px-3 py-2 rounded-lg text-sm focus:outline-hidden focus:border-blue-500 transition-colors resize-none"
                />
                
                <button
                  type="submit"
                  disabled={submittingNote}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm py-2.5 rounded-lg shadow-sm transition-colors"
                >
                  {submittingNote ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" /> Save Note
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
