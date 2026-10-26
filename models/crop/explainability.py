import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import shap

class CropExplainer:
    def __init__(self, model_service):
        self.model_service = model_service
        # Get base estimator from the FrozenEstimator wrapped inside calibrated classifier
        try:
            frozen_estimator = self.model_service.model.calibrated_classifiers_[0].estimator
            self.base_model = getattr(frozen_estimator, "estimator", frozen_estimator)
        except Exception:
            self.base_model = self.model_service.model
        self.feature_names = self.model_service.feature_names
        
        # Instantiate TreeExplainer
        self.explainer = shap.TreeExplainer(self.base_model)

    def explain_prediction(self, input_data: dict, predicted_crop: str):
        """
        Calculates local SHAP feature contributions for a specific prediction.
        """
        # Encode prediction
        predicted_idx = self.model_service.label_encoder.transform([predicted_crop])[0]
        
        # Scale inputs
        values = [input_data[name] for name in self.feature_names]
        X = np.array([values])
        X_scaled = self.model_service.scaler.transform(X)
        
        # Compute SHAP values
        # shap_values output shape depends on model type.
        # For multi-class XGBClassifier, it is typically list of length num_classes, each of shape (num_samples, num_features)
        # or a single array of shape (num_samples, num_features, num_classes)
        shap_out = self.explainer.shap_values(X_scaled)
        
        if isinstance(shap_out, list):
            # List of length classes
            class_shap = shap_out[predicted_idx][0]
        elif isinstance(shap_out, np.ndarray):
            if len(shap_out.shape) == 3:
                # Shape: (num_samples, num_features, num_classes)
                class_shap = shap_out[0, :, predicted_idx]
            elif len(shap_out.shape) == 2:
                # Binary/Single class shape: (num_samples, num_features)
                class_shap = shap_out[0]
            else:
                class_shap = shap_out
        else:
            class_shap = np.zeros(len(self.feature_names))
            
        # Create mapping
        contributions = []
        for i, name in enumerate(self.feature_names):
            contributions.append({
                "feature": name,
                "value": float(values[i]),
                "shap_value": float(class_shap[i])
            })
            
        # Sort by absolute SHAP value
        contributions = sorted(contributions, key=lambda x: abs(x["shap_value"]), reverse=True)
        return contributions

def generate_shap_bar_plot(contributions, predicted_crop):
    """
    Creates a Matplotlib horizontal bar chart of the SHAP feature contributions.
    Returns: matplotlib Figure with transparent background.
    """
    sorted_contribs = sorted(contributions, key=lambda x: x["shap_value"])
    
    features = [c["feature"] for c in sorted_contribs]
    shap_vals = [c["shap_value"] for c in sorted_contribs]
    colors = ['#10b981' if v >= 0 else '#ef4444' for v in shap_vals]
    
    fig, ax = plt.subplots(figsize=(6, 3.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    ax.barh(features, shap_vals, color=colors, edgecolor='none', height=0.55)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#88888844')
    ax.tick_params(colors='#888888', labelsize=9)
    ax.axvline(0, color='#88888844', linewidth=0.8, linestyle='--')
    
    plt.title(f"Feature Impact: {predicted_crop}", fontsize=10, pad=12, color='#888888')
    plt.xlabel("SHAP Value (Impact)", fontsize=8, color='#888888')
    plt.tight_layout()
    
    return fig
