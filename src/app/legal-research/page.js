import { Card, CardHeader, Badge, Input, Button } from '../../components/ui';

export default function LegalResearchPage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader title="Legal Research" right={<Badge tone="green">Demo</Badge>} />
        <div className="p-5 space-y-4">
          <div className="text-sm text-slate-600">
            Placeholder research interface. In a full build, connect to a legal research data source (or your own knowledge base) and summarize authorities.
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_140px]">
            <Input placeholder="Search: e.g., whistleblower retaliation California" />
            <Button>Search</Button>
          </div>
          <div className="rounded-2xl border bg-slate-50 p-4 text-sm text-slate-600">
            Results will appear here. (Demo)
          </div>
        </div>
      </Card>
    </div>
  );
}
