"use client";

import { useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardHeader, Button, Badge } from "../../../components/ui";
import { useLocalState } from "../../../lib/useLocalState";

export default function DocumentDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { state, update } = useLocalState();

  const doc = useMemo(() => {
    return (state?.documents || []).find((d) => d.id === id);
  }, [state, id]);

  if (!doc) {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader title="Document not found" />
          <div className="p-5 text-sm text-slate-600">
            This document may not exist in LocalStorage.
            <div className="mt-4">
              <Button onClick={() => router.push("/documents")}>Back to Documents</Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const remove = () => {
    update((s) => {
      s.documents = (s.documents || []).filter((d) => d.id !== id);
      s.metrics.totalDocuments = s.documents.length;
      return s;
    });
    router.push("/documents");
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title={doc.title}
          right={
            <div className="flex items-center gap-2">
              <Badge tone="slate">{doc.type}</Badge>
              <Badge tone="violet">{doc.status || "draft"}</Badge>
            </div>
          }
        />
        <div className="p-5 space-y-3">
          <div className="text-sm text-slate-600">
            <div><span className="font-medium">Client:</span> {doc.client || "—"}</div>
            <div><span className="font-medium">Jurisdiction:</span> {doc.jurisdiction || "—"}</div>
            <div><span className="font-medium">Created:</span> {doc.createdAt || "—"}</div>
          </div>

          <div className="rounded-2xl border bg-slate-50 p-4">
            <pre className="whitespace-pre-wrap text-sm leading-6 text-slate-800">
              {doc.body || ""}
            </pre>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => router.push("/documents")}>Back</Button>
            <Button variant="outline" onClick={() => router.push("/document-analyzer")}>Analyze</Button>
            <Button variant="danger" onClick={remove}>Delete</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
