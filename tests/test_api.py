import io
import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import app
from api.routes import crop as crop_route, summary as summary_route
from models.translation.indictrans import validate_translation

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models_loaded" in data

def test_crop_recommendation_valid():
    payload = {
        "nitrogen": 80,
        "phosphorus": 45,
        "potassium": 40,
        "temperature": 24.5,
        "humidity": 85,
        "ph": 6.2,
        "rainfall": 180
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_crop" in data
    assert "confidence" in data
    assert "top_recommendations" in data
    assert "explanation" in data
    assert len(data["explanation"]["top_features"]) > 0

def test_crop_recommendation_invalid_values():
    # Nitrogen out of bound
    payload = {
        "nitrogen": -10,
        "phosphorus": 45,
        "potassium": 40,
        "temperature": 24.5,
        "humidity": 120, # out of bound
        "ph": 6.2,
        "rainfall": 180
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 422  # Validation Error

def test_crop_recommendation_missing_param():
    payload = {
        "nitrogen": 80,
        "phosphorus": 45,
        "potassium": 40
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 422  # Validation Error


def test_indian_crop_recommendation_valid():
    response = client.post(
        "/api/v1/crop/recommend-india",
        json={"state": "Punjab", "district": "Ludhiana", "year": 2017, "top_k": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == "crop_indian_recommender_v2"
    assert len(data["recommendations"]) == 3
    assert all("crop" in item for item in data["recommendations"])
    assert "recommended_crop" in data
    assert all("predicted_yield_kg_per_hectare" not in item for item in data["recommendations"])


def test_indian_crop_recommendation_invalid_top_k():
    response = client.post(
        "/api/v1/crop/recommend-india",
        json={"state": "Punjab", "district": "Ludhiana", "top_k": 11},
    )
    assert response.status_code == 422


def test_current_crop_weather(monkeypatch):
    class MockWeatherClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def get(self, url, params):
            if url == crop_route.GEOCODING_URL:
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "name": "Ludhiana",
                                "admin1": "Punjab",
                                "latitude": 30.91,
                                "longitude": 75.85,
                            }
                        ]
                    },
                    request=httpx.Request("GET", url),
                )
            return httpx.Response(
                200,
                json={
                    "current": {
                        "temperature_2m": 27.5,
                        "relative_humidity_2m": 62,
                        "time": "2026-10-25T10:00",
                    },
                    "timezone": "Asia/Kolkata",
                },
                request=httpx.Request("GET", url),
            )

    monkeypatch.setattr(crop_route.httpx, "AsyncClient", lambda **kwargs: MockWeatherClient())
    response = client.get(
        "/api/v1/crop/weather/current",
        params={"district": "Ludhiana", "state": "Punjab"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "location": "Ludhiana, Punjab",
        "temperature_c": 27.5,
        "relative_humidity_percent": 62,
        "observed_at": "2026-10-25T10:00",
        "timezone": "Asia/Kolkata",
        "source": "Open-Meteo",
    }


def test_farmer_summary_translation_uses_local_model(monkeypatch):
    class MockTranslator:
        def translate(self, text, language):
            assert text.startswith("For Rice in Punjab")
            assert language == "hi"
            return "पंजाब में धान की अच्छी पैदावार हो सकती है।"

    monkeypatch.setattr(summary_route, "get_translator", lambda: MockTranslator())
    response = client.post(
        "/api/v1/summary/translate",
        json={
            "text": "For Rice in Punjab, the harvest may be good.",
            "language": "hi",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "language": "hi",
        "translated_text": "पंजाब में धान की अच्छी पैदावार हो सकती है।",
    }


def test_farmer_summary_translation_rejects_unsupported_language():
    response = client.post(
        "/api/v1/summary/translate",
        json={"text": "Harvest estimate.", "language": "fr"},
    )
    assert response.status_code == 422


def test_farmer_summary_translation_does_not_return_english_on_model_failure(monkeypatch):
    source_text = "For Rice in Punjab, the harvest may be good."

    def fail_to_load_model():
        raise RuntimeError("Model access is unavailable.")

    monkeypatch.setattr(summary_route, "get_translator", fail_to_load_model)
    response = client.post(
        "/api/v1/summary/translate",
        json={"text": source_text, "language": "hi"},
    )
    assert response.status_code == 503
    assert source_text not in response.text


def test_farmer_summary_translation_rejects_latin_script_output():
    with pytest.raises(RuntimeError, match="untranslated English"):
        validate_translation("धान की उपज 2.22 tonnes per hectare है।")


def test_yield_prediction_valid():
    payload = {
        "state": "Punjab",
        "crop": "Rice",
        "season": "Kharif     ",
        "area_hectares": 2.5,
        "confidence_level": 0.90
    }
    response = client.post("/api/v1/yield/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_yield" in data
    assert "unit" in data
    assert "interval" in data
    assert data["interval"]["confidence_level"] == 0.90
    assert "explanation" in data

def test_yield_prediction_invalid():
    payload = {
        "crop": "Rice",
        "season": "Kharif",
        "area_hectares": 0.0,   # Below minimum 0.1
        "confidence_level": 0.90
    }
    response = client.post("/api/v1/yield/predict", json=payload)
    assert response.status_code == 422

def test_disease_diagnosis_invalid_file_format():
    files = {"image": ("test.txt", b"dummy text content", "text/plain")}
    response = client.post("/api/v1/disease/predict", files=files)
    # 400 when format is rejected before model check; 503 if model not yet loaded but
    # the route validation fires first (order depends on FastAPI dependency resolution).
    assert response.status_code in (400, 503)
    if response.status_code == 400:
        assert "Unsupported image format" in response.json()["detail"]

def test_disease_diagnosis_valid_image():
    # Create a dummy image in memory
    img = Image.new("RGB", (224, 224), (255, 255, 255))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    files = {"image": ("test.png", img_bytes, "image/png")}
    response = client.post("/api/v1/disease/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "top_predictions" in data
    assert "uncertainty" in data
    assert "explanation" in data
    assert data["explanation"]["explanation_available"] is True
    assert "overlay_base64" in data["explanation"]
