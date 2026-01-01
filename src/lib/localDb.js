const KEY = 'legalassist_v1';

function nowIso() {
  return new Date().toISOString();
}

export const seedState = {
  user: { name: 'Asma' },
  metrics: {
    totalDocuments: 5,
    caseAnalyses: 2,
    aiGenerations: 7,
    timeSavedHours: 14
  },
  documents: [
    { id: 'doc_contract_1', title: 'Contract', type: 'agreement', status: 'draft', client: 'Adam', createdAt: '2026-01-01', summary: 'Professional contract between Adam (Client) and another party.' },
    { id: 'doc_nda_1', title: 'Non-Disclosure Agreement - Tech Startup', type: 'nda', status: 'final', client: 'TechVenture Inc.', createdAt: '2026-01-01', summary: 'Mutual NDA for a technology startup collaboration.' },
    { id: 'doc_emp_1', title: 'Employment Contract - Senior Developer', type: 'contract', status: 'draft', client: 'Global Solutions Ltd.', createdAt: '2026-01-01', summary: 'Employment agreement for a senior developer role.' },
    { id: 'doc_priv_1', title: 'Privacy Policy - E-Commerce Platform', type: 'privacy_policy', status: 'review', client: 'ShopEasy Inc.', createdAt: '2026-01-01', summary: 'Privacy policy for an e-commerce platform.' }
  ],
  tasks: [
    { id: 't1', title: 'Review and finalize NDA for TechVenture Inc.', priority: 'high', tag: 'review', client: 'TechVenture Inc.', dueAt: '2025-12-20T17:00:00', status: 'overdue', description: 'Complete final review of non-disclosure agreement, ensure all terms are properly defined and update signature page.' },
    { id: 't2', title: 'Research case law for Johnson employment case', priority: 'urgent', tag: 'research', client: 'Robert Johnson', dueAt: '2025-12-21T12:00:00', status: 'overdue', description: 'Find precedents for wrongful termination based on whistleblower retaliation in California.' },
    { id: 't3', title: 'Prepare exhibits for court hearing', priority: 'urgent', tag: 'preparation', client: 'Robert Johnson', dueAt: '2025-12-21T18:00:00', status: 'overdue', description: 'Organize and label all exhibits for Johnson v. ABC Corp hearing on 12/22.' },
    { id: 't4', title: 'Draft motion to compel discovery', priority: 'high', tag: 'drafting', client: 'Smith Family', dueAt: '2025-12-22T16:00:00', status: 'overdue', description: 'Prepare motion to compel production of documents in Smith trust matter.' },
    { id: 't5', title: 'File petition with county clerk', priority: 'urgent', tag: 'filing', client: 'Robert Johnson', dueAt: '2025-12-23T17:00:00', status: 'overdue', description: 'Submit petition and confirm docketing with county clerk.' }
  ],
  events: []
};

export function loadState() {
  if (typeof window === 'undefined') return seedState;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) {
      window.localStorage.setItem(KEY, JSON.stringify(seedState));
      return seedState;
    }
    return JSON.parse(raw);
  } catch (e) {
    console.warn('Failed to load local state', e);
    return seedState;
  }
}

export function saveState(next) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(KEY, JSON.stringify(next));
}

export function updateState(mutator) {
  const current = loadState();
  const next = mutator(structuredClone(current));
  saveState(next);
  return next;
}

export function newId(prefix='id') {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return `${prefix}_${crypto.randomUUID()}`;
  return `${prefix}_${Math.random().toString(16).slice(2)}_${Date.now()}`;
}

export function generateDocumentBody({ docType, client, title, jurisdiction, notes }) {
  const header = `${title || docType.toUpperCase()}\nClient: ${client || ''}\nDate: ${new Date().toLocaleDateString()}\n`;
  const boiler = `\n---\nThis document was generated for demo purposes. Replace placeholders and have a licensed attorney review before use.\n`;
  const j = jurisdiction ? `\nJurisdiction: ${jurisdiction}` : '';
  const n = notes ? `\nNotes: ${notes}` : '';
  return header + j + n + boiler;
}

export async function aiSummarizeText(text) {
  // Optional: you can wire this to your own API route later.
  const lines = String(text || '').split(/\n+/).filter(Boolean);
  const take = lines.slice(0, 6).join(' ');
  return take.length ? take : 'No content provided.';
}
