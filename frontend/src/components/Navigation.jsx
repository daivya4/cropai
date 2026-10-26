import React from 'react';
import { LayoutDashboard, Scan, Sprout, TrendingUp } from 'lucide-react';

export function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'overview', label: 'OVERVIEW', icon: LayoutDashboard },
    { id: 'disease', label: 'DISEASE DIAGNOSIS', icon: Scan },
    { id: 'crop', label: 'CROP RECOMMENDATION', icon: Sprout },
    { id: 'yield', label: 'YIELD PREDICTION', icon: TrendingUp },
  ];

  return (
    <nav className="border-b border-[var(--border-card)] bg-[var(--bg-card)]/70 backdrop-blur transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-1 sm:space-x-4 overflow-x-auto py-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 text-xs font-mono-tech tracking-wider rounded transition-all duration-200 cursor-pointer ${
                  isActive
                    ? 'bg-[var(--text-primary)] text-[var(--bg-main)] font-semibold shadow-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-inner)]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
