import base64
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Dict, Any

from api.dependencies import get_disease_service
from models.disease.inference import DiseaseInferenceService

router = APIRouter()

SUPPORTED_FORMATS = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/predict")
async def predict_disease(
    image: UploadFile = File(...),
    service: DiseaseInferenceService = Depends(get_disease_service)
) -> Dict[str, Any]:
    # Validate content type before any heavy computation
    if image.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported image format. Upload JPG, JPEG, PNG, or WebP.")

    if service is None:
        raise HTTPException(status_code=503, detail="Disease model is not yet loaded. Please try again later.")

    # Read file
    content = await image.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit of 5MB.")

    # Run prediction
    try:
        result = service.predict(content)
    except Exception as e:
        # Internal server error logging
        import logging
        logging.error(f"Inference error in disease route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal inference engine failure.")
        
    # Convert overlay bytes to base64 string
    overlay_b64 = base64.b64encode(result["overlay_bytes"]).decode("utf-8")
    
    return {
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "top_predictions": result["top_predictions"],
        "uncertainty": result["uncertainty"],
        "explanation": {
            "explanation_available": True,
            "overlay_base64": overlay_b64
        },
        "model_version": result["model_version"]
    }
