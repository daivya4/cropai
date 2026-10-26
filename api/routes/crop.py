import logging
import math

import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Dict, Any

from api.dependencies import get_crop_indian_service, get_crop_service
from models.crop.inference import CropInferenceService
from models.crop.indian_inference import IndianCropInferenceService
from models.crop.explainability import CropExplainer

router = APIRouter()

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def _weather_json(response: httpx.Response, service: str) -> dict:
    try:
        data = response.json()
    except ValueError as exc:
        logging.warning("Weather provider returned invalid JSON from %s", service)
        raise HTTPException(status_code=502, detail="Weather provider returned an invalid response.") from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Weather provider returned an invalid response.")
    return data


@router.get("/weather/current")
async def current_crop_weather(
    district: str = Query(..., min_length=2, max_length=80),
    state: str = Query(..., min_length=2, max_length=80),
) -> Dict[str, Any]:
    district_aliases = {"bangalore": "Bengaluru"}
    search_district = district_aliases.get(district.casefold(), district)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            geocoding_response = await client.get(
                GEOCODING_URL,
                params={
                    "name": f"{search_district}, {state}",
                    "count": 10,
                    "language": "en",
                    "format": "json",
                    "countryCode": "IN",
                },
            )
            geocoding_response.raise_for_status()
            geocoding = _weather_json(geocoding_response, "geocoding")
            results = geocoding.get("results", [])
            location = next(
                (
                    item
                    for item in results
                    if isinstance(item, dict)
                    and str(item.get("admin1", "")).casefold() == state.casefold()
                ),
                None,
            ) if isinstance(results, list) else None
            if location is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Weather location not found for {district}, {state}, India.",
                )

            latitude = location.get("latitude")
            longitude = location.get("longitude")
            if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
                raise HTTPException(status_code=502, detail="Weather provider returned an invalid location.")

            weather_response = await client.get(
                WEATHER_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m",
                    "timezone": "auto",
                },
            )
            weather_response.raise_for_status()
            weather = _weather_json(weather_response, "forecast")
    except httpx.TimeoutException as exc:
        logging.warning("Weather provider request timed out for %s, %s", district, state)
        raise HTTPException(status_code=502, detail="Weather provider timed out. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        logging.warning("Weather provider returned HTTP %s", exc.response.status_code)
        raise HTTPException(status_code=502, detail="Weather provider is temporarily unavailable.") from exc
    except httpx.RequestError as exc:
        logging.warning("Weather provider request failed: %s", exc)
        raise HTTPException(status_code=502, detail="Could not connect to the weather provider.") from exc

    current = weather.get("current")
    if not isinstance(current, dict):
        raise HTTPException(status_code=502, detail="Weather provider returned no current conditions.")

    temperature = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    if (
        not isinstance(temperature, (int, float))
        or not math.isfinite(temperature)
        or not isinstance(humidity, (int, float))
        or not math.isfinite(humidity)
    ):
        raise HTTPException(status_code=502, detail="Weather provider returned invalid current conditions.")

    return {
        "location": f"{location.get('name', district)}, {location.get('admin1', state)}",
        "temperature_c": temperature,
        "relative_humidity_percent": humidity,
        "observed_at": current.get("time"),
        "timezone": weather.get("timezone"),
        "source": "Open-Meteo",
    }


class CropRecommendRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=200, description="Nitrogen content in soil (mg/kg)")
    phosphorus: float = Field(..., ge=0, le=200, description="Phosphorus content in soil (mg/kg)")
    potassium: float = Field(..., ge=0, le=300, description="Potassium content in soil (mg/kg)")
    temperature: float = Field(..., ge=-10, le=60, description="Air temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")
    rainfall: float = Field(..., ge=0, le=1000, description="Annual/seasonal rainfall (mm)")


class IndianCropRecommendRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=80)
    district: str = Field(..., min_length=2, max_length=80)
    year: int = Field(2020, ge=2010, le=2035)
    top_k: int = Field(5, ge=1, le=10)
    nitrogen: float | None = Field(None, ge=0, le=200)
    phosphorus: float | None = Field(None, ge=0, le=200)
    potassium: float | None = Field(None, ge=0, le=300)
    temperature: float | None = Field(None, ge=-10, le=60)
    humidity: float | None = Field(None, ge=0, le=100)
    ph: float | None = Field(None, ge=0, le=14)
    rainfall: float | None = Field(None, ge=0, le=1000)

@router.get("/recommend-india/locations")
async def indian_crop_locations(
    service: IndianCropInferenceService = Depends(get_crop_indian_service),
) -> Dict[str, list[str]]:
    return service.locations()


@router.post("/recommend-india")
async def recommend_indian_crop(
    payload: IndianCropRecommendRequest,
    service: IndianCropInferenceService = Depends(get_crop_indian_service),
) -> Dict[str, Any]:
    try:
        soil_names = ("nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall")
        soil_inputs = {name: getattr(payload, name) for name in soil_names}
        soil_inputs = soil_inputs if all(value is not None for value in soil_inputs.values()) else None
        return service.recommend(payload.state, payload.district, payload.year, payload.top_k, soil_inputs)
    except Exception as exc:
        import logging

        logging.error("Indian crop recommendation error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Indian crop recommendation failed.") from exc

@router.post("/recommend")
async def recommend_crop(
    payload: CropRecommendRequest,
    service: CropInferenceService = Depends(get_crop_service)
) -> Dict[str, Any]:
    # Extract data as dict
    input_dict = payload.model_dump()
    
    # Run prediction
    try:
        result = service.predict(input_dict)
    except Exception as e:
        import logging
        logging.error(f"Inference error in crop route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal inference engine failure.")
        
    # Generate SHAP explanations
    try:
        explainer = CropExplainer(service)
        contributions = explainer.explain_prediction(input_dict, result["recommended_crop"])
    except Exception as e:
        import logging
        logging.error(f"SHAP explanation error in crop route: {str(e)}", exc_info=True)
        contributions = []
        
    return {
        "recommended_crop": result["recommended_crop"],
        "confidence": result["confidence"],
        "top_recommendations": result["top_recommendations"],
        "reliability": result["reliability"],
        "explanation": {
            "top_features": contributions
        },
        "model_version": result["model_version"]
    }
