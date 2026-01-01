'use client';

import Link from 'next/link';
import { Card, CardHeader, Badge, Button } from '../../../components/ui';
import { useLocalState } from '../../../lib/useLocalState';
import { generateDocumentBody } from '../../../lib/localDb';

function tone(s) {
  if (s === 'final') return 'green';
  if (s === 'review') return 'amber';
  if (s === 'draft') return 'slate';
  return 'slate';
}

export default function DocumentView({ params }) {
  const { state, update } = useLocalState();
  const doc = (state.documents ?? []).find(d => d.id === params.id);

  if (!doc) {
    return (
      <Card className="p-6">
        <div className="text-lg font-semibold">Document not found</div>
        <Link className="mt-2 inline-block text-sm text-violet-700 hover:underline" href="/documents">Back to documents</Link>
      </Card>
    );
  }

  const body = doc.body || generateDocumentBody({
    docType: doc.type,
    client: doc.client,
    title: doc.title,
    jurisdiction: doc.jurisdiction,
    notes: doc.notes
  });

  const saveAsDraft = () => {
    update(s => {
      const idx = s.documents.findIndex(d => d.id === doc.id);
      if (idx >= 0) s.documents[idx].status = 'draft';
      return s;
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title={doc.title}
          right={
            <div className="flex items-center gap-2">
              <Badge tone="violet">{doc.type}</Badge>
              <Badge tone={tone(doc.status)}>{doc.status}</Badge>
            </div>
          }
        />
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="text-sm text-slate-600"><span className="font-medium text-slate-900">Client:</span> {doc.client || '—'}</div>
            <div className="text-sm text-slate-600"><span className="font-medium text-slate-900">Created:</span> {doc.createdAt}</div>
          </div>

          <pre className="whitespace-pre-wrap rounded-2xl border bg-slate-50 p-4 text-sm leading-6">{body}</pre>

          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={saveAsDraft}>Mark as Draft</Button>
            <Link href="/documents"><Button variant="subtle">Back</Button></Link>
          </div>
        </div>
      </Card>
    </div>
  );
}
