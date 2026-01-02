"use client";

import { useEffect, useMemo, useState } from "react";

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

export default function DocumentAnalyzerPage() {
  const [docs, setDocs] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const selectedDoc = useMemo(
    () => docs.find((d) => d.id === selectedId),
    [docs, selectedId]
  );

  const [text, setText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    const d = loadDocs();
    setDocs(d);
  }, []);

  useEffect(() => {
    if (selectedDoc?.content) {
      setText(selectedDoc.content);
      setAnalysis(null);
      setError("");
    }
  }, [selectedDoc]);

  async function onAnalyze() {
    setError("");
    setAnalysis(null);

    if (!text.trim()) {
      setError("Paste text or select a saved document first.");
      return;
    }

    setAnalyzing(true);
    try {
      const res = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Analysis failed");

      setAnalysis(data);
    } catch (e) {
      setError(e?.message || "Something went wrong.");
    } finally {
      setAnalyzing(false);
    }
  }

  function onSaveAnalysisToDoc() {
    setError("");

    if (!selectedDoc?.id) {
      setError("Select a saved document first to attach analysis.");
      return;
    }
    if (!analysis) {
      setError("Run analysis first.");
      return;
    }

    const next = docs.map((d) => {
      if (d.id !== selectedDoc.id) return d;
      return {
        ...d,
        updatedAt: new Date().toISOString(),
        meta: {
          ...(d.meta || {}),
          lastAnalysis: analysis,
          lastAnalysisAt: new Date().toISOString(),
        },
      };
    });

    saveDocs(next);
    setDocs(next);
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Document Analyzer</h1>
        <p className="text-sm opacity-80">
          Paste a document (or load one you saved) and get AI summary + risk
          flags.
        </p>
      </div>

      {error ? (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm">
          {error}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left */}
        <div className="rounded-2xl border bg-white/5 p-5">
          <div className="mb-3 grid gap-2">
            <label className="text-sm font-medium">Load a saved document</label>
            <select
              className="rounded-lg border bg-transparent px-3 py-2"
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              <option value="">— Choose —</option>
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title || d.type} ({new Date(d.updatedAt).toLocaleDateString()})
                </option>
              ))}
            </select>
            <p className="text-xs opacity-70">
              Or paste content manually below.
            </p>
          </div>

          <label className="text-sm font-medium">Document text</label>
          <textarea
            className="mt-2 min-h-[420px] w-full rounded-xl border bg-transparent px-3 py-3 text-sm leading-6"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste document text here…"
          />

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={onAnalyze}
              disabled={analyzing}
              className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            >
              {analyzing ? "Analyzing…" : "Analyze"}
            </button>

            <button
              onClick={onSaveAnalysisToDoc}
              disabled={!analysis || !selectedDoc?.id}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              Save analysis to selected doc
            </button>
          </div>
        </div>

        {/* Right */}
        <div className="rounded-2xl border bg-white/5 p-5">
          <div className="mb-3">
            <h2 className="text-lg font-semibold">Results</h2>
            <p className="text-xs opacity-70">
              Output is best-effort and not legal advice.
            </p>
          </div>

          {!analysis ? (
            <div className="rounded-xl border border-dashed p-6 text-sm opacity-70">
              Run analysis to see summary, risks, clauses, and recommendations.
            </div>
          ) : (
            <div className="space-y-5">
              <section>
                <h3 className="text-sm font-semibold">Summary</h3>
                <p className="mt-2 whitespace-pre-wrap rounded-xl border bg-black/10 p-3 text-sm leading-6">
                  {analysis.summary || "(No summary returned)"}
                </p>
              </section>

              <section>
                <h3 className="text-sm font-semibold">Risks</h3>
                <ul className="mt-2 space-y-2">
                  {(analysis.risks || []).length === 0 ? (
                    <li className="text-sm opacity-70">(No risks returned)</li>
                  ) : (
                    analysis.risks.map((r, idx) => (
                      <li
                        key={idx}
                        className="rounded-xl border bg-black/10 p-3 text-sm"
                      >
                        {typeof r === "string" ? r : JSON.stringify(r)}
                      </li>
                    ))
                  )}
                </ul>
              </section>

              <section>
                <h3 className="text-sm font-semibold">Clauses</h3>
                <div className="mt-2 space-y-2">
                  {(analysis.clauses || []).length === 0 ? (
                    <div className="text-sm opacity-70">(No clauses returned)</div>
                  ) : (
                    analysis.clauses.map((c, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border bg-black/10 p-3 text-sm"
                      >
                        <div className="font-medium">
                          {c?.name || `Clause ${idx + 1}`}
                        </div>
                        <div className="mt-2 whitespace-pre-wrap opacity-90">
                          {c?.excerpt || ""}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>

              <section>
                <h3 className="text-sm font-semibold">Recommendations</h3>
                <ul className="mt-2 list-disc space-y-2 pl-5 text-sm">
                  {(analysis.recommendations || []).length === 0 ? (
                    <li className="opacity-70">(No recommendations returned)</li>
                  ) : (
                    analysis.recommendations.map((rec, idx) => (
                      <li key={idx}>
                        {typeof rec === "string" ? rec : JSON.stringify(rec)}
                      </li>
                    ))
                  )}
                </ul>
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
