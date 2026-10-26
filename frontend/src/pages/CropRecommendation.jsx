import React, { useEffect, useState } from 'react';
import { Sprout, AlertCircle, MapPin, CloudSun, LoaderCircle } from 'lucide-react';
import { api } from '../api/client';
import FarmerSummary from '../components/FarmerSummary';

function SliderField({ label, min, max, step = 1, value, onChange, unit = '' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600 }}>
          {label}
        </label>
        <span style={{ fontSize: 12, color: '#4ade80', fontWeight: 700, fontFamily: 'ui-monospace, monospace' }}>
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}

export function CropRecommendation() {
  const [params, setParams] = useState({
    state: 'Karnataka',
    district: 'Bangalore',
    year: 2017,
    top_k: 5,
    nitrogen: 50,
    phosphorus: 50,
    potassium: 50,
    temperature: 25,
    humidity: 75,
    ph: 6.5,
    rainfall: 120,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [locations, setLocations] = useState({});
  const [locationsLoading, setLocationsLoading] = useState(true);

  useEffect(() => {
    api.getIndianCropLocations()
      .then((availableLocations) => {
        setLocations(availableLocations);
        const states = Object.keys(availableLocations);
        const initialState = states.includes(params.state) ? params.state : states[0];
        const districts = availableLocations[initialState] || [];
        updateParam('state', initialState);
        updateParam('district', districts[0] || '');
      })
      .catch(() => setError('Location data unavailable.'))
      .finally(() => setLocationsLoading(false));
  }, []);

  const states = Object.keys(locations);
  const districts = locations[params.state] || [];

  const handleStateChange = (state) => {
    updateParam('state', state);
    updateParam('district', (locations[state] || [])[0] || '');
    setWeather(null);
    setWeatherError(null);
    setResult(null);
  };

  const updateParam = (key, value) =>
    setParams((prev) => ({ ...prev, [key]: value }));

  const handleDistrictChange = (district) => {
    updateParam('district', district);
    setWeather(null);
    setWeatherError(null);
  };

  const handleFetchWeather = async () => {
    setWeatherLoading(true);
    setWeatherError(null);
    try {
      const current = await api.getCurrentCropWeather({
        district: params.district,
        state: params.state,
      });
      setParams((prev) => ({
        ...prev,
        temperature: current.temperature_c,
        humidity: current.relative_humidity_percent,
      }));
      setWeather(current);
    } catch (err) {
      setWeatherError(err.response?.data?.detail || 'Could not fetch current weather.');
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleRecommend = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.recommendIndianCrop(params));
    } catch (err) {
      setError(err.response?.data?.detail || 'Recommendation engine failure.');
    } finally {
      setLoading(false);
    }
  };

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
            <MapPin size={18} color="#4ade80" />
          </div>
          <span style={{ fontSize: 11, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.45)', fontFamily: 'ui-monospace, monospace', fontWeight: 600 }}>
            MODULE 02 / INDIAN CROP SUITABILITY RANKER
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 800, color: '#fff', margin: 0, lineHeight: 1.1, fontFamily: "'Playfair Display', serif" }}>
          Crop Recommendation Engine
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 15, marginTop: 10, lineHeight: 1.6, maxWidth: 540 }}>
          Get AI-powered crop suitability rankings based on Indian district history, soil chemistry, and climatic signals.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, alignItems: 'start' }}>
        {/* Input panel */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.6)', marginBottom: 16, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
            LOCATION & SOIL / CLIMATE
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* State */}
            <div>
              <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600, display: 'block', marginBottom: 6 }}>
                STATE
              </label>
              <select
                value={params.state}
                onChange={(e) => handleStateChange(e.target.value)}
                disabled={locationsLoading || states.length === 0}
                className="input-field"
              >
                {locationsLoading && <option>Loading states…</option>}
                {states.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            {/* District */}
            <div>
              <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600, display: 'block', marginBottom: 6 }}>
                DISTRICT
              </label>
              <select
                value={params.district}
                onChange={(e) => handleDistrictChange(e.target.value)}
                disabled={locationsLoading || districts.length === 0}
                className="input-field"
              >
                {locationsLoading && <option>Loading districts…</option>}
                {districts.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>

            <div>
              <button
                type="button"
                onClick={handleFetchWeather}
                disabled={weatherLoading || locationsLoading || !params.district}
                className="weather-fetch-button"
                aria-live="polite"
              >
                {weatherLoading
                  ? <LoaderCircle className="weather-fetch-icon weather-fetch-icon-loading" size={18} />
                  : <CloudSun className="weather-fetch-icon" size={18} />}
                <span>{weatherLoading ? 'Fetching weather…' : 'Use Current Weather'}</span>
              </button>
              {weather && (
                <div className="weather-result" aria-live="polite">
                  <div className="weather-result-heading">
                    <MapPin size={14} />
                    <span>{weather.location}</span>
                    <span className="weather-live-badge">LIVE</span>
                  </div>
                  <div className="weather-metrics">
                    <div className="weather-metric">
                      <span className="weather-metric-label">Temperature</span>
                      <strong>{weather.temperature_c}°C</strong>
                    </div>
                    <div className="weather-metric">
                      <span className="weather-metric-label">Humidity</span>
                      <strong>{weather.relative_humidity_percent}%</strong>
                    </div>
                  </div>
                  <div className="weather-result-source">
                    {weather.source} · {weather.observed_at} ({weather.timezone})
                  </div>
                </div>
              )}
              {weatherError && (
                <div className="weather-error" role="alert">
                  {weatherError}
                </div>
              )}
              <div className="weather-help">
                Fetches current temperature and humidity for this district. Soil values and rainfall remain editable; rainfall is not replaced with today’s weather.
              </div>
            </div>

            {/* Year */}
            <div>
              <label style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.08em', fontFamily: 'ui-monospace, monospace', fontWeight: 600, display: 'block', marginBottom: 6 }}>
                REFERENCE YEAR
              </label>
              <input
                type="number"
                min="2010"
                max="2035"
                value={params.year}
                onChange={(e) => updateParam('year', Number(e.target.value))}
                className="input-field"
              />
            </div>

            {/* Soil divider */}
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 14 }}>
              <div style={{ fontSize: 11, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.45)', fontFamily: 'ui-monospace, monospace', fontWeight: 600, marginBottom: 14 }}>
                SOIL & CLIMATIC SIGNALS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <SliderField label="NITROGEN (N)" min={0} max={140} value={params.nitrogen} onChange={(v) => updateParam('nitrogen', v)} unit=" mg/kg" />
                <SliderField label="PHOSPHORUS (P)" min={5} max={145} value={params.phosphorus} onChange={(v) => updateParam('phosphorus', v)} unit=" mg/kg" />
                <SliderField label="POTASSIUM (K)" min={5} max={205} value={params.potassium} onChange={(v) => updateParam('potassium', v)} unit=" mg/kg" />
                <SliderField label="TEMPERATURE" min={-10} max={60} step={0.5} value={params.temperature} onChange={(v) => updateParam('temperature', v)} unit="°C" />
                <SliderField label="HUMIDITY" min={0} max={100} value={params.humidity} onChange={(v) => updateParam('humidity', v)} unit="%" />
                <SliderField label="SOIL pH" min={3.5} max={10} step={0.1} value={params.ph} onChange={(v) => updateParam('ph', v)} />
                <SliderField label="RAINFALL" min={20} max={300} value={params.rainfall} onChange={(v) => updateParam('rainfall', v)} unit=" mm" />
              </div>
            </div>
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
            onClick={handleRecommend}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', marginTop: 20, borderRadius: 12 }}
          >
            {loading ? 'Ranking Crops…' : 'Recommend Crops →'}
          </button>

          {/* Stats footer */}
          <div style={{ marginTop: 14, padding: '12px 14px', background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.12)', borderRadius: 10 }}>
            <div style={{ fontSize: 11, color: '#4ade80', fontFamily: 'ui-monospace, monospace', letterSpacing: '0.06em', marginBottom: 4, fontWeight: 600 }}>MODEL STATS</div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>Accuracy: <strong style={{ color: '#fff' }}>100.0%</strong> · Records: <strong style={{ color: '#fff' }}>27,676</strong></div>
          </div>
        </div>

        {/* Results panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {result ? (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="glass-card" style={{ padding: '20px 24px' }}>
                  <div style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 6, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                    TOP RECOMMENDATION
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: '#4ade80', lineHeight: 1.1, textTransform: 'capitalize' }}>
                    {result.recommended_crop}
                  </div>
                  <div className="metric-badge" style={{ marginTop: 8 }}>TOP CHOICE</div>
                </div>
                <div className="glass-card" style={{ padding: '20px 24px' }}>
                  <div style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 6, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                    LOCATION
                  </div>
                  <div style={{ fontSize: 18, fontWeight: 800, color: '#fff', lineHeight: 1.2, textTransform: 'capitalize' }}>
                    {result.district}
                  </div>
                  <div className="metric-badge" style={{ marginTop: 8 }}>{result.state.toUpperCase()}</div>
                </div>
              </div>

              <FarmerSummary
                type="crop"
                data={{
                  recommendedCrop: result.recommended_crop,
                  district: result.district,
                  state: result.state,
                  usesSoilWeather: result.data_source.includes('soil_weather'),
                }}
              />

              <div className="glass-card" style={{ padding: 20 }}>
                <div style={{ fontSize: 11, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 16, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                  TOP INDIAN CROP ALTERNATIVES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {result.top_recommendations.map((item, index) => (
                    <div
                      key={item.crop}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        padding: '10px 14px',
                        background: index === 0 ? 'rgba(74,222,128,0.08)' : 'rgba(255,255,255,0.03)',
                        border: `1px solid ${index === 0 ? 'rgba(74,222,128,0.2)' : 'rgba(255,255,255,0.07)'}`,
                        borderRadius: 10,
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div className="rank-circle">{String(index + 1).padStart(2, '0')}</div>
                        <span style={{ fontSize: 13, color: index === 0 ? '#fff' : 'rgba(255,255,255,0.7)', fontWeight: index === 0 ? 600 : 400, textTransform: 'capitalize' }}>
                          {item.crop}
                        </span>
                      </div>
                      <span style={{ fontSize: 12, color: index === 0 ? '#4ade80' : 'rgba(255,255,255,0.4)', fontFamily: 'ui-monospace, monospace', fontWeight: 600 }}>
                        {(item.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 12, fontSize: 11, color: 'rgba(255,255,255,0.3)', fontFamily: 'ui-monospace, monospace' }}>
                  SOURCE: {result.data_source} · {result.model_version}
                </div>
              </div>
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
                <Sprout size={26} color="rgba(74,222,128,0.5)" />
              </div>
              <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13, fontFamily: 'ui-monospace, monospace', letterSpacing: '0.06em' }}>
                SELECT STATE & DISTRICT TO BEGIN
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CropRecommendation;
