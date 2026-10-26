import React, { useState, useRef, useEffect } from 'react';
import homepageBg from './assets/homepage.png';
import DiseaseDiagnosis from './pages/DiseaseDiagnosis';
import CropRecommendation from './pages/CropRecommendation';
import YieldPrediction from './pages/YieldPrediction';
import { Home, Scan, Sprout, TrendingUp, Leaf } from 'lucide-react';

/* ── Navigation items ── */
const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'disease', label: 'Disease Detection', icon: Scan },
  { id: 'crop', label: 'Crop Recommendation', icon: Sprout },
  { id: 'yield', label: 'Yield Prediction', icon: TrendingUp },
];

/* ── Floating centered navbar ── */
function Navbar({ activePage, onNavigate }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <header
      className="fixed top-5 left-0 right-0 z-50 flex justify-center px-4 transition-all duration-300"
    >
      <nav
        className="glass-nav"
        style={{
          background: scrolled
            ? 'rgba(0,0,0,0.55)'
            : 'rgba(0,0,0,0.25)',
        }}
      >
        {/* Logo pill */}
        <div className="flex items-center gap-2 px-3 mr-2 select-none">
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'linear-gradient(135deg, #4ade80, #22c55e)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Leaf size={14} color="#052e0f" strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: 13, fontWeight: 700, color: '#fff', letterSpacing: '-0.01em' }}>
            CropAI
          </span>
        </div>

        {/* Nav buttons */}
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`nav-btn ${activePage === id ? 'active' : ''}`}
            onClick={() => onNavigate(id)}
          >
            {label}
          </button>
        ))}
      </nav>
    </header>
  );
}

/* ── Hero homepage ── */
function HeroPage({ onNavigate }) {
  return (
    <section className="hero-section">
      {/* Background image */}
      <div
        className="hero-bg"
        style={{ backgroundImage: `url(${homepageBg})` }}
      />
      {/* Gradient overlay */}
      <div className="hero-overlay" />

      {/* Content */}
      <div className="hero-content">
        {/* Spacer to push content below nav */}
        <div style={{ flex: '0 0 auto', height: '120px' }} />

        {/* Middle – title + summary */}
        <div
          style={{
            flex: '1 1 auto',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            padding: '0 24px',
          }}
        >
          {/* Badge
          <div className="tag-pill fade-in" style={{ marginBottom: 24, animationDelay: '0.1s' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ade80', flexShrink: 0 }} />
            Agricultural AI Decision Support · v2.0
          </div> */}

          {/* Main title */}
          <h1
            className="font-display fade-in green-glow"
            style={{
              fontSize: 'clamp(48px, 8vw, 92px)',
              fontWeight: 800,
              lineHeight: 1.05,
              color: '#ffffff',
              marginBottom: 24,
              maxWidth: 900,
              animationDelay: '0.2s',
            }}
          >
            Intelligent Farming,{' '}
            <span style={{ color: '#4ade80' }}>Crop AI</span>
          </h1>

          {/* Summary */}
          <p
            className="fade-in"
            style={{
              fontSize: 'clamp(15px, 2vw, 19px)',
              color: 'rgba(255,255,255,0.72)',
              lineHeight: 1.7,
              maxWidth: 640,
              marginBottom: 40,
              fontWeight: 400,
              animationDelay: '0.3s',
            }}
          >
            CropAI is an explainable, uncertainty-aware agricultural decision support
            system, empowering farmers with AI-driven disease detection, crop
            recommendations, and yield forecasting with calibrated confidence.
          </p>


        </div>

        {/* Bottom – creator names + scroll indicator */}
        <div
          style={{
            flex: '0 0 auto',
            paddingBottom: 32,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 20,
          }}
        >
          {/* Creator info */}
          <div
            style={{
              background: 'rgba(0,0,0,0.35)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 999,
              padding: '10px 28px',
              display: 'flex',
              alignItems: 'center',
              gap: 20,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)', letterSpacing: '0.1em', fontWeight: 500 }}>
              CREATED BY
            </span>
            {[
              'Bhavya Makadia',
              'Bramha Bajannavar',
              'Daivya Shah',
              'Hitesh Sharma',
            ].map((name, i) => (
              <span
                key={i}
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: '#ffffffa4',
                  letterSpacing: '0.01em',
                }}
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Floating navbar for feature pages ── */
function FeaturePageWrapper({ activePage, onNavigate, children }) {
  return (
    <>
      {/* Blurred BG */}
      <div
        className="feature-backdrop"
        style={{ backgroundImage: `url(${homepageBg})` }}
      />

      {/* Page content */}
      <div className="feature-page page-enter">
        <div
          style={{
            maxWidth: 1200,
            margin: '0 auto',
            padding: '0 24px 60px',
          }}
        >
          {children}
        </div>
      </div>
    </>
  );
}

/* ── Root App ── */
export default function App() {
  const [activePage, setActivePage] = useState('home');

  const navigate = (page) => {
    // Smooth scroll to top then switch page
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => setActivePage(page), page === 'home' ? 0 : 120);
  };

  return (
    <div style={{ minHeight: '100vh', position: 'relative' }}>
      <Navbar activePage={activePage} onNavigate={navigate} />

      {activePage === 'home' && (
        <HeroPage onNavigate={navigate} />
      )}

      {activePage !== 'home' && (
        <FeaturePageWrapper activePage={activePage} onNavigate={navigate}>
          {activePage === 'disease' && <DiseaseDiagnosis />}
          {activePage === 'crop' && <CropRecommendation />}
          {activePage === 'yield' && <YieldPrediction />}
        </FeaturePageWrapper>
      )}
    </div>
  );
}
