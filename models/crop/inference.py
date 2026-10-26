import os
import pickle
import numpy as np
import pandas as pd

class CropInferenceService:
    def __init__(self, config_path="configs/config.yaml"):
        # Load config
        import yaml
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.model_path = self.config["models"]["crop"]["path"]
        self.scaler_path = self.config["models"]["crop"]["scaler_path"]
        
        # Load artifacts
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        with open(self.scaler_path, "rb") as f:
            self.scaler = pickle.load(f)
            
        # Get class labels from label encoder stored in metadata/artifacts
        artifact_dir = os.path.dirname(self.model_path)
        le_path = os.path.join(artifact_dir, "label_encoder.pkl")
        with open(le_path, "rb") as f:
            self.label_encoder = pickle.load(f)
            
        self.classes = self.label_encoder.classes_.tolist()
        self.feature_names = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]

    def predict(self, input_data: dict):
        """
        Input: dict with keys: nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall.
        """
        # Convert to array in correct order
        values = [input_data[name] for name in self.feature_names]
        X = np.array([values])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict probabilities
        probs = self.model.predict_proba(X_scaled)[0]
        
        # Get prediction
        predicted_idx = int(np.argmax(probs))
        predicted_crop = self.classes[predicted_idx]
        confidence = float(probs[predicted_idx])
        
        # Top recommendations
        top_recommendations = []
        for idx, prob in enumerate(probs):
            top_recommendations.append({
                "crop": self.classes[idx],
                "probability": float(prob)
            })
        top_recommendations = sorted(top_recommendations, key=lambda x: x["probability"], reverse=True)
        
        # Reliability rating
        # High reliability if confidence > 0.7, medium if > 0.4, else low
        reliability = "High" if confidence > 0.7 else ("Medium" if confidence > 0.4 else "Low")
        
        # Features map for explainability reference
        # Store scaled values as well as original values
        raw_features = {self.feature_names[i]: float(values[i]) for i in range(len(self.feature_names))}
        scaled_features = {self.feature_names[i]: float(X_scaled[0][i]) for i in range(len(self.feature_names))}
        
        return {
            "recommended_crop": predicted_crop,
            "confidence": confidence,
            "top_recommendations": top_recommendations,
            "reliability": reliability,
            "features": raw_features,
            "scaled_features": scaled_features,
            "model_version": "crop_v2"
        }
