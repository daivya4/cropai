import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.dependencies import get_disease_service
from api.main import app
from models.disease.inference import DiseaseInferenceService
from models.disease.leaf_validation import NOT_LEAF_MESSAGE, NotLeafImageError


def image_bytes():
    image = Image.new("RGB", (32, 32), color="green")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_disease_service_rejects_non_leaf_before_running_disease_model():
    service = DiseaseInferenceService.__new__(DiseaseInferenceService)
    validation_calls = []
    model_calls = []

    class RejectingValidator:
        def validate(self, image):
            validation_calls.append(image)
            raise NotLeafImageError(NOT_LEAF_MESSAGE)

    service.leaf_validator = RejectingValidator()
    service._predict_leaf = lambda image: model_calls.append(image)

    with pytest.raises(NotLeafImageError, match="does not appear to show a plant leaf"):
        service.predict(image_bytes())

    assert len(validation_calls) == 1
    assert model_calls == []


def test_disease_service_runs_disease_model_after_leaf_validation():
    service = DiseaseInferenceService.__new__(DiseaseInferenceService)
    validation_calls = []
    model_calls = []
    expected_result = {"prediction": "Tomato___healthy"}

    class AcceptingValidator:
        def validate(self, image):
            validation_calls.append(image)
            return 0.9

    service.leaf_validator = AcceptingValidator()

    def run_model(image):
        model_calls.append(image)
        return expected_result

    service._predict_leaf = run_model

    assert service.predict(image_bytes()) == expected_result
    assert len(validation_calls) == 1
    assert len(model_calls) == 1


def test_disease_endpoint_returns_clear_error_for_non_leaf(monkeypatch):
    class RejectingService:
        def predict(self, content):
            assert content.startswith(b"\x89PNG")
            raise NotLeafImageError(NOT_LEAF_MESSAGE)

    monkeypatch.setitem(
        app.dependency_overrides, get_disease_service, lambda: RejectingService()
    )
    response = TestClient(app).post(
        "/api/v1/disease/predict",
        files={"image": ("face.png", image_bytes(), "image/png")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == NOT_LEAF_MESSAGE
