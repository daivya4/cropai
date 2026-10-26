import React from 'react';

export function MonochromeShapChart({ contributions, title = "FEATURE ATTRIBUTION (SHAP)" }) {
  if (!contributions || contributions.length === 0) {
    return (
      <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-lg p-6 text-center text-xs text-[var(--text-muted)] font-mono-tech">
        NO EXPLANATION DATA AVAILABLE
      </div>
    );
  }

  const maxAbsVal = Math.max(...contributions.map((c) => Math.abs(c.shap_value)), 0.0001);

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-lg p-5 transition-colors duration-300">
      <div className="flex items-center justify-between mb-4 border-b border-[var(--border-card)] pb-3">
        <span className="text-xs font-mono-tech tracking-wider text-[var(--text-primary)] uppercase">
          {title}
        </span>
        <span className="text-[10px] font-mono-tech text-[var(--text-muted)]">
          POSITIVE (SOLID) / NEGATIVE (BORDERED)
        </span>
      </div>

      <div className="space-y-3 font-mono-tech text-xs">
        {contributions.map((item, idx) => {
          const val = item.shap_value;
          const isPositive = val >= 0;
          const widthPct = Math.min(100, Math.max(4, (Math.abs(val) / maxAbsVal) * 100));

          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-[var(--text-primary)] font-medium">
                  {item.feature}
                  {item.value !== undefined && (
                    <span className="text-[var(--text-muted)] text-[10px] ml-2">
                      [{item.value}]
                    </span>
                  )}
                </span>
                <span className="text-[var(--text-muted)] font-mono">
                  {isPositive ? `+${val.toFixed(4)}` : val.toFixed(4)}
                </span>
              </div>

              {/* Bar visualization */}
              <div className="h-2 bg-[var(--bar-track)] rounded-sm overflow-hidden flex items-center relative">
                <div
                  style={{ width: `${widthPct}%` }}
                  className={`h-full rounded-sm transition-all duration-300 ${
                    isPositive
                      ? 'bg-[var(--bar-bg)]'
                      : 'bg-[var(--text-dim)] border border-[var(--border-hover)]'
                  }`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default MonochromeShapChart;
