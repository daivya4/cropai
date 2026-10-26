"""Validate and split the real CropAI datasets without modifying raw files.

Run from the repository root:
    python scripts/prepare_real_data.py

The script creates CSV manifests in ``data/processed``.  It deliberately does
not copy the 54k PlantVillage images, keeping raw downloads untouched and
avoiding duplicated storage.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SEED = 42


def _write_splits(frame: pd.DataFrame, output_dir: Path) -> None:
    """Write deterministic 70/15/15 stratified splits for a labelled frame."""
    train, remainder = train_test_split(
        frame, test_size=0.30, stratify=frame["label"], random_state=SEED
    )
    validation, test = train_test_split(
        remainder, test_size=0.50, stratify=remainder["label"], random_state=SEED
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, split in (("train", train), ("val", validation), ("test", test)):
        split.sort_values("label").to_csv(output_dir / f"{name}.csv", index=False)


def prepare_recommendation() -> None:
    source = RAW / "recommendation" / "Crop_recommendation.csv"
    frame = pd.read_csv(source)
    expected = {"N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"}
    if set(frame.columns) != expected:
        raise ValueError(f"Unexpected recommendation columns: {list(frame.columns)}")

    frame = frame.rename(columns={"N": "nitrogen", "P": "phosphorus", "K": "potassium"})
    frame["label"] = frame["label"].str.strip().str.lower()
    if frame.isna().any().any():
        raise ValueError("Recommendation dataset contains missing values.")
    _write_splits(frame, PROCESSED / "recommendation")
    print(f"Recommendation: {len(frame)} rows, {frame['label'].nunique()} classes")


def prepare_indian_recommendation() -> None:
    """Normalize the Indian district/year crop outcomes into crop-level rows."""
    source = RAW / "recommendation" / "Crops_data.csv"
    frame = pd.read_csv(source)
    required = {"Dist Code", "Year", "State Code", "State Name", "Dist Name"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Unexpected Indian recommendation columns: {list(frame.columns)}")

    rows: list[dict[str, object]] = []
    excluded = ("OILSEEDS", "SORGHUM", "PULSES", "FRUITS", "VEGETABLES", "FODDER")
    for yield_column in (column for column in frame.columns if column.endswith(" YIELD (Kg per ha)")):
        crop_name = yield_column.removesuffix(" YIELD (Kg per ha)").strip()
        if any(term in crop_name.upper() for term in excluded):
            continue
        area_column = f"{crop_name} AREA (1000 ha)"
        production_column = f"{crop_name} PRODUCTION (1000 tons)"
        if area_column not in frame.columns or production_column not in frame.columns:
            continue

        crop_rows = frame[
            ["Dist Code", "Year", "State Code", "State Name", "Dist Name",
             area_column, production_column, yield_column]
        ].copy()
        crop_rows.columns = [
            "district_code", "year", "state_code", "state", "district",
            "area_thousand_hectares", "production_thousand_tonnes", "yield_kg_per_hectare",
        ]
        for numeric_column in (
            "district_code", "year", "state_code", "area_thousand_hectares",
            "production_thousand_tonnes", "yield_kg_per_hectare",
        ):
            crop_rows[numeric_column] = pd.to_numeric(crop_rows[numeric_column], errors="coerce")
        crop_rows["state"] = crop_rows["state"].astype("string").str.strip()
        crop_rows["district"] = crop_rows["district"].astype("string").str.strip()
        crop_rows = crop_rows[
            crop_rows["yield_kg_per_hectare"].notna()
            & (crop_rows["yield_kg_per_hectare"] > 0)
        ].copy()
        crop_rows.insert(5, "crop", crop_name.title())
        rows.extend(crop_rows.to_dict("records"))

    normalized = pd.DataFrame(rows)
    if normalized.empty or len(normalized) < 20_000:
        raise ValueError(f"Indian recommendation normalization produced only {len(normalized)} rows.")
    normalized = normalized.sort_values(["year", "state", "district", "crop"]).reset_index(drop=True)

    output_dir = PROCESSED / "recommendation_indian"
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output_dir / "all.csv", index=False)
    train = normalized[normalized["year"] <= normalized["year"].max() - 2]
    validation = normalized[normalized["year"] == normalized["year"].max() - 1]
    test = normalized[normalized["year"] == normalized["year"].max()]
    for name, split in (("train", train), ("val", validation), ("test", test)):
        split.to_csv(output_dir / f"{name}.csv", index=False)
    print(
        f"Indian recommendation: {len(normalized)} rows, "
        f"{normalized['crop'].nunique()} crops, {normalized['state'].nunique()} states"
    )


def prepare_disease() -> None:
    image_root = RAW / "disease" / "plantvillage" / "raw" / "color"
    if not image_root.is_dir():
        raise FileNotFoundError(f"PlantVillage colour images were not found at {image_root}")

    rows: list[dict[str, str]] = []
    valid_suffixes = {".jpg", ".jpeg", ".png"}
    for class_dir in sorted(path for path in image_root.iterdir() if path.is_dir()):
        for image_path in class_dir.iterdir():
            if image_path.suffix.lower() in valid_suffixes:
                rows.append(
                    {
                        "path": image_path.relative_to(ROOT).as_posix(),
                        "label": class_dir.name,
                    }
                )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("No PlantVillage images were found.")
    if (frame["label"].value_counts() < 4).any():
        raise ValueError("Every PlantVillage class needs at least four images for splitting.")
    _write_splits(frame, PROCESSED / "disease")
    print(f"Disease: {len(frame)} images, {frame['label'].nunique()} classes")


def prepare_yield() -> None:
    source = RAW / "yield" / "crop_production.csv"
    frame = pd.read_csv(source)
    expected = {
        "State_Name", "District_Name", "Crop_Year", "Season", "Crop", "Area", "Production"
    }
    if set(frame.columns) != expected:
        raise ValueError(f"Unexpected yield columns: {list(frame.columns)}")

    frame = frame.rename(
        columns={
            "State_Name": "state",
            "District_Name": "district",
            "Crop_Year": "year",
            "Season": "season",
            "Crop": "crop",
            "Area": "area_hectares",
            "Production": "production_tonnes",
        }
    )
    for column in ("state", "district", "season", "crop"):
        frame[column] = frame[column].astype("string").str.strip()
    frame = frame.dropna(subset=["state", "district", "year", "season", "crop", "area_hectares", "production_tonnes"])
    frame = frame[(frame["area_hectares"] > 0) & (frame["production_tonnes"] >= 0)].copy()
    frame["yield_tonnes_per_hectare"] = frame["production_tonnes"] / frame["area_hectares"]

    latest_year = int(frame["year"].max())
    validation_year = latest_year - 1
    train = frame[frame["year"] < validation_year]
    validation = frame[frame["year"] == validation_year]
    test = frame[frame["year"] == latest_year]
    if train.empty or validation.empty or test.empty:
        raise ValueError("Yield data cannot form a train/validation/test temporal split.")

    output_dir = PROCESSED / "yield"
    output_dir.mkdir(parents=True, exist_ok=True)
    train.to_csv(output_dir / "train.csv", index=False)
    validation.to_csv(output_dir / "val.csv", index=False)
    test.to_csv(output_dir / "test.csv", index=False)
    print(
        "Yield: "
        f"{len(frame)} valid rows; temporal split train < {validation_year}, "
        f"validation = {validation_year}, test = {latest_year}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--module",
        choices=("all", "disease", "recommendation", "recommendation_indian", "yield"),
        default="all",
        help="Dataset preparation target.",
    )
    args = parser.parse_args()
    if args.module in ("all", "recommendation"):
        prepare_recommendation()
    if args.module in ("all", "recommendation_indian"):
        prepare_indian_recommendation()
    if args.module in ("all", "yield"):
        prepare_yield()
    if args.module in ("all", "disease"):
        prepare_disease()


if __name__ == "__main__":
    main()
