from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any

from api.dependencies import get_yield_service
import importlib
yield_inf_mod = importlib.import_module("models.yield.inference")
yield_exp_mod = importlib.import_module("models.yield.explainability")
YieldInferenceService = yield_inf_mod.YieldInferenceService
YieldExplainer = yield_exp_mod.YieldExplainer

router = APIRouter()

class YieldPredictRequest(BaseModel):
    state: str = Field("Punjab", description="Target state (e.g., Punjab, Maharashtra, Uttar Pradesh)")
    crop: str = Field(..., description="Target crop category (e.g., Rice, Maize)")
    season: str = Field(..., description="Target growing season (e.g., Kharif, Rabi)")
    area_hectares: float = Field(..., ge=0.1, le=10_000_000, description="Cultivated land area (hectares)")
    confidence_level: float = Field(0.90, ge=0.50, le=0.99, description="Conformal prediction interval confidence")

@router.post("/predict")
async def predict_yield(
    payload: YieldPredictRequest,
    service: YieldInferenceService = Depends(get_yield_service)
) -> Dict[str, Any]:
    # Extract data as dict
    input_dict = payload.model_dump()
    conf_level = input_dict.pop("confidence_level")
    
    # Run prediction
    try:
        result = service.predict(input_dict, confidence_level=conf_level)
    except Exception as e:
        import logging
        logging.error(f"Inference error in yield route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal inference engine failure.")
        
    # Generate SHAP explanations
    try:
        explainer = YieldExplainer(service)
        contributions = explainer.explain_prediction(input_dict)
    except Exception as e:
        import logging
        logging.error(f"SHAP explanation error in yield route: {str(e)}", exc_info=True)
        contributions = []
        
    return {
        "predicted_yield": result["predicted_yield"],
        "unit": result["unit"],
        "interval": result["interval"],
        "explanation": {
            "top_features": contributions
        },
        "model_version": result["model_version"]
    }
