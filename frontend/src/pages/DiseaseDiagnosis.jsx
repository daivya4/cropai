import React, { useState } from 'react';
import { Upload, Scan, AlertCircle, Shield, Eye, X } from 'lucide-react';
import { api } from '../api/client';
import FarmerSummary from '../components/FarmerSummary';

function MetricPill({ label, value, sub }) {
  return (
    <div className="glass-card" style={{ padding: '20px 24px' }}>
      <div style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 6, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
        {label}
      </div>
      <div style={{ fontSize: 22, fontWeight: 800, color: '#fff', lineHeight: 1.1 }}>{value}</div>
      {sub && (
        <div className="metric-badge" style={{ marginTop: 8 }}>{sub}</div>
      )}
    </div>
  );
}

export function DiseaseDiagnosis() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (file) => {
    if (!file) return;
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Unsupported format. Please upload JPG, PNG, or WebP.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) handleFileChange(e.dataTransfer.files[0]);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.predictDisease(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Inference engine failure. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
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
            <Scan size={18} color="#4ade80" />
          </div>
          <span style={{ fontSize: 11, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.45)', fontFamily: 'ui-monospace, monospace', fontWeight: 600 }}>
            MODULE 01 / VISION MODEL
          </span>
        </div>
        <h1 style={{ fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 800, color: '#fff', margin: 0, lineHeight: 1.1, fontFamily: "'Playfair Display', serif" }}>
          Plant Disease Detection
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.55)', fontSize: 15, marginTop: 10, lineHeight: 1.6, maxWidth: 540 }}>
          Upload a leaf image for AI-powered pathology diagnosis with Grad-CAM visual explanation and uncertainty quantification.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 24 }}>
        {/* Upload panel */}
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ fontSize: 12, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.6)', marginBottom: 16, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
            INPUT LEAF IMAGE
          </div>

          <div
            className="upload-zone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => !previewUrl && document.getElementById('leaf-upload').click()}
          >
            <input
              id="leaf-upload"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
              style={{ display: 'none' }}
            />

            {previewUrl ? (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={(e) => { e.stopPropagation(); clearFile(); }}
                  style={{
                    position: 'absolute', top: -8, right: -8, zIndex: 2,
                    background: 'rgba(0,0,0,0.7)', border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '50%', width: 24, height: 24,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', color: '#fff',
                  }}
                >
                  <X size={12} />
                </button>
                <img
                  src={previewUrl}
                  alt="Selected leaf"
                  style={{ maxHeight: 220, borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)', objectFit: 'contain', display: 'block', margin: '0 auto' }}
                />
                <p style={{ marginTop: 10, fontSize: 11, color: 'rgba(255,255,255,0.4)', fontFamily: 'ui-monospace, monospace' }}>
                  {selectedFile?.name}
                </p>
              </div>
            ) : (
              <div style={{ padding: '20px 0' }}>
                <div style={{
                  width: 52, height: 52, borderRadius: '50%',
                  background: 'rgba(74,222,128,0.1)',
                  border: '1px solid rgba(74,222,128,0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px',
                }}>
                  <Upload size={22} color="#4ade80" />
                </div>
                <p style={{ fontSize: 13, color: '#fff', fontWeight: 600, marginBottom: 6 }}>
                  Drop leaf image here or click to browse
                </p>
                <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', fontFamily: 'ui-monospace, monospace' }}>
                  JPG · PNG · WEBP (max 5MB)
                </p>
              </div>
            )}
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
            onClick={handleAnalyze}
            disabled={!selectedFile || loading}
            className="btn-primary"
            style={{ width: '100%', marginTop: 16, borderRadius: 12 }}
          >
            {loading ? 'Analyzing…' : 'Run Diagnosis →'}
          </button>
        </div>

        {/* Results panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {result ? (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <MetricPill
                  label="DIAGNOSIS"
                  value={result.prediction.replace(/___/g, ' · ').replace(/_/g, ' ')}
                  sub="PATHOGEN"
                />
                <MetricPill
                  label="CONFIDENCE"
                  value={`${(result.confidence * 100).toFixed(1)}%`}
                  sub="CALIBRATED"
                />
              </div>

              <FarmerSummary
                type="disease"
                data={{ prediction: result.prediction, confidence: result.confidence }}
              />

              {/* Uncertainty */}
              <div className="glass-card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, color: '#fff' }}>
                    <Shield size={14} color="#4ade80" />
                    Predictive Uncertainty (MC Dropout)
                  </div>
                  <div className="metric-badge">{result.uncertainty.reliability.toUpperCase()}</div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {[
                    { label: 'Predictive Entropy', val: result.uncertainty.entropy.toFixed(4) },
                    { label: 'Normalized Entropy', val: result.uncertainty.normalized_entropy.toFixed(4) },
                  ].map(({ label, val }) => (
                    <div key={label} className="glass-card-inner" style={{ padding: '12px 14px' }}>
                      <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginBottom: 4, fontFamily: 'ui-monospace, monospace', letterSpacing: '0.06em' }}>{label.toUpperCase()}</div>
                      <div style={{ fontSize: 18, fontWeight: 700, color: '#4ade80' }}>{val}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Probability bars */}
              <div className="glass-card" style={{ padding: 20 }}>
                <div style={{ fontSize: 11, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.45)', marginBottom: 14, fontWeight: 600, fontFamily: 'ui-monospace, monospace' }}>
                  TOP PROBABILITY DISTRIBUTION
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {result.top_predictions.slice(0, 4).map((item, idx) => (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: idx === 0 ? '#fff' : 'rgba(255,255,255,0.6)', marginBottom: 5, fontWeight: idx === 0 ? 600 : 400 }}>
                        <span>{item.class.replace(/___/g, ' · ').replace(/_/g, ' ')}</span>
                        <span style={{ color: idx === 0 ? '#4ade80' : 'rgba(255,255,255,0.45)', fontFamily: 'ui-monospace, monospace' }}>{(item.probability * 100).toFixed(1)}%</span>
                      </div>
                      <div className="progress-track">
                        <div className="progress-fill" style={{ width: `${item.probability * 100}%`, opacity: idx === 0 ? 1 : 0.5 }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Grad-CAM */}
              {result.explanation?.overlay_base64 && (
                <div className="glass-card" style={{ padding: 20 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, color: '#fff', marginBottom: 14 }}>
                    <Eye size={14} color="#4ade80" />
                    Grad-CAM Visual Explanation
                  </div>
                  <img
                    src={`data:image/png;base64,${result.explanation.overlay_base64}`}
                    alt="Grad-CAM Overlay"
                    style={{ maxHeight: 260, borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)', objectFit: 'contain', display: 'block', margin: '0 auto', width: '100%' }}
                  />
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
                <Scan size={26} color="rgba(74,222,128,0.5)" />
              </div>
              <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 13, fontFamily: 'ui-monospace, monospace', letterSpacing: '0.06em' }}>
                AWAITING IMAGE INPUT
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DiseaseDiagnosis;
