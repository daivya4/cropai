import React from 'react';
import MetricCard from '../components/MetricCard';
import { Scan, Sprout, TrendingUp, Cpu } from 'lucide-react';

export function OverviewDashboard({ setActiveTab }) {
  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-xl p-6 sm:p-8 transition-colors duration-300">
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded bg-[var(--bg-inner)] border border-[var(--border-card)] text-[11px] font-mono-tech text-[var(--text-muted)]">
            <Cpu className="w-3.5 h-3.5" />
            <span>AGRICULTURAL DECISION-SUPPORT ENGINE</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-[var(--text-primary)] font-mono-tech">
            CROP.AI TECHNICAL PLATFORM
          </h1>
        </div>
      </div>

      {/* System Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          label="DISEASE DIAGNOSIS"
          value="99.17%"
          badge="MODEL 2"
        />
        <MetricCard
          label="YIELD PREDICTION R²"
          value="0.9469"
          badge="MODEL 3"
        />
        <MetricCard
          label="CROP RECOMMENDATION ACCURACY"
          value="100.0%"
          badge="TEST SET"
        />
      </div>

      {/* Module Launch Cards (Action Buttons with 0.5s inverting hover effect) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Disease Card */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-xl p-6 flex flex-col justify-between hover:border-[var(--border-hover)] transition-all duration-300">
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-lg bg-[var(--bg-inner)] border border-[var(--border-card)] flex items-center justify-center text-[var(--text-primary)]">
              <Scan className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[var(--text-primary)] font-mono-tech">DISEASE DIAGNOSIS</h3>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('disease')}
            className="mt-6 w-full btn-invert font-mono-tech text-xs font-semibold py-3 rounded tracking-wider cursor-pointer"
          >
            RUN DIAGNOSIS &rarr;
          </button>
        </div>

        {/* Crop Recommendation Card */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-xl p-6 flex flex-col justify-between hover:border-[var(--border-hover)] transition-all duration-300">
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-lg bg-[var(--bg-inner)] border border-[var(--border-card)] flex items-center justify-center text-[var(--text-primary)]">
              <Sprout className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[var(--text-primary)] font-mono-tech">CROP RECOMMENDATION</h3>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('crop')}
            className="mt-6 w-full btn-invert font-mono-tech text-xs font-semibold py-3 rounded tracking-wider cursor-pointer"
          >
            RECOMMEND CROP &rarr;
          </button>
        </div>

        {/* Yield Prediction Card */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-card)] rounded-xl p-6 flex flex-col justify-between hover:border-[var(--border-hover)] transition-all duration-300">
          <div className="space-y-4">
            <div className="w-10 h-10 rounded-lg bg-[var(--bg-inner)] border border-[var(--border-card)] flex items-center justify-center text-[var(--text-primary)]">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[var(--text-primary)] font-mono-tech">YIELD PREDICTION</h3>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('yield')}
            className="mt-6 w-full btn-invert font-mono-tech text-xs font-semibold py-3 rounded tracking-wider cursor-pointer"
          >
            PREDICT YIELD &rarr;
          </button>
        </div>
      </div>
    </div>
  );
}

export default OverviewDashboard;
