# CropAI — Project Brief & Implementation Hand-off

> **Explainable, Uncertainty-Aware Agricultural Decision Support System**  
> A production-ready ML platform covering disease detection, crop recommendation, and yield prediction — with SHAP/Grad-CAM explainability and calibrated uncertainty on every prediction.

---

## 1. Project Overview

CropAI is a three-module machine learning platform designed for smallholder farmers and agri-analysts. Every prediction endpoint returns not just an answer, but *why* (explainability) and *how confident* (uncertainty), meeting the transparency requirements of responsible AI in high-stakes domains.

| Module | Task Type | Output |
|---|---|---|
| Disease Detection | Image Classification (38 classes) | Diagnosis + Grad-CAM heatmap + MC Dropout uncertainty |
| Crop Recommendation | Tabular Classification (22 classes) | Crop label + SHAP contributions + entropy |
| Yield Prediction | Tabular Regression | Yield t/ha + 90% conformal interval + SHAP waterfall |

---

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Backend API | FastAPI + Uvicorn |
| UI | Streamlit (multi-page) |
| Image Models | PyTorch + torchvision (MobileNetV3-Small → EfficientNet-B0 champion) |
| Tabular Models | scikit-learn · XGBoost · LightGBM · CatBoost |
| Explainability | SHAP TreeExplainer · Grad-CAM (custom hooks) · LIME (tabular/image) |
| Uncertainty | MC Dropout (classification) · Conformal Prediction via MAPIE (regression) |
| Experiment Tracking | MLflow |
| Containerisation | Docker + docker-compose |
| Linting / Types | ruff + mypy --strict |
| Testing | pytest |

---

## 3. Datasets

### 3.1 Disease Detection (Image)

| Dataset | Description | Source |
|---|---|---|
| PlantVillage (colour) | ~54 k leaf images, 38 disease/healthy classes across 14 crop species | [Kaggle: emmarex/plantdisease](https://www.kaggle.com/datasets/emmarex/plantdisease) |
| Cassava Leaf Disease | 21 k images, 5 classes (Kaggle 2021 competition) | [Kaggle: c2021-plant-pathology](https://www.kaggle.com/c/cassava-leaf-disease-classification) |

### 3.2 Crop Recommendation (Tabular)

| Dataset | Description | Source |
|---|---|---|
| Crop Recommendation Dataset | 2200 rows · features: N, P, K, temperature, humidity, pH, rainfall · target: crop label (22 classes) | [Kaggle: atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| Soil Fertility Dataset (augment) | Additional soil chemistry features for enrichment | [Kaggle: rahmasleam/soil-fertility](https://www.kaggle.com/datasets/rahmasleam/soil-fertility) |

### 3.3 Yield Prediction (Tabular + Temporal)

| Dataset | Description | Source |
|---|---|---|
| Crop Yield in Indian States | State + crop + year + area + production; derive `yield = production / area` | [Kaggle: abhinand05/crop-production-in-india](https://www.kaggle.com/datasets/abhinand05/crop-production-in-india) |
| FAOSTAT — Crops and livestock products | Global, 1961–present, country × crop × year | [faostat.fao.org](https://www.faostat.fao.org/) (Bulk: `Production_Crops_Livestock_E_All_Data.zip`) |
| USDA NASS QuickStats | US county-level yields for major crops | [quickstats.nass.usda.gov](https://quickstats.nass.usda.gov/) |
| Climate covariates | Rainfall, temperature, NDVI — ERA5 monthly aggregates or WorldClim v2 | ERA5: [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/) · WorldClim: [worldclim.org](https://www.worldclim.org/data/worldclim21.html) |

**Primary yield target:** India state-crop-year dataset joined with monthly climate aggregates (rainfall, mean temp) for the growing season. Hold out the most recent full year as the test set — **no random split, respect temporal order**.

---

## 4. Repository Structure

```
cropai/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── Makefile                     # make setup / train-all / serve / test
│
├── data/
│   ├── raw/                    # untouched downloads
│   ├── interim/                # cleaned, joined
│   └── processed/              # train/val/test splits, tensors
│
├── src/cropai/
│   ├── models/                 # model definitions per module
│   ├── uncertainty/
│   │   ├── mc_dropout.py
│   │   ├── conformal.py        # MAPIE wrappers
│   │   └── entropy.py          # classification uncertainty
│   ├── xai/
│   │   ├── shap_explainer.py
│   │   ├── lime_explainer.py
│   │   └── gradcam.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── calibration.py     # reliability diagrams, ECE
│   │   └── ood.py             # OOD detection via energy score
│   ├── inference/
│   │   ├── predictors.py      # unified Predictor interface
│   │   └── schemas.py         # Pydantic request/response models
│   └── api/
│       └── main.py            # FastAPI app
│
├── app/
│   └── streamlit_app.py        # demo UI
│
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models_smoke.py
│   ├── test_uncertainty.py
│   └── test_api.py
│
├── scripts/
│   ├── download_all.py
│   ├── prepare_all.py
│   └── train_all.py
│
└── artifacts/
    ├── models/                # saved weights, joblib bundles
    ├── explainers/            # cached SHAP explainers
    └── mlruns/                # MLflow local store
```

---

## 5. Models per Module

### 5.1 Disease Detection

| Parameter | Value |
|---|---|
| Baseline | EfficientNet-B0 pretrained on ImageNet, fine-tuned. Input 224×224 |
| Champion candidate | ConvNeXt-Tiny or EfficientNetV2-S via `timm` |
| Loss | Cross-entropy with label smoothing 0.1; class weights if imbalanced |
| Augmentation | RandAugment + Mixup + CutMix · Color jitter (leaves) |
| Optimizer | AdamW · cosine schedule with 3-epoch warmup · LR 3e-4 · weight decay 1e-4 |
| Uncertainty | MC Dropout at inference (p=0.2 in classifier head, 30 stochastic passes) + 5-model deep ensemble |
| XAI | Grad-CAM and Grad-CAM++ over final conv block · LIME image segmentation as a second view |

### 5.2 Crop Recommendation

| Parameter | Value |
|---|---|
| Baseline | Logistic Regression · RandomForest |
| Boosters | XGBoost · LightGBM · CatBoost |
| Neural | 3-layer MLP with dropout for MC Dropout uncertainty |
| Selection | 5-fold stratified CV; pick by macro-F1 |
| Uncertainty | Predicted probability + entropy · MC Dropout for the MLP |
| XAI | SHAP TreeExplainer for boosters · LIME tabular for the MLP |

### 5.3 Yield Prediction

| Parameter | Value |
|---|---|
| Baseline | Ridge · RandomForestRegressor |
| Boosters | XGBoost · LightGBM (with monotonic constraints where sensible, e.g. rainfall) |
| Temporal | LSTM or TFT (Temporal Fusion Transformer) on monthly climate sequences per (state, crop, year) |
| Uncertainty | Conformal Prediction via MAPIE (`MapieRegressor` with jackknife+ or CV+) for calibrated intervals; deep ensemble variance for LSTM |
| XAI | SHAP TreeExplainer for boosters · SHAP DeepExplainer or Captum Integrated Gradients for LSTM |

---

## 6. Uncertainty — Concrete Requirements

Every prediction endpoint **must** return, alongside the point prediction:

**Classification:**
- Predicted class
- Softmax probability
- Predictive entropy
- MC Dropout mean/variance across 30 passes
- Flag `low_confidence = True` if top-1 prob < 0.6 or entropy > threshold set on validation

**Regression:**
- Point estimate
- 90% conformal interval `[lower, upper]`
- Ensemble std
- Flag `high_uncertainty = True` if interval width > 25% of mean yield

**Calibration report per module:**
- Reliability diagram + Expected Calibration Error (ECE) for classification
- Empirical coverage vs nominal for regression conformal intervals

---

## 7. Step-by-Step Implementation Pipeline

### Step 1 — Repository scaffold
Create directory layout (Section 4), `pyproject.toml`, `requirements.txt`, `.env.example`, `Makefile`.

### Step 2 — Data ingestion
- `scripts/download_all.py` — automated Kaggle CLI + FAOSTAT bulk downloads.
- `scripts/prepare_all.py` — validation, renaming, splitting, and hash logging.
- Write `data/raw/LICENCES.md`.

### Step 3 — Utilities
- `src/cropai/utils/seed.py` — `set_seed(seed: int)` utility (numpy, random, torch, torch.cuda).
- `src/cropai/evaluation/metrics.py` — ECE, coverage, RMSE, macro-F1.

### Step 4 — Feature pipelines
- Recommendation: StandardScaler + LabelEncoder saved to `artifacts/`.
- Yield: ColumnTransformer (OneHot + Scaler) fitted on train only.
- Disease: torchvision transforms saved as JSON config.

### Step 5 — Recommendation module (fastest win)
Train XGBoost, LightGBM, CatBoost, MLP. Log all runs to MLflow.  
Save champion to `artifacts/models/recommendation_champion.joblib`.  
Wire SHAP explainer, LIME tabular, MC Dropout for MLP.  
**Tests:** data loader, feature pipeline round-trip, predict-with-explanation returns expected shape.

### Step 6 — Yield module
Join India yield with WorldClim/ERA5 features by (state, year).  
Train boosters + LSTM. Temporal split: hold out the most recent full year.  
Fit MAPIE `MapieRegressor` on the champion for conformal intervals.  
Wire SHAP + Captum IG for LSTM.  
**Tests:** temporal split has no leakage; conformal coverage on validation is 88–92%.

### Step 7 — Disease module
PyTorch training loop with mixed precision, `torch.compile` optional.  
Train EfficientNet-B0 and ConvNeXt-Tiny; select by val accuracy.  
Train a 5-model deep ensemble of the champion (different seeds + augmentation).  
Evaluate on PlantDoc as OOD; report accuracy drop.  
Wire Grad-CAM (from `pytorch-grad-cam`) and LIME image.  
**Tests:** forward pass, MC Dropout produces variance, Grad-CAM returns H×W map.

### Step 8 — Unified inference layer
`src/cropai/inference/predictors.py`: `DiseasePredictor`, `RecommendationPredictor`, `YieldPredictor`, each with `.predict(x)` returning a `Prediction` Pydantic model (point + uncertainty + explanation).

### Step 9 — FastAPI service
**Routes:**
- `POST /disease/predict` — multipart image
- `POST /recommend/predict` — JSON: N, P, K, temperature, humidity, pH, rainfall
- `POST /yield/predict` — JSON: state, crop, year, season, area, climate features
- `GET /explain/global/{module}`
- `GET /health`

CORS enabled. OpenAPI docs at `/docs`.

### Step 10 — Streamlit UI
Three tabs, one per module. Upload/form → call FastAPI → render prediction, uncertainty bar, and XAI panel (Grad-CAM overlay or SHAP waterfall).

### Step 11 — Evaluation report
Generate `reports/evaluation.md` with tables, ROC curves, reliability diagrams, conformal coverage plots, and OOD results. Rendered from a script, not hand-written.

### Step 12 — Packaging
- `Dockerfile` (`python:3.11-slim`, CPU-only default; add `Dockerfile.gpu` variant)
- `docker-compose.yml` with FastAPI + Streamlit
- README with quickstart: `make setup && make download && make train-all && make serve`

---

## 8. API Contract (Pydantic schemas)

```python
# POST /recommend/predict
class RecommendRequest(BaseModel):
    nitrogen: float    # 0–200 mg/kg
    phosphorus: float  # 0–200 mg/kg
    potassium: float   # 0–300 mg/kg
    temperature: float # -10–60 °C
    humidity: float    # 0–100 %
    ph: float          # 0–14
    rainfall: float    # 0–1000 mm

class RecommendResponse(BaseModel):
    recommended_crop: str
    confidence: float
    low_confidence: bool
    predictive_entropy: float
    top_recommendations: list[dict]
    explanation: dict  # SHAP waterfall data

# POST /yield/predict
class YieldRequest(BaseModel):
    crop: str
    season: str
    rainfall: float    # mm
    temperature: float # °C
    area: float        # hectares

class YieldResponse(BaseModel):
    predicted_yield: float  # tonnes/hectare
    unit: str
    interval: dict     # {lower, upper, confidence_level, width}
    high_uncertainty: bool
    explanation: dict  # SHAP contributions

# POST /disease/predict  (multipart/form-data)
class DiseaseResponse(BaseModel):
    prediction: str
    confidence: float
    low_confidence: bool
    mc_dropout_entropy: float
    top_predictions: list[dict]
    explanation: dict  # {overlay_base64, gradcam_available}
```

---

## 9. Non-Negotiable Engineering Rules

| Rule | Detail |
|---|---|
| **Reproducibility** | Seeds fixed everywhere (numpy, random, torch, torch.cuda) via `set_seed(seed)`. Seed 42 for training; ensemble members use 42–46. |
| **No temporal leakage** | Yield uses strict temporal split. Disease uses stratified split on class. |
| **No data leakage** | Scalers/encoders fitted **only** on train set. |
| **Artefact metadata** | Every model saved with a `metadata.json` (metrics, dataset hash, git SHA). |
| **Pydantic validation** | All API responses are Pydantic-validated — no raw dicts. |
| **Type safety** | Type hints everywhere; run `ruff` + `mypy --strict` on `src/cropai/`. |
| **CI gate** | `pytest -q` must pass before a step is considered done. |

---

## 10. Deliverables Checklist

- [ ] Working repo with the structure in Section 4
- [ ] Three trained champion models + one ensemble for disease
- [ ] Uncertainty estimates on every prediction
- [ ] SHAP / LIME / Grad-CAM in the API responses
- [ ] Calibration + conformal coverage report
- [ ] FastAPI service + Streamlit UI
- [ ] Dockerfile + docker-compose
- [ ] README with quickstart, dataset licences, and evaluation numbers
- [ ] `reports/evaluation.md` auto-generated

---

## 11. Stretch Goals *(only after Section 10 is complete)*

1. Add Bayesian last layer (Laplace approximation via `laplace-torch`) for the CNN as a third uncertainty method.
2. Add OOD detection with an energy-based score on the disease model; reject predictions below threshold.
3. Add active learning loop for cassava (real-world): flag high-uncertainty samples for labelling.
4. Swap SHAP with KernelSHAP on the LSTM for a comparison plot.
5. Serve with BentoML or Ray Serve instead of FastAPI for benchmarking.

---

## 12. Licences & Attribution

`data/raw/LICENCES.md` must record:

| Dataset | Licence |
|---|---|
| PlantVillage | CC BY-SA 4.0 |
| Cassava Leaf Disease | Kaggle competition rules |
| Crop Recommendation | CC0 (public domain) on Kaggle |
| FAOSTAT | CC BY-NC-SA 3.0 IGO |
| USDA NASS | US Public Domain |
| WorldClim v2 | Free for academic/commercial use with citation |

Cite all datasets in the README.

---

## 13. Quickstart (after implementation)

```bash
# 1. Clone and install
git clone https://github.com/your-org/cropai.git && cd cropai
make setup            # creates venv + pip install -r requirements.txt

# 2. Download data (requires Kaggle API key in .env)
make download

# 3. Prepare splits
make prepare

# 4. Train all models (~2 h on GPU, ~8 h CPU)
make train-all

# 5. Launch services
make serve            # FastAPI on :8000, Streamlit on :8501

# 6. Run tests
make test
```

---

*End of project brief. The executor AI should begin at Step 1 and proceed sequentially, committing after each step.*
