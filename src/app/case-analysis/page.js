import { Card, CardHeader, Badge } from '../../components/ui';

export default function CaseAnalysisPage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Case Analysis" right={<Badge tone="amber">Demo</Badge>} />
        <div className="p-5 space-y-3 text-sm text-slate-600">
          <p>This is a placeholder for AI-powered case strategy (facts → issues → risks → next actions).</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Capture case facts and timeline</li>
            <li>Generate issue spotting + risk classification</li>
            <li>Suggest discovery plan and next steps</li>
          </ul>
          <p className="text-xs text-slate-500">You can wire this to an API route later. This build focuses on the LocalStorage demo foundation.</p>
        </div>
      </Card>
    </div>
  );
}
