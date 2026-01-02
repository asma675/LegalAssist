"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

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

export default function DocumentDetailPage() {
  const { id } = useParams();
  const router = useRouter();

  const [docs, setDocs] = useState([]);

  useEffect(() => {
    setDocs(loadDocs());
  }, []);

  const doc = useMemo(() => docs.find((d) => d.id === id), [docs, id]);

  function onDelete() {
    const next = docs.filter((d) => d.id !== id);
    saveDocs(next);
    router.push("/documents");
  }

  if (!doc) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-2xl border bg-white/5 p-6">
          <h1 className="text-xl font-semibold">Document not found</h1>
          <p className="mt-2 text-sm opacity-80">
            This document ID doesn’t exist in LocalStorage.
          </p>
          <button
            onClick={() => router.push("/documents")}
            className="mt-4 rounded-lg border px-4 py-2 text-sm"
          >
            Back to Documents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{doc.title}</h1>
          <div className="mt-1 text-sm opacity-80">
            <span className="mr-3">Type: {doc.type || "—"}</span>
            <span className="mr-3">Client: {doc.clientName || "—"}</span>
            <span>Status: {doc.status || "draft"}</span>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => router.push("/documents")}
            className="rounded-lg border px-4 py-2 text-sm"
          >
            Back
          </button>
          <button
            onClick={() => router.push("/document-analyzer")}
            className="rounded-lg border px-4 py-2 text-sm"
          >
            Analyze
          </button>
          <button
            onClick={onDelete}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="rounded-2xl border bg-white/5 p-6">
        <div className="text-sm opacity-80">
          <div>Jurisdiction: {doc?.meta?.jurisdiction || "—"}</div>
          <div>Updated: {doc.updatedAt ? new Date(doc.updatedAt).toLocaleString() : "—"}</div>
        </div>

        <div className="mt-5 rounded-xl border bg-black/10 p-4">
          <pre className="whitespace-pre-wrap text-sm leading-6">
            {doc.content || ""}
          </pre>
        </div>
      </div>
    </div>
  );
}
