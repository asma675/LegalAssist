'use client';

import { useState } from 'react';
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui';
import { aiSummarizeText } from '../../lib/localDb';

function extractClauses(text) {
  const lower = text.toLowerCase();
  const clauses = [];
  const rules = [
    { key: 'Confidentiality', needles: ['confidential', 'non-disclosure', 'nda'] },
    { key: 'Indemnity', needles: ['indemn', 'hold harmless'] },
    { key: 'Termination', needles: ['terminate', 'termination'] },
    { key: 'Governing Law', needles: ['governing law', 'jurisdiction'] },
    { key: 'Payment', needles: ['payment', 'fees', 'invoice'] }
  ];
  for (const r of rules) {
    const hit = r.needles.some(n => lower.includes(n));
    if (hit) clauses.push(r.key);
  }
  return clauses.length ? clauses : ['No obvious clauses detected (demo)'];
}

export default function DocumentAnalyzerPage() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [clauses, setClauses] = useState([]);

  const analyze = async () => {
    const s = await aiSummarizeText(text);
    setSummary(s);
    setClauses(extractClauses(text));
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Document Analyzer" right={<Badge tone="violet">LocalStorage Demo</Badge>} />
        <div className="p-5 space-y-4">
          <div className="text-sm text-slate-600">
            Paste a contract or document text below. In this demo build, analysis runs locally (no API calls).
          </div>

          <Textarea rows={10} value={text} onChange={e => setText(e.target.value)} placeholder="Paste document text here..." />

          <div className="flex gap-2">
            <Button onClick={analyze} disabled={!text.trim()}>Analyze</Button>
            <Button variant="outline" onClick={() => { setText(''); setSummary(''); setClauses([]); }}>Clear</Button>
          </div>

          {summary ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-2xl border bg-white p-4">
                <div className="text-sm font-semibold">Summary</div>
                <div className="mt-2 text-sm text-slate-600">{summary}</div>
              </div>
              <div className="rounded-2xl border bg-white p-4">
                <div className="text-sm font-semibold">Detected Clauses</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {clauses.map((c, i) => <Badge key={i} tone="amber">{c}</Badge>)}
                </div>
              </div>
            </div>
          ) : null}

          <div className="text-xs text-slate-500">
            To make this production-grade, connect an LLM API route, add file uploads (PDF/DOCX), and store results in a DB.
          </div>
        </div>
      </Card>
    </div>
  );
}
