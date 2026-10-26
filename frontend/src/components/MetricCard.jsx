import React from 'react';

export function MetricCard({ label, value, badge }) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-lg p-4 transition-all duration-300 hover:border-[var(--border-hover)]">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-mono-tech tracking-wider text-[var(--text-muted)] uppercase">
          {label}
        </span>
        {badge && (
          <span className="text-[10px] font-mono-tech px-2 py-0.5 rounded border border-[var(--badge-border)] bg-[var(--badge-bg)] text-[var(--badge-text)]">
            {badge}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold tracking-tight text-[var(--text-primary)] font-mono-tech my-1">
        {value}
      </div>
    </div>
  );
}

export default MetricCard;
