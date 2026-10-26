from __future__ import annotations

import json
import pickle
from pathlib import Path


class IndianCropInferenceService:
    def __init__(self, config_path: str = "configs/config.yaml"):
        import yaml

        with open(config_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        root = Path(config_path).resolve().parent.parent
        artifact_dir = root / "artifacts" / "crop_indian"
        with (artifact_dir / "model.pkl").open("rb") as handle:
            self.model = pickle.load(handle)
        self.metadata = json.loads((artifact_dir / "metadata.json").read_text(encoding="utf-8"))

    def locations(self) -> dict[str, list[str]]:
        locations: dict[str, set[str]] = {}
        for key in self.model["district_scores"]:
            state, district = key.split("\t", maxsplit=1)
            locations.setdefault(state, set()).add(district)
        return {
            state: sorted(districts)
            for state, districts in sorted(locations.items())
        }

    def recommend(self, state: str, district: str, year: int, top_k: int, soil_inputs: dict | None = None) -> dict:
        state, district = state.strip(), district.strip()
        key = f"{state}\t{district}"
        scores = self.model["district_scores"].get(
            key,
            self.model["state_scores"].get(state, self.model["national_scores"]),
        ).copy()
        source = "indian_district_crop_history"
        if soil_inputs is not None:
            from models.crop.inference import CropInferenceService

            legacy = CropInferenceService().predict(soil_inputs)
            legacy_scores = {
                item["crop"].title(): item["probability"]
                for item in legacy["top_recommendations"]
            }
            scores = {
                crop: 0.8 * score + 0.2 * legacy_scores.get(crop, 0.0)
                for crop, score in scores.items()
            }
            source = "indian_history_plus_soil_weather"
        recommendations = sorted(
            [
                {"crop": crop, "probability": round(float(score), 6)}
                for crop, score in scores.items()
            ],
            key=lambda item: item["probability"],
            reverse=True,
        )[:top_k]
        return {
            "state": state,
            "district": district,
            "year": year,
            "recommended_crop": recommendations[0]["crop"],
            "confidence": recommendations[0]["probability"],
            "top_recommendations": recommendations,
            "recommendations": recommendations,
            "data_source": source,
            "model_version": self.metadata["model_version"],
        }
