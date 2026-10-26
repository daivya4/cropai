import React from 'react';

export function SliderInput({ label, min, max, step = 1, value, onChange, unit = "" }) {
  return (
    <div className="bg-[var(--bg-inner)] border border-[var(--border-card)] rounded-lg p-2.5 space-y-1.5 transition-colors duration-300">
      <div className="flex items-center justify-between text-xs font-mono-tech">
        <span className="text-[var(--text-primary)] font-medium">{label}</span>
        <span className="text-[var(--text-primary)] font-bold bg-[var(--bg-card)] border border-[var(--border-card)] px-2 py-0.5 rounded text-[11px]">
          {value} {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-[var(--bar-track)] rounded-lg appearance-none cursor-pointer accent-[var(--text-primary)]"
      />
      <div className="flex justify-between text-[10px] text-[var(--text-muted)] font-mono-tech">
        <span>MIN: {min}</span>
        <span>MAX: {max}</span>
      </div>
    </div>
  );
}

export default SliderInput;
