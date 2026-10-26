from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "processed" / "recommendation_indian" / "all.csv"
ARTIFACT_DIR = ROOT / "artifacts" / "crop_indian"


def build_scores(frame: pd.DataFrame) -> dict:
    crops = sorted(frame["crop"].unique().tolist())
    district = frame.groupby(["state", "district", "crop"]).size()
    state = frame.groupby(["state", "crop"]).size()
    national = frame.groupby("crop").size()
    district_totals = frame.groupby(["state", "district"]).size()
    state_totals = frame.groupby("state").size()
    total = len(frame)
    scores: dict[str, dict[str, float]] = {}
    for (state_name, district_name), _ in frame.groupby(["state", "district"]):
        scores[f"{state_name}\t{district_name}"] = {
            crop: (
                0.70 * district.get((state_name, district_name, crop), 0)
                / district_totals.get((state_name, district_name), 1)
                + 0.25 * state.get((state_name, crop), 0)
                / state_totals.get(state_name, 1)
                + 0.05 * national.get(crop, 0) / total
            )
            for crop in crops
        }
    state_scores = {
        state_name: {
            crop: 0.95 * state.get((state_name, crop), 0) / state_totals[state_name]
            + 0.05 * national.get(crop, 0) / total
            for crop in crops
        }
        for state_name in frame["state"].unique()
    }
    national_scores = {crop: national.get(crop, 0) / total for crop in crops}
    return {
        "crops": crops,
        "district_scores": scores,
        "state_scores": state_scores,
        "national_scores": national_scores,
    }


def main() -> None:
    frame = pd.read_csv(DATA_PATH)
    train = frame[frame["year"] <= 2015]
    test = frame[frame["year"] == 2017]
    artifact = build_scores(train)
    group_hits = {1: 0, 3: 0, 5: 0}
    group_recall = {1: 0.0, 3: 0.0, 5: 0.0}
    groups = 0
    for (state, district), rows in test.groupby(["state", "district"]):
        key = f"{state}\t{district}"
        scores = artifact["district_scores"].get(
            key, artifact["state_scores"].get(state, artifact["national_scores"])
        )
        ranking = sorted(scores, key=scores.get, reverse=True)
        actual = set(rows["crop"])
        groups += 1
        for k in group_hits:
            selected = set(ranking[:k])
            group_hits[k] += bool(selected & actual)
            group_recall[k] += len(selected & actual) / len(actual)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with (ARTIFACT_DIR / "model.pkl").open("wb") as handle:
        pickle.dump(artifact, handle)
    metadata = {
        "model_name": "indian_crop_suitability_ranker",
        "model_version": "crop_indian_recommender_v2",
        "dataset": "Indian district-year crop occurrence dataset",
        "target": "historical crop suitability ranking",
        "training_rows": len(train),
        "test_rows": len(test),
        "test_districts": groups,
        "metrics": {
            "group_hit_at_1": group_hits[1] / groups,
            "group_hit_at_3": group_hits[3] / groups,
            "group_hit_at_5": group_hits[5] / groups,
            "group_recall_at_1": group_recall[1] / groups,
            "group_recall_at_3": group_recall[3] / groups,
            "group_recall_at_5": group_recall[5] / groups,
        },
        "classes": artifact["crops"],
        "scoring": "70% district history, 25% state history, 5% national history",
    }
    (ARTIFACT_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
