'use client';

import { useMemo, useState } from 'react';
import { Card, CardHeader, Button, Badge } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';

function startOfMonth(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }
function endOfMonth(d) { return new Date(d.getFullYear(), d.getMonth() + 1, 0); }
function addMonths(d, n) { return new Date(d.getFullYear(), d.getMonth() + n, 1); }

export default function CalendarPage() {
  const { state } = useLocalState();
  const [cursor, setCursor] = useState(() => new Date());
  const events = state.events ?? [];

  const days = useMemo(() => {
    const start = startOfMonth(cursor);
    const end = endOfMonth(cursor);
    const firstDow = (start.getDay() + 6) % 7; // Monday=0
    const total = firstDow + end.getDate();
    const rows = Math.ceil(total / 7);
    const out = [];
    for (let i = 0; i < rows * 7; i++) {
      const dayNum = i - firstDow + 1;
      const date = new Date(cursor.getFullYear(), cursor.getMonth(), dayNum);
      out.push(date);
    }
    return out;
  }, [cursor]);

  const title = cursor.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title="Calendar"
          right={
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setCursor(addMonths(cursor, -1))}>←</Button>
              <div className="min-w-[160px] text-center text-sm font-medium">{title}</div>
              <Button variant="outline" onClick={() => setCursor(addMonths(cursor, 1))}>→</Button>
            </div>
          }
        />
        <div className="p-5">
          <div className="grid grid-cols-7 gap-2 text-xs text-slate-500">
            {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d => <div key={d} className="px-2">{d}</div>)}
          </div>

          <div className="mt-2 grid grid-cols-7 gap-2">
            {days.map((d, idx) => {
              const inMonth = d.getMonth() === cursor.getMonth();
              const iso = d.toISOString().slice(0,10);
              const eCount = events.filter(e => (e.date || '').slice(0,10) === iso).length;
              return (
                <div key={idx} className={['min-h-[86px] rounded-xl border p-2', inMonth ? 'bg-white' : 'bg-slate-50 text-slate-400'].join(' ')}>
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">{d.getDate()}</div>
                    {eCount ? <Badge tone="violet">{eCount}</Badge> : null}
                  </div>
                  <div className="mt-2 space-y-1 text-xs text-slate-600">
                    {(events.filter(e => (e.date || '').slice(0,10) === iso).slice(0,2)).map(e => (
                      <div key={e.id} className="truncate">• {e.title}</div>
                    ))}
                    {eCount > 2 ? <div className="text-slate-400">+{eCount-2} more</div> : null}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 text-sm text-slate-500">
            Tip: add real events later by extending the LocalStorage state. This is a demo calendar view.
          </div>
        </div>
      </Card>
    </div>
  );
}
