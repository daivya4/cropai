import os
<<<<<<< HEAD
=======
import sys
from pathlib import Path
>>>>>>> origin/bhavya-feature
import requests
import streamlit as st
import matplotlib.pyplot as plt
import importlib
<<<<<<< HEAD
=======

# Add repository root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

>>>>>>> origin/bhavya-feature
yield_exp_mod = importlib.import_module("models.yield.explainability")
generate_yield_shap_plot = yield_exp_mod.generate_yield_shap_plot

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Yield Prediction — CropAI", page_icon="🌱", layout="wide")

<<<<<<< HEAD
st.markdown("""
<style>
    .section-title {
        color: #2E7D32;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c5e1a5;
=======
# Custom CSS for modern theme-adaptive design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .section-title {
        font-weight: 700;
        font-size: 2rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }
    .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 1.25rem;
        border-radius: 12px;
>>>>>>> origin/bhavya-feature
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
<<<<<<< HEAD
        color: #2E7D32;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555555;
=======
        letter-spacing: -0.02em;
        color: #10b981;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.65;
        font-weight: 500;
>>>>>>> origin/bhavya-feature
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='section-title'>📈 Yield Prediction</h1>", unsafe_allow_html=True)
st.write("Predict expected agricultural crop yield (tonnes per hectare) and calculate statistical reliability boundaries using Conformal Prediction intervals.")

st.write("---")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Agricultural Parameters")

<<<<<<< HEAD
=======
    state = st.selectbox("Select State", ["Punjab", "Maharashtra", "Uttar Pradesh", "Tamil Nadu", "West Bengal", "Karnataka", "Gujarat", "Madhya Pradesh", "Andhra Pradesh", "Haryana", "Bihar", "Odisha", "Rajasthan", "Kerala", "Assam"])
>>>>>>> origin/bhavya-feature
    crop = st.selectbox("Select Crop", ["Rice", "Maize", "Chickpea", "Cotton", "Mango", "Banana", "Grapes", "Wheat", "Sugarcane", "Arhar/Tur"])
    season = st.selectbox("Select Season", ["Kharif     ", "Rabi   ", "Summer", "Whole Year", "Winter", "Autumn"])
    area_ha = st.number_input("Cultivated Area (hectares)", min_value=0.1, max_value=10_000_000.0, value=1000.0, step=100.0)

    # Conformal confidence selector
    conf_pct = st.selectbox("Statistical Confidence Level", ["90% (Recommended)", "95%", "80%"])
    conf_level = {"90% (Recommended)": 0.90, "95%": 0.95, "80%": 0.80}[conf_pct]

    if st.button("Predict Expected Yield", type="primary", use_container_width=True):
        payload = {
<<<<<<< HEAD
=======
            "state": state,
>>>>>>> origin/bhavya-feature
            "crop": crop,
            "season": season,
            "area_hectares": area_ha,
            "confidence_level": conf_level
        }

        with st.spinner("Processing regression and generating conformal intervals..."):
            try:
                response = requests.post(f"{API_URL}/api/v1/yield/predict", json=payload, timeout=30)
                if response.status_code == 200:
                    st.session_state["yield_result"] = response.json()
                    st.success("Yield prediction calculated!")
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail', 'Yield prediction failed')}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

with col_right:
    st.subheader("Yield Estimates & Reliability")

    if "yield_result" in st.session_state:
        res = st.session_state["yield_result"]
        pred_yield = res["predicted_yield"]
        unit = res["unit"]
        interval = res["interval"]
        explanation = res["explanation"]

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">Estimated Yield ({unit})</div>
                <div class="metric-value">{pred_yield:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">{int(interval['confidence_level']*100)}% Confidence Interval</div>
                <div class="metric-value">[{interval['lower']:.2f}, {interval['upper']:.2f}]</div>
            </div>
            """, unsafe_allow_html=True)

        # Explanatory card
        st.write("#### 🛡️ Conformal Prediction Bounds")
        st.write(f"- Under the requested **{int(interval['confidence_level']*100)}%** confidence level, the true yield is statistically guaranteed to fall between **{interval['lower']:.2f}** and **{interval['upper']:.2f}** {unit} (assuming environment consistency).")
        st.write(f"- **Interval Width:** `{interval['interval_width']:.4f}` {unit}")

        # Draw SHAP explanation graph
        if explanation.get("top_features"):
            st.write("#### ⚖️ Feature Contribution (SHAP)")
            st.caption("Shows the relative impact of each categorical class one-hot encoding or numeric environmental feature on the predicted yield value.")

            fig = generate_yield_shap_plot(explanation["top_features"], pred_yield)
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("Input parameters in the left panel and click 'Predict Expected Yield' to view outputs.")

if st.button("Return to Dashboard"):
    st.switch_page("streamlit_app.py")
