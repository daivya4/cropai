from models.disease.inference import DiseaseInferenceService
from models.crop.inference import CropInferenceService
from models.crop.indian_inference import IndianCropInferenceService
import importlib
yield_inference = importlib.import_module("models.yield.inference")
YieldInferenceService = yield_inference.YieldInferenceService

# Global singletons cached in memory
_disease_service = None
_crop_service = None
_crop_indian_service = None
_yield_service = None

def get_disease_service():
    global _disease_service
    if _disease_service is None:
        try:
            _disease_service = DiseaseInferenceService()
        except Exception:
            return None
    return _disease_service

def get_crop_service() -> CropInferenceService:
    global _crop_service
    if _crop_service is None:
        _crop_service = CropInferenceService()
    return _crop_service


def get_crop_indian_service() -> IndianCropInferenceService:
    global _crop_indian_service
    if _crop_indian_service is None:
        _crop_indian_service = IndianCropInferenceService()
    return _crop_indian_service

def get_yield_service() -> YieldInferenceService:
    global _yield_service
    if _yield_service is None:
        _yield_service = YieldInferenceService()
    return _yield_service
