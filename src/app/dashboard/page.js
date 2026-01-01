'use client';

import Link from 'next/link';
import { Card, Badge } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';

function Stat({ label, value, delta }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-3xl font-semibold">{value}</div>
          <div className="mt-1 text-sm text-slate-500">{label}</div>
        </div>
        {delta ? <Badge tone="green">{delta}</Badge> : null}
      </div>
    </Card>
  );
}

function QuickCard({ href, title, subtitle, tone }) {
  const iconBg = tone === 'violet' ? 'from-violet-500 to-fuchsia-500' :
                 tone === 'amber' ? 'from-amber-500 to-orange-500' :
                 tone === 'green' ? 'from-emerald-500 to-teal-500' : 'from-slate-500 to-slate-700';
  return (
    <Link href={href} className="block">
      <Card className="p-5 hover:shadow-lg transition">
        <div className="flex gap-4">
          <div className={['h-12 w-12 rounded-2xl bg-gradient-to-br', iconBg, 'flex items-center justify-center text-white text-xl'].join(' ')}>
            ✦
          </div>
          <div className="min-w-0">
            <div className="text-base font-semibold">{title}</div>
            <div className="mt-1 text-sm text-slate-500">{subtitle}</div>
          </div>
        </div>
      </Card>
    </Link>
  );
}

export default function DashboardPage() {
  const { state } = useLocalState();
  const docs = state.documents ?? [];
  const tasks = state.tasks ?? [];

  return (
    <div className="space-y-4">
      <div className="rounded-3xl bg-gradient-to-br from-slate-950 via-violet-900 to-violet-700 p-7 text-white shadow-soft">
        <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs">
          ✨ <span className="opacity-90">AI-Powered Legal Platform</span>
        </div>
        <div className="mt-4 text-4xl font-semibold">Welcome back, {state.user?.name || 'Asma'}</div>
        <div className="mt-2 max-w-2xl text-white/80">
          Your intelligent legal assistant is ready to help. Generate documents, analyze cases, and streamline your legal workflow.
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <QuickCard href="/document-generator" title="Generate Document" subtitle="Create contracts, agreements & more" tone="violet" />
        <QuickCard href="/document-analyzer" title="Analyze Document" subtitle="Upload & extract key clauses" tone="violet" />
        <QuickCard href="/case-analysis" title="Case Analysis" subtitle="AI-powered case strategy" tone="amber" />
        <QuickCard href="/legal-research" title="Legal Research" subtitle="Search legal precedents" tone="green" />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Stat label="Total Documents" value={state.metrics?.totalDocuments ?? docs.length} delta="+12%" />
        <Stat label="Case Analyses" value={state.metrics?.caseAnalyses ?? 2} delta="+8%" />
        <Stat label="AI Generations" value={state.metrics?.aiGenerations ?? 7} delta="+24%" />
        <Stat label="Time Saved" value={(state.metrics?.timeSavedHours ?? 14) + 'h'} delta="+15%" />
      </div>

      <Card className="">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <div className="text-lg font-semibold">Recent Documents</div>
          <Link className="text-sm text-violet-700 hover:underline" href="/documents">View all →</Link>
        </div>
        <div className="divide-y">
          {docs.slice(0, 4).map(d => (
            <Link key={d.id} href={`/documents/${d.id}`} className="flex items-center gap-3 px-5 py-4 hover:bg-slate-50">
              <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center">📄</div>
              <div className="min-w-0 flex-1">
                <div className="font-medium">{d.title}</div>
                <div className="text-sm text-slate-500">{d.type} • {d.createdAt}</div>
              </div>
              <div className="text-slate-400">›</div>
            </Link>
          ))}
          {!docs.length ? <div className="px-5 py-6 text-sm text-slate-500">No documents yet.</div> : null}
        </div>
      </Card>

      <Card className="">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <div className="text-lg font-semibold">Tasks Overview</div>
          <Link className="text-sm text-violet-700 hover:underline" href="/tasks">View all →</Link>
        </div>
        <div className="grid grid-cols-3 gap-4 px-5 py-6">
          <div className="text-center">
            <div className="text-3xl font-semibold">{tasks.filter(t => t.status !== 'done').length}</div>
            <div className="text-sm text-slate-500">Active</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-semibold">{tasks.filter(t => isToday(t.dueAt)).length}</div>
            <div className="text-sm text-slate-500">Due Today</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-semibold text-red-600">{tasks.filter(t => t.status === 'overdue').length}</div>
            <div className="text-sm text-slate-500">Overdue</div>
          </div>
        </div>
      </Card>
    </div>
  );
}

function isToday(iso) {
  if (!iso) return false;
  const d = new Date(iso);
  const n = new Date();
  return d.getFullYear() === n.getFullYear() && d.getMonth() === n.getMonth() && d.getDate() === n.getDate();
}
