export function Card({ children, className = '' }) {
  return <div className={['rounded-2xl border bg-white shadow-soft', className].join(' ')}>{children}</div>;
}
export function CardHeader({ title, right }) {
  return (
    <div className="flex items-center justify-between border-b px-5 py-4">
      <div className="text-lg font-semibold text-slate-900">{title}</div>
      {right ? <div>{right}</div> : null}
    </div>
  );
}
export function Badge({ children, tone = 'slate' }) {
  const tones = {
    slate: 'bg-slate-100 text-slate-700',
    violet: 'bg-violet-100 text-violet-700',
    green: 'bg-emerald-100 text-emerald-700',
    amber: 'bg-amber-100 text-amber-700',
    red: 'bg-red-100 text-red-700'
  };
  return <span className={['inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium', tones[tone] || tones.slate].join(' ')}>{children}</span>;
}
export function Button({ children, className = '', variant = 'primary', ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition';
  const variants = {
    primary: 'bg-violet-700 text-white hover:bg-violet-800',
    subtle: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
    outline: 'border bg-white text-slate-900 hover:bg-slate-50',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  return <button className={[base, variants[variant] || variants.primary, className].join(' ')} {...props}>{children}</button>;
}
export function Input({ className = '', ...props }) {
  return <input className={['w-full rounded-xl border bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-violet-300', className].join(' ')} {...props} />;
}
export function Select({ className = '', children, ...props }) {
  return <select className={['w-full rounded-xl border bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-violet-300', className].join(' ')} {...props}>{children}</select>;
}
export function Textarea({ className = '', ...props }) {
  return <textarea className={['w-full rounded-xl border bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-violet-300', className].join(' ')} {...props} />;
}
