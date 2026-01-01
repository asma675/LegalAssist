'use client';

import { Card, CardHeader, Button, Input, Badge } from '../../components/ui';
import { useLocalState } from '../../lib/useLocalState';

export default function SettingsPage() {
  const { state, update } = useLocalState();

  const setName = (name) => {
    update(s => { s.user.name = name; return s; });
  };

  const reset = () => {
    if (!confirm('Reset demo data?')) return;
    localStorage.removeItem('legalassist_v1');
    location.reload();
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Settings" right={<Badge tone="violet">LocalStorage</Badge>} />
        <div className="p-5 space-y-4">
          <div>
            <div className="mb-1 text-sm font-medium text-slate-700">Display Name</div>
            <Input value={state.user?.name || ''} onChange={e => setName(e.target.value)} />
            <div className="mt-1 text-xs text-slate-500">Stored locally in your browser.</div>
          </div>
          <div className="flex gap-2">
            <Button variant="danger" onClick={reset}>Reset Demo Data</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
