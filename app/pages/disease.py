import os
<<<<<<< HEAD
=======
import sys
from pathlib import Path
>>>>>>> origin/bhavya-feature
import io
import base64
import requests
import streamlit as st
from PIL import Image

<<<<<<< HEAD
=======
# Add repository root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

>>>>>>> origin/bhavya-feature
# Config
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Disease Diagnosis — CropAI", page_icon="🌱", layout="wide")

<<<<<<< HEAD
# Custom CSS for modern design
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

st.markdown("<h1 class='section-title'>🔍 Crop Disease Diagnosis</h1>", unsafe_allow_html=True)
st.write("Upload a crop leaf image to analyze and classify plant diseases with explainable heatmaps.")

st.write("---")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Supported formats: JPG, JPEG, PNG, WebP (Max 5MB)", 
        type=["jpg", "jpeg", "png", "webp"]
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption="Uploaded Crop Leaf", use_container_width=True)
        
        # Predict Button
        if st.button("Run Diagnosis", type="primary", use_container_width=True):
            with st.spinner("Analyzing image via MobileNetV3 + MC Dropout + Grad-CAM..."):
                try:
                    # Prepare file payload
                    files = {"image": (uploaded_file.name, image_bytes, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/api/v1/disease/predict", files=files, timeout=30)
                    
                    if response.status_code == 200:
                        st.session_state["disease_result"] = response.json()
                        st.success("Analysis Completed!")
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Inference failed')}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

with col_right:
    st.subheader("Diagnosis Results")
    
    if "disease_result" in st.session_state:
        res = st.session_state["disease_result"]
        
        # Predict values
        pred_class = res["prediction"].replace("___", " - ")
        confidence = res["confidence"]
        uncertainty = res["uncertainty"]
        explanation = res["explanation"]
        
        # 1. Main prediction card
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">Predicted Class</div>
                <div class="metric-value">{pred_class}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
<<<<<<< HEAD
            <div class="metric-container">
=======
            <div class="metric-card">
>>>>>>> origin/bhavya-feature
                <div class="metric-label">Confidence</div>
                <div class="metric-value">{confidence * 100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. Uncertainty indicator
        st.write("#### 🛡️ Uncertainty & Reliability")
        rel_color = {"High": "green", "Medium": "orange", "Low": "red"}[uncertainty["reliability"]]
        st.markdown(f"**Prediction Reliability:** :{rel_color}[**{uncertainty['reliability']}**]")
        st.write(f"- **Predictive Entropy:** `{uncertainty['entropy']:.4f}` (Normalized: `{uncertainty['normalized_entropy']:.4f}`)")
        
        # Draw confidence meter
        st.progress(confidence)
        
        # 3. Top Predictions list
        st.write("#### 📊 Probability Distribution")
        top_preds = res["top_predictions"]
        for p in top_preds:
            st.write(f"- **{p['class'].replace('___', ' - ')}:** {p['probability'] * 100:.1f}%")
            
        # 4. Grad-CAM overlay image display
        if explanation["explanation_available"]:
            st.write("#### 👁️ Grad-CAM Visual Explanation")
            st.caption("The heatmap highlights the regions (red/yellow) that influenced the model prediction. Useful for locating disease lesions.")
            
            # Decode base64 Grad-CAM overlay
            overlay_data = base64.b64decode(explanation["overlay_base64"])
            overlay_image = Image.open(io.BytesIO(overlay_data))
            st.image(overlay_image, caption="Grad-CAM Activation Overlay", use_container_width=True)
            
            st.info("**Caution:** This heatmap highlights correlation of activations, not clinical causal proof. Utilize as decision support.")
    else:
        st.info("Upload a leaf image and click 'Run Diagnosis' to view outputs.")

# Add return button
if st.button("Return to Dashboard"):
    st.switch_page("streamlit_app.py")
