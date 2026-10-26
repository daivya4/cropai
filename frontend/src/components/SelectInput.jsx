import React from 'react';

export function SelectInput({ label, options, value, onChange }) {
  return (
    <div className="bg-[var(--bg-inner)] border border-[var(--border-card)] rounded-lg p-2.5 space-y-1.5 transition-colors duration-300">
      <label className="block text-xs font-mono-tech text-[var(--text-primary)] font-medium">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-[var(--bg-card)] border border-[var(--border-card)] rounded px-3 py-1.5 text-xs font-mono-tech text-[var(--text-primary)] focus:outline-none focus:border-[var(--border-hover)] transition-colors duration-300 cursor-pointer"
      >
        {options.map((opt) => {
          const val = typeof opt === 'object' ? opt.value : opt;
          const lbl = typeof opt === 'object' ? opt.label : opt;
          return (
            <option key={val} value={val} className="bg-[var(--bg-card)] text-[var(--text-primary)]">
              {lbl}
            </option>
          );
        })}
      </select>
    </div>
  );
}

export default SelectInput;
