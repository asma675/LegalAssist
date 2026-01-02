"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

const LS_DOCS_KEY = "legalassist.documents.v1";

function loadDocs() {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(LS_DOCS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveDocs(docs) {
  localStorage.setItem(LS_DOCS_KEY, JSON.stringify(docs));
}

function createDoc({
  title,
  type,
  clientName,
  matter,
  content,
  meta = {},
}) {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title: title || `${type} — ${clientName || "Client"}`,
    type,
    clientName: clientName || "",
    matter: matter || "",
    content: content || "",
    createdAt: now,
    updatedAt: now,
    status: "draft",
    meta,
  };
}

export default function DocumentGeneratorPage() {
  const router = useRouter();

  const [docType, setDocType] = useState("NDA");
  const [title, setTitle] = useState("");
  const [clientName, setClientName] = useState("");
  const [matter, setMatter] = useState("");
  const [jurisdiction, setJurisdiction] = useState("Ontario, Canada");
  const [tone, setTone] = useState("Professional");
  const [keyTerms, setKeyTerms] = useState("");
  const [notes, setNotes] = useState("");

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [draft, setDraft] = useState("");

  const prompt = useMemo(() => {
    return `Draft a ${docType}.

Client: ${clientName || "(not provided)"}
Matter/Context: ${matter || "(not provided)"}
Jurisdiction: ${jurisdiction || "(not provided)"}
Tone: ${tone || "Professional"}

Key terms / constraints (must include if relevant):
${keyTerms || "(none)"}

Additional notes:
${notes || "(none)"}

Output requirements:
- Use clear headings and numbered clauses.
- Keep it practical and readable.
- Include standard sections for this document type.
- Add placeholders where information is missing (e.g., [Effective Date], [Disclosing Party]).
- Provide the final document text only (no commentary).`;
  }, [docType, clientName, matter, jurisdiction, tone, keyTerms, notes]);

  async function onGenerate() {
    setError("");
    setDraft("");
    setGenerating(true);

    try {
      const res = await fetch("/api/ai/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          system:
            "You are a careful legal drafting assistant. Draft professional documents, avoid hallucinating facts, and use placeholders when details are missing.",
          prompt,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "AI generation failed");
      setDraft(data?.text || "");
    } catch (e) {
      setError(e?.message || "Something went wrong.");
    } finally {
      setGenerating(false);
    }
  }

  function onSave() {
    setError("");
    if (!draft.trim()) {
      setError("Nothing to save yet — generate a draft first.");
      return;
    }

    const docs = loadDocs();
    const doc = createDoc({
      title: title || `${docType} — ${clientName || "Client"}`,
      type: docType,
      clientName,
      matter,
      content: draft,
      meta: { jurisdiction, tone, keyTerms, notes },
    });

    const next = [doc, ...docs];
    saveDocs(next);

    // Go to documents list or document details if you have it
    // If you already have /documents/[id], use router.push(`/documents/${doc.id}`)
    router.push("/documents");
  }

  async function onCopy() {
    try {
      await navigator.clipboard.writeText(draft);
    } catch {
      // ignore
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Document Generator</h1>
        <p className="text-sm opacity-80">
          Generate a legal draft with AI, then save it to LocalStorage.
        </p>
      </div>

      {error ? (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: Inputs */}
        <div className="rounded-2xl border bg-white/5 p-5">
          <div className="grid gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Document type</label>
              <select
                className="rounded-lg border bg-transparent px-3 py-2"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
              >
                <option>NDA</option>
                <option>Employment Offer Letter</option>
                <option>Independent Contractor Agreement</option>
                <option>Service Agreement</option>
                <option>Privacy Policy</option>
                <option>Terms of Service</option>
                <option>Cease &amp; Desist Letter</option>
              </select>
            </div>

            <div className="grid gap-2">
              <label className="text-sm font-medium">Title (optional)</label>
              <input
                className="rounded-lg border bg-transparent px-3 py-2"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Mutual NDA — Project Aurora"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Client name</label>
                <input
                  className="rounded-lg border bg-transparent px-3 py-2"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="e.g., Acme Inc."
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Matter / context</label>
                <input
                  className="rounded-lg border bg-transparent px-3 py-2"
                  value={matter}
                  onChange={(e) => setMatter(e.target.value)}
                  placeholder="e.g., Vendor onboarding"
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Jurisdiction</label>
                <input
                  className="rounded-lg border bg-transparent px-3 py-2"
                  value={jurisdiction}
                  onChange={(e) => setJurisdiction(e.target.value)}
                  placeholder="e.g., Ontario, Canada"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Tone</label>
                <select
                  className="rounded-lg border bg-transparent px-3 py-2"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                >
                  <option>Professional</option>
                  <option>Friendly</option>
                  <option>Firm</option>
                  <option>Plain English</option>
                  <option>Formal</option>
                </select>
              </div>
            </div>

            <div className="grid gap-2">
              <label className="text-sm font-medium">
                Key terms / constraints (bullets ok)
              </label>
              <textarea
                className="min-h-[110px] rounded-lg border bg-transparent px-3 py-2"
                value={keyTerms}
                onChange={(e) => setKeyTerms(e.target.value)}
                placeholder={`- Term: 2 years
- Confidentiality covers source code + customer lists
- No reverse engineering
- Governing law: Ontario`}
              />
            </div>

            <div className="grid gap-2">
              <label className="text-sm font-medium">Additional notes</label>
              <textarea
                className="min-h-[90px] rounded-lg border bg-transparent px-3 py-2"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Anything else the draft should include or avoid…"
              />
            </div>

            <button
              onClick={onGenerate}
              disabled={generating}
              className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {generating ? "Generating…" : "Generate Draft"}
            </button>
          </div>
        </div>

        {/* Right: Output */}
        <div className="rounded-2xl border bg-white/5 p-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold">Draft</h2>
              <p className="text-xs opacity-70">
                You can edit this text before saving.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={onCopy}
                disabled={!draft.trim()}
                className="rounded-lg border px-3 py-2 text-xs disabled:opacity-50"
              >
                Copy
              </button>
              <button
                onClick={onSave}
                disabled={!draft.trim()}
                className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white disabled:opacity-50"
              >
                Save Document
              </button>
            </div>
          </div>

          <textarea
            className="min-h-[520px] w-full rounded-xl border bg-transparent px-3 py-3 text-sm leading-6"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Your AI draft will appear here…"
          />
        </div>
      </div>
    </div>
  );
}
