import os
<<<<<<< HEAD
=======
import sys
from pathlib import Path
>>>>>>> origin/bhavya-feature
import requests
import streamlit as st
import matplotlib.pyplot as plt

<<<<<<< HEAD
=======
# Add repository root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

>>>>>>> origin/bhavya-feature
from models.crop.explainability import generate_shap_bar_plot

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Crop Recommendation — CropAI", page_icon="🌱", layout="wide")

st.markdown("""
<style>
<<<<<<< HEAD
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

st.markdown("<h1 class='section-title'>🚜 Crop Recommendation</h1>", unsafe_allow_html=True)
st.write("Input soil chemical properties and climatic metrics to receive a calibrated recommendation of the most suitable crop.")

st.write("---")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Soil & Climatic Parameters")
    
    # Sliders for soil features
    n = st.slider("Nitrogen (N) content in soil (mg/kg)", min_value=0.0, max_value=140.0, value=50.0, step=1.0)
    p = st.slider("Phosphorus (P) content in soil (mg/kg)", min_value=5.0, max_value=145.0, value=50.0, step=1.0)
    k = st.slider("Potassium (K) content in soil (mg/kg)", min_value=5.0, max_value=205.0, value=50.0, step=1.0)
    temp = st.slider("Temperature (°C)", min_value=10.0, max_value=50.0, value=25.0, step=0.5)
    hum = st.slider("Humidity (%)", min_value=10.0, max_value=100.0, value=75.0, step=1.0)
    ph = st.slider("Soil pH value", min_value=3.5, max_value=10.0, value=6.5, step=0.1)
    rain = st.slider("Rainfall (mm)", min_value=20.0, max_value=300.0, value=120.0, step=1.0)
    
    if st.button("Recommend Crop", type="primary", use_container_width=True):
        payload = {
            "nitrogen": n,
            "phosphorus": p,
            "potassium": k,
            "temperature": temp,
            "humidity": hum,
            "ph": ph,
            "rainfall": rain
        }
        
        with st.spinner("Processing features and calculating SHAP values..."):
            try:
                response = requests.post(f"{API_URL}/api/v1/crop/recommend", json=payload, timeout=10)
                if response.status_code == 200:
                    st.session_state["crop_result"] = response.json()
                    st.success("Recommendation generated!")
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail', 'Recommendation failed')}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

with col_right:
    st.subheader("Calibrated Recommendations")
    
    if "crop_result" in st.session_state:
        res = st.session_state["crop_result"]
        crop = res["recommended_crop"]
        conf = res["confidence"]
        rel = res["reliability"]
        explanation = res["explanation"]
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">Recommended Crop</div>
                <div class="metric-value">{crop}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">Calibrated Probability</div>
                <div class="metric-value">{conf * 100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Reliability status
        rel_color = {"High": "green", "Medium": "orange", "Low": "red"}[rel]
        st.markdown(f"**Recommendation Reliability:** :{rel_color}[**{rel}**]")
        st.progress(conf)
        
        # Display top 3 list
        st.write("#### 📊 Top Alternatives")
        for i, alt in enumerate(res["top_recommendations"][:3]):
            st.write(f"{i+1}. **{alt['crop']}:** {alt['probability'] * 100:.1f}%")
            
        # Draw SHAP explanation graph
        if explanation.get("top_features"):
            st.write("#### ⚖️ Feature Importance (SHAP)")
            st.caption("This chart show the relative impact of each environmental feature. Green bars show features supporting the prediction, red bars indicate negative push.")
            
            fig = generate_shap_bar_plot(explanation["top_features"], crop)
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("Adjust the sliders in the left panel and click 'Recommend Crop' to view outputs.")

if st.button("Return to Dashboard"):
    st.switch_page("streamlit_app.py")
