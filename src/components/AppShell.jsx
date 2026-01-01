'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useMemo, useState } from 'react';

const NAV = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/documents', label: 'Documents' },
  { href: '/document-generator', label: 'Document Generator' },
  { href: '/document-analyzer', label: 'Document Analyzer' },
  { href: '/tasks', label: 'Tasks' },
  { href: '/calendar', label: 'Calendar' },
  { href: '/case-analysis', label: 'Case Analysis' },
  { href: '/legal-research', label: 'Legal Research' },
  { href: '/settings', label: 'Settings' }
];

function NavItem({ href, label, active, onClick }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={[
        'block rounded-xl px-3 py-2 text-sm transition',
        active ? 'bg-violet-600 text-white shadow-soft' : 'text-slate-700 hover:bg-violet-50'
      ].join(' ')}
    >
      {label}
    </Link>
  );
}

export default function AppShell({ children }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const activeHref = useMemo(() => {
    const hit = NAV.find(n => pathname === n.href || pathname?.startsWith(n.href + '/'));
    return hit?.href ?? '/dashboard';
  }, [pathname]);

  return (
    <div className="min-h-screen bg-texture">
      <div className="sticky top-0 z-20 border-b bg-white/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3">
          <button
            onClick={() => setOpen(v => !v)}
            className="rounded-lg border px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 md:hidden"
            aria-label="Toggle navigation"
          >
            ☰
          </button>
          <div className="text-base font-semibold text-slate-900">LegalAssist</div>
          <div className="ml-auto text-sm text-slate-500">AI Legal Platform</div>
        </div>
      </div>

      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-4 px-4 py-6 md:grid-cols-[240px_1fr]">
        <aside className="hidden md:block">
          <div className="rounded-2xl border bg-white p-3 shadow-soft">
            <div className="mb-3 rounded-2xl bg-gradient-to-br from-slate-950 via-violet-900 to-violet-700 p-4 text-white">
              <div className="text-sm opacity-80">AI-Powered Legal Platform</div>
              <div className="mt-1 text-xl font-semibold">Welcome back, Asma</div>
              <div className="mt-1 text-xs opacity-80">Generate documents, analyze cases, and streamline your workflow.</div>
            </div>

            <nav className="space-y-1">
              {NAV.map(item => (
                <NavItem key={item.href} {...item} active={activeHref === item.href} />
              ))}
            </nav>
          </div>
        </aside>

        {open ? (
          <div className="md:hidden">
            <div className="rounded-2xl border bg-white p-3 shadow-soft">
              <nav className="space-y-1">
                {NAV.map(item => (
                  <NavItem
                    key={item.href}
                    {...item}
                    active={activeHref === item.href}
                    onClick={() => setOpen(false)}
                  />
                ))}
              </nav>
            </div>
          </div>
        ) : null}

        <main className="min-w-0">{children}</main>
      </div>
    </div>
  );
}
