import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b border-[var(--border-card)] bg-[var(--bg-main)]/90 backdrop-blur sticky top-0 z-50 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-[var(--text-primary)] text-[var(--bg-main)] flex items-center justify-center font-bold text-sm tracking-tighter transition-colors duration-300">
            CAI
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold tracking-tight text-[var(--text-primary)] text-base transition-colors duration-300">
                CROP.AI
              </span>
              <span className="text-[10px] font-mono-tech uppercase bg-[var(--bg-card)] border border-[var(--border-card)] px-1.5 py-0.5 rounded text-[var(--text-muted)] transition-colors duration-300">
                v2.0.0
              </span>
            </div>
            <p className="text-[11px] text-[var(--text-muted)] transition-colors duration-300">
              Decoupled ML Serving Platform
            </p>
          </div>
        </div>

        {/* Global Theme Toggle Button */}
        <div className="flex items-center">
          <button
            onClick={toggleTheme}
            aria-label="Toggle Global Theme"
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg border border-[var(--border-card)] bg-[var(--bg-card)] text-[var(--text-primary)] hover:border-[var(--border-hover)] text-xs font-mono-tech transition-all duration-300 cursor-pointer"
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-3.5 h-3.5" />
                <span>LIGHT MODE</span>
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5" />
                <span>DARK MODE</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
