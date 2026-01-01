'use client';

import Link from 'next/link';
import { Card, CardHeader, Badge, Input, Select, Button } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';
import { newId } from '../../lib/localDb';

const typeLabels = {
  agreement: 'Agreement',
  nda: 'NDA',
  contract: 'Contract',
  privacy_policy: 'Privacy Policy',
  terms: 'Terms of Service',
  letter: 'Legal Letter'
};

function statusTone(s) {
  if (s === 'final') return 'green';
  if (s === 'review') return 'amber';
  if (s === 'draft') return 'slate';
  return 'slate';
}

export default function DocumentsPage() {
  const { state, update } = useLocalState();
  const [q, setQ] = useLocalStateValue('docs_q', '');
  const [type, setType] = useLocalStateValue('docs_type', 'all');

  const docs = (state.documents ?? []).filter(d => {
    const matchesQ = !q || (d.title + ' ' + (d.client || '')).toLowerCase().includes(q.toLowerCase());
    const matchesType = type === 'all' || d.type === type;
    return matchesQ && matchesType;
  });

  const createDummy = () => {
    update(s => {
      const id = newId('doc');
      s.documents.unshift({
        id,
        title: 'New Document',
        type: 'agreement',
        status: 'draft',
        client: 'New Client',
        createdAt: new Date().toISOString().slice(0,10),
        summary: 'Draft created in local demo.'
      });
      s.metrics.totalDocuments = s.documents.length;
      return s;
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title="Documents"
          right={<Button onClick={createDummy}>+ Create Document</Button>}
        />
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_220px]">
            <Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search documents..." />
            <Select value={type} onChange={e => setType(e.target.value)}>
              <option value="all">All Types</option>
              {Object.keys(typeLabels).map(k => <option key={k} value={k}>{typeLabels[k]}</option>)}
            </Select>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {docs.map(d => (
              <Link key={d.id} href={`/documents/${d.id}`} className="block">
                <Card className="p-5 hover:shadow-lg transition">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center">📄</div>
                    <div className="min-w-0 flex-1">
                      <div className="text-base font-semibold truncate">{d.title}</div>
                      <div className="mt-1 text-sm text-slate-500 line-clamp-2">{d.summary}</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Badge tone="violet">{d.type}</Badge>
                        <Badge tone={statusTone(d.status)}>{d.status}</Badge>
                      </div>
                      <div className="mt-3 text-sm text-slate-500">
                        <div>Client: {d.client || '—'}</div>
                        <div>{d.createdAt}</div>
                      </div>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
            {!docs.length ? <div className="text-sm text-slate-500">No matching documents.</div> : null}
          </div>
        </div>
      </Card>
    </div>
  );
}

import React from 'react';

function useLocalStateValue(key, initial) {
  const [value, setValue] = React.useState(initial);
  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    const raw = window.localStorage.getItem(key);
    if (raw !== null) setValue(raw);
  }, [key]);
  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(key, value);
  }, [key, value]);
  return [value, setValue];
}
