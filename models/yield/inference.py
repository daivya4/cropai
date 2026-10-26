import os
import pickle
import numpy as np
import pandas as pd

class YieldInferenceService:
    def __init__(self, config_path="configs/config.yaml"):
        # Load config
        import yaml
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.model_path = self.config["models"]["yield"]["path"]
        self.residuals_path = self.config["models"]["yield"]["conformal_residuals_path"]
        
        # Load artifacts
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        with open(self.residuals_path, "rb") as f:
            self.conformal_residuals = pickle.load(f)
            
        self.categorical_cols = ["state", "crop", "season"]
        self.numeric_cols = ["area_hectares"]

    def predict(self, input_data: dict, confidence_level: float = 0.90):
        """
        Input: dict with keys: state (optional, defaults to Punjab), crop, season, area_hectares.
        """
        # Ensure state is present
        data = dict(input_data)
        if "state" not in data or not data["state"]:
            data["state"] = "Punjab"
            
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Make base prediction on log scale and expm1 back to original scale
        pred_log = float(self.model.predict(df)[0])
        pred = float(np.expm1(pred_log))
        
        # Calculate conformal interval
        alpha = 1.0 - confidence_level
        n_val = len(self.conformal_residuals)
        q_index = int(np.ceil((1.0 - alpha) * (n_val + 1))) - 1
        q_index = max(0, min(q_index, n_val - 1))
        q_hat = float(np.sort(self.conformal_residuals)[q_index])
        
        lower_bound = max(0.0, pred - q_hat) # Yield cannot be negative
        upper_bound = pred + q_hat
        
        # Features map for explainability reference
        return {
            "predicted_yield": pred,
            "unit": "tonnes/hectare",
            "interval": {
                "lower": lower_bound,
                "upper": upper_bound,
                "confidence_level": confidence_level,
                "interval_width": float(q_hat * 2)
            },
            "features": data,
            "model_version": "yield_v2"
        }
