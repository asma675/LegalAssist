'use client';

import { Card, CardHeader, Badge, Button } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';

function tone(p) {
  if (p === 'urgent') return 'red';
  if (p === 'high') return 'amber';
  if (p === 'medium') return 'violet';
  return 'slate';
}

function fmt(iso) {
  const d = new Date(iso);
  const opts = { month: 'short', day: 'numeric' };
  const date = d.toLocaleDateString(undefined, opts);
  const time = d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  return `${date}, ${time}`;
}

export default function TasksPage() {
  const { state, update } = useLocalState();
  const tasks = state.tasks ?? [];

  const overdue = tasks.filter(t => t.status === 'overdue');
  const active = tasks.filter(t => t.status !== 'done');
  const dueToday = tasks.filter(t => isToday(t.dueAt));

  const markDone = (id) => {
    update(s => {
      const idx = s.tasks.findIndex(t => t.id === id);
      if (idx >= 0) s.tasks[idx].status = 'done';
      return s;
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Tasks" />
        <div className="grid grid-cols-3 gap-4 px-5 py-6">
          <div className="text-center">
            <div className="text-3xl font-semibold">{active.length}</div>
            <div className="text-sm text-slate-500">Active</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-semibold">{dueToday.length}</div>
            <div className="text-sm text-slate-500">Due Today</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-semibold text-red-600">{overdue.length}</div>
            <div className="text-sm text-slate-500">Overdue</div>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader title={`Overdue (${overdue.length})`} />
        <div className="divide-y">
          {overdue.map(t => (
            <div key={t.id} className="px-5 py-4">
              <div className="flex items-start gap-3">
                <div className="mt-1 h-5 w-5 rounded-full border"></div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="font-semibold">{t.title}</div>
                    <Badge tone={tone(t.priority)}>{t.priority}</Badge>
                    <Badge tone="slate">{t.tag}</Badge>
                  </div>
                  <div className="mt-1 text-sm text-slate-500">{t.description}</div>
                  <div className="mt-2 text-sm text-red-600">Overdue — {fmt(t.dueAt)}</div>
                </div>
                <Button variant="subtle" onClick={() => markDone(t.id)}>Mark done</Button>
              </div>
            </div>
          ))}
          {!overdue.length ? <div className="px-5 py-6 text-sm text-slate-500">Nothing overdue 🎉</div> : null}
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
