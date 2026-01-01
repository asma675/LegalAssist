'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, Button, Input, Select, Textarea, Badge } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';
import { generateDocumentBody, newId } from '../../lib/localDb';

const TYPES = [
  { key: 'contract', title: 'Contract', desc: 'Professional contract template' },
  { key: 'nda', title: 'NDA', desc: 'Non-disclosure agreement' },
  { key: 'agreement', title: 'Agreement', desc: 'General agreement document' },
  { key: 'legal_letter', title: 'Legal Letter', desc: 'Formal legal correspondence' },
  { key: 'privacy_policy', title: 'Privacy Policy', desc: 'Website privacy policy' },
  { key: 'terms', title: 'Terms of Service', desc: 'Website terms & conditions' }
];

export default function DocumentGeneratorPage() {
  const { update } = useLocalState();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [docType, setDocType] = useState('contract');
  const [title, setTitle] = useState('Employment Contract - Senior Developer');
  const [client, setClient] = useState('Global Solutions Ltd.');
  const [jurisdiction, setJurisdiction] = useState('California');
  const [notes, setNotes] = useState('Include confidentiality + IP assignment. Provide standard at-will language.');

  const selected = useMemo(() => TYPES.find(t => t.key === docType), [docType]);
  const preview = useMemo(() => generateDocumentBody({ docType, title, client, jurisdiction, notes }), [docType, title, client, jurisdiction, notes]);

  const create = () => {
    const id = newId('doc');
    update(s => {
      s.documents.unshift({
        id,
        title,
        type: docType,
        status: 'draft',
        client,
        createdAt: new Date().toISOString().slice(0,10),
        summary: (selected?.desc || 'Generated document') + ' (Local demo).',
        jurisdiction,
        notes,
        body: preview
      });
      s.metrics.totalDocuments = s.documents.length;
      s.metrics.aiGenerations = (s.metrics.aiGenerations || 0) + 1;
      s.metrics.timeSavedHours = (s.metrics.timeSavedHours || 0) + 1;
      return s;
    });
    router.push(`/documents/${id}`);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Document Generator" right={<Badge tone="violet">LocalStorage Demo</Badge>} />
        <div className="p-5">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Step active={step===1} label="Select Type" />
            <Dot />
            <Step active={step===2} label="Fill Details" />
            <Dot />
            <Step active={step===3} label="Generate" />
          </div>

          {step === 1 ? (
            <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              {TYPES.map(t => (
                <button
                  key={t.key}
                  onClick={() => setDocType(t.key)}
                  className={[
                    'text-left rounded-2xl border bg-white p-5 transition hover:shadow-lg',
                    t.key === docType ? 'border-violet-400 ring-2 ring-violet-200' : ''
                  ].join(' ')}
                >
                  <div className="text-base font-semibold">{t.title}</div>
                  <div className="mt-1 text-sm text-slate-500">{t.desc}</div>
                </button>
              ))}
              <div className="md:col-span-2 flex justify-end">
                <Button onClick={() => setStep(2)}>Continue →</Button>
              </div>
            </div>
          ) : null}

          {step === 2 ? (
            <div className="mt-5 space-y-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Field label="Document Type">
                  <Select value={docType} onChange={e => setDocType(e.target.value)}>
                    {TYPES.map(t => <option key={t.key} value={t.key}>{t.title}</option>)}
                  </Select>
                </Field>
                <Field label="Jurisdiction">
                  <Input value={jurisdiction} onChange={e => setJurisdiction(e.target.value)} placeholder="e.g., California" />
                </Field>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <Field label="Document Title">
                  <Input value={title} onChange={e => setTitle(e.target.value)} />
                </Field>
                <Field label="Client / Party">
                  <Input value={client} onChange={e => setClient(e.target.value)} />
                </Field>
              </div>

              <Field label="Notes / Requirements">
                <Textarea rows={4} value={notes} onChange={e => setNotes(e.target.value)} />
              </Field>

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)}>← Back</Button>
                <Button onClick={() => setStep(3)}>Continue →</Button>
              </div>
            </div>
          ) : null}

          {step === 3 ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-2xl border bg-slate-50 p-4">
                <div className="text-sm font-medium text-slate-900">Preview</div>
                <pre className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{preview}</pre>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <Button variant="outline" onClick={() => setStep(2)}>← Back</Button>
                <Button onClick={create}>Generate Document</Button>
              </div>
              <div className="text-xs text-slate-500">
                Demo disclaimer: content is placeholder text generated locally. For real use, connect an API + attorney review.
              </div>
            </div>
          ) : null}
        </div>
      </Card>
    </div>
  );
}

function Step({ active, label }) {
  return <span className={['rounded-full px-3 py-1', active ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-slate-600'].join(' ')}>{label}</span>;
}
function Dot(){ return <span className="text-slate-400">•</span>; }
function Field({ label, children }) {
  return (
    <div>
      <div className="mb-1 text-sm font-medium text-slate-700">{label}</div>
      {children}
    </div>
  );
}
