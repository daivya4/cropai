import React, { useState } from 'react';
import { TrendingUp, AlertCircle, ShieldAlert } from 'lucide-react';
import { api } from '../api/client';
import FarmerSummary from '../components/FarmerSummary';

const STATES = [
  'Punjab', 'Maharashtra', 'Uttar Pradesh', 'Tamil Nadu', 'West Bengal',
  'Karnataka', 'Gujarat', 'Madhya Pradesh', 'Andhra Pradesh', 'Haryana',
  'Bihar', 'Odisha', 'Rajasthan', 'Kerala', 'Assam',
];

const CROPS = [
  'Rice', 'Maize', 'Chickpea', 'Cotton', 'Mango', 'Banana', 'Grapes', 'Wheat', 'Sugarcane', 'Arhar/Tur',
];

const SEASONS = ['Kharif     ', 'Rabi   ', 'Summer', 'Whole Year', 'Winter', 'Autumn'];
const CONFIDENCE_OPTS = [
  { value: 0.90, label: '90% Range (Recommended)' },
  { value: 0.95, label: '95% Range' },
  { value: 0.80, label: '80% Range' },
];

function SelectField({ label, options, value, onChange }) {
  return (
    <div>
      <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600, display: 'block', marginBottom: 6 }}>
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input-field"
      >
        {options.map((opt) => {
          const v = typeof opt === 'object' ? opt.value : opt;
          const l = typeof opt === 'object' ? opt.label : opt;
          return <option key={v} value={v}>{l}</option>;
        })}
      </select>
    </div>
  );
}

/* SHAP bar chart row */
function ShapRow({ feature, value, maxAbs }) {
  const pct = Math.abs(value) / maxAbs * 100;
  const positive = value >= 0;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <div style={{ width: 150, fontSize: 11, color: 'rgba(255,255,255,0.6)', fontFamily: 'ui-monospace, monospace', textAlign: 'right', flexShrink: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {feature.replace(/crop_|state_|season_/g, '')}
      </div>
      <div style={{ flex: 1, height: 8, background: 'rgba(255,255,255,0.06)', borderRadius: 999, position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute',
          height: '100%',
          width: `${pct}%`,
          background: positive ? 'linear-gradient(90deg, #4ade80, #22c55e)' : 'linear-gradient(90deg, #f87171, #ef4444)',
          borderRadius: 999,
          transition: 'width 0.6s ease',
        }} />
      </div>
      <div style={{ width: 56, fontSize: 11, color: positive ? '#4ade80' : '#f87171', fontFamily: 'ui-monospace, monospace', textAlign: 'right', flexShrink: 0 }}>
        {value > 0 ? '+' : ''}{value.toFixed(3)}
      </div>
    </div>
  );
}

export function YieldPrediction() {
  const [state, setState] = useState('Punjab');
  const [crop, setCrop] = useState('Rice');
  const [season, setSeason] = useState('Kharif     ');
  const [area, setArea] = useState(1000.0);
  const [confLevel, setConfLevel] = useState(0.90);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.predictYield({ state, crop, season, area_hectares: area, confidence_level: confLevel });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Yield prediction failure. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /* Top SHAP features (non-zero, sorted by |value|) */
  const topShap = result?.explanation?.top_features
    ?.filter((f) => f.shap_value !== 0)
    .slice(0, 8) ?? [];
  const maxAbs = topShap.length ? Math.max(...topShap.map((f) => Math.abs(f.shap_value))) : 1;

  return (
    <div style={{ paddingTop: 16 }}>
      {/* Page header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'rgba(74,222,128,0.15)',
            border: '1px solid rgba(74,222,128,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <TrendingUp size={18} color="#4ade80" />
          </div>
          <span style={{ fontSize: 11, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.45)', fontFamily: 'ui-monospace, monospace', fontWeight: 600 }}>
            MODULE 03 / CONFORMAL REGRESSOR
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 800, color: '#fff', margin: 0, lineHeight: 1.1, fontFamily: "'Playfair Display', serif" }}>
          Yield Forecasting
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 15, marginTop: 10, lineHeight: 1.6, maxWidth: 540 }}>
          Estimate likely harvest per hectare and view a range for planning. Actual yield can change with weather, soil, and farming practices.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, alignItems: 'start' }}>
        {/* Input panel */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.6)', marginBottom: 16, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
            REGRESSION PARAMETERS
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <SelectField label="STATE LOCATION" options={STATES} value={state} onChange={setState} />
            <SelectField label="TARGET CROP" options={CROPS} value={crop} onChange={setCrop} />
            <SelectField label="CULTIVATION SEASON" options={SEASONS} value={season} onChange={setSeason} />

            <div>
              <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600, display: 'block', marginBottom: 6 }}>
                CULTIVATED AREA (HECTARES)
              </label>
              <input
                type="number"
                min={0.1}
                max={10000000}
                value={area}
                onChange={(e) => setArea(parseFloat(e.target.value) || 0)}
                className="input-field"
              />
            </div>

            <SelectField
              label="ESTIMATED RANGE"
              options={CONFIDENCE_OPTS}
              value={confLevel}
              onChange={(v) => setConfLevel(parseFloat(v))}
            />
          </div>

          {error && (
            <div style={{
              marginTop: 12, padding: '10px 14px', borderRadius: 10,
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
              display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#fca5a5',
            }}>
              <AlertCircle size={14} style={{ flexShrink: 0 }} />
              {error}
            </div>
          )}

          <button
            onClick={handlePredict}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', marginTop: 20, borderRadius: 12 }}
          >
            {loading ? 'Calculating…' : 'Predict Yield →'}
          </button>
        </div>

        {/* Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {result ? (
            <>
              {/* Metric cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="glass-card" style={{ padding: '20px 24px' }}>
                  <div style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 6, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>PREDICTED YIELD</div>
                  <div style={{ fontSize: 25, fontWeight: 800, color: '#4ade80', lineHeight: 1.2 }}>
                    {result.predicted_yield.toFixed(2)}
                  </div>
                  <div style={{ marginTop: 5, fontSize: 12, color: 'rgba(255,255,255,0.72)' }}>
                    tonnes/hectare (t/ha)
                  </div>
                  <div className="metric-badge" style={{ marginTop: 8 }}>ESTIMATED YIELD</div>
                </div>
                <div className="glass-card" style={{ padding: '20px 24px' }}>
                  <div style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 6, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                    {(result.interval.confidence_level * 100).toFixed(0)}% CONFORMAL BOUNDS
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#fff', lineHeight: 1.3 }}>
                    {result.interval.lower.toFixed(2)} – {result.interval.upper.toFixed(2)}
                  </div>
                  <div style={{ marginTop: 5, fontSize: 11, color: 'rgba(255,255,255,0.58)' }}>
                    tonnes/hectare (t/ha)
                  </div>
                  <div className="metric-badge" style={{ marginTop: 8 }}>
                    {result.interval.confidence_level * 100}% ESTIMATED RANGE
                  </div>
                </div>
              </div>

              <FarmerSummary
                type="yield"
                data={{
                  crop,
                  state,
                  season,
                  estimate: result.predicted_yield,
                  lower: result.interval.lower,
                  upper: result.interval.upper,
                  unit: result.unit,
                  confidence: result.interval.confidence_level,
                }}
              />

              {/* Guarantee card */}
              <div className="glass-card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 600, color: '#fff', marginBottom: 10 }}>
                  <ShieldAlert size={15} color="#4ade80" />
                  Estimated Yield Range
                </div>
                <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', lineHeight: 1.65, margin: 0 }}>
                  At the selected{' '}
                  <strong style={{ color: '#4ade80' }}>{(result.interval.confidence_level * 100).toFixed(0)}%</strong>
                  {' '}level, the model estimates yield may be between{' '}
                  <strong style={{ color: '#fff' }}>{result.interval.lower.toFixed(2)} and {result.interval.upper.toFixed(2)} {result.unit}</strong>.
                  {' '}This is an estimate, not a guarantee.
                </p>
              </div>

              {/* SHAP chart */}
              {topShap.length > 0 && (
                <div className="glass-card" style={{ padding: 20 }}>
                  <div style={{ fontSize: 11, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 16, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                    FEATURE INFLUENCE (SHAP) · {result.predicted_yield.toFixed(2)} T/HA
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {topShap.map((f) => (
                      <ShapRow key={f.feature} feature={f.feature} value={f.shap_value} maxAbs={maxAbs} />
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="glass-card" style={{ padding: 60, textAlign: 'center' }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                background: 'rgba(74,222,128,0.08)',
                border: '1px solid rgba(74,222,128,0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 16px',
              }}>
                <TrendingUp size={26} color="rgba(74,222,128,0.5)" />
              </div>
              <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13, fontFamily: 'ui-monospace, monospace', letterSpacing: '0.06em' }}>
                AWAITING REGRESSION PARAMETERS
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default YieldPrediction;
