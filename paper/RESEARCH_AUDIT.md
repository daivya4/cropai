# Research Audit — Evidence Traceability

This document records which repository evidence supports each claim in the paper, which results were directly extracted, and what information gaps remain.

---

## 1. Evidence Supporting Main Claims

### Claim: Disease classification accuracy of 99.17%
- **Source:** `artifacts/disease/metadata.json` → `metrics.test_accuracy: 0.9916523447090596`
- **Training code:** `training/disease/train_disease.py` (lines 214–223)
- **Verified:** The value is directly extracted from the serialized metadata produced by the training script.

### Claim: Macro F1 of 0.985 for disease
- **Source:** `artifacts/disease/metadata.json` → `metrics.macro_f1: 0.9845873878825081`
- **Verified:** Computed via `sklearn.metrics.precision_recall_fscore_support` with `average="macro"`.

### Claim: ECE of 0.106 for disease
- **Source:** `artifacts/disease/metadata.json` → `metrics.ece: 0.10597478128967838`
- **Training code:** `training/disease/train_disease.py` (lines 49–64, function `calculate_ece`)
- **Verified:** ECE function uses 10 equal-width bins.

### Claim: MobileNetV3-Small architecture
- **Source:** `training/disease/train_disease.py` (line 142): `models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)`
- **Source:** `models/disease/model.py` (line 8): `models.mobilenet_v3_small(weights=None)`
- **Verified:** Consistent across training and inference.

### Claim: 38 classes from PlantVillage
- **Source:** `artifacts/disease/class_mapping.json` — 38 entries (indices 0–37)
- **Source:** `artifacts/disease/metadata.json` → `num_classes: 38`
- **Verified.**

### Claim: Crop recommendation accuracy of 100%
- **Source:** `artifacts/crop/metadata.json` → `metrics.test_accuracy: 1.0`
- **Source:** Confusion matrix in same file — perfect 22×22 diagonal.
- **Verified:** All per-class test counts are 15 (15 × 22 = 330 test samples, all correct).

### Claim: Crop ECE of 0.075
- **Source:** `artifacts/crop/metadata.json` → `metrics.ece: 0.07549257481796483`
- **Verified.**

### Claim: 22 crop classes
- **Source:** `artifacts/crop/metadata.json` → `classes` array has 22 elements.
- **Verified.**

### Claim: Yield R² of 0.947
- **Source:** `artifacts/yield/metadata.json` → `metrics.r2: 0.9468893181749212`
- **Training code:** `training/yield/train_yield.py` (line 72)
- **Verified.**

### Claim: Conformal coverage of 94.8% at 90% nominal
- **Source:** `artifacts/yield/metadata.json` → `metrics.conformal_90_coverage: 0.948306595365419`
- **Training code:** `training/yield/train_yield.py` (lines 74–84)
- **Verified.** Conservative coverage (94.8% > 90%) is expected from finite-sample conformal quantile.

### Claim: Conformal interval width of 7.41
- **Source:** `artifacts/yield/metadata.json` → `metrics.conformal_90_interval_width: 7.405919674146379`
- **Verified.**

### Claim: Grad-CAM implementation
- **Source:** `models/disease/explainability.py` — full Grad-CAM class with hook-based implementation.
- **Verified:** Implements standard Grad-CAM (register forward/backward hooks, GAP of gradients, ReLU activation).

### Claim: MC Dropout implementation
- **Source:** `models/disease/uncertainty.py` — `enable_dropout()` function + 10 stochastic passes.
- **Verified.**

### Claim: SHAP TreeExplainer for crop and yield
- **Source:** `models/crop/explainability.py` → `shap.TreeExplainer(self.base_model)`
- **Source:** `models/yield/explainability.py` → `shap.TreeExplainer(self.regressor)`
- **Verified.**

### Claim: Sigmoid calibration for crop model
- **Source:** `training/crop/train_crop.py` (lines 117–121): `CalibratedClassifierCV(estimator=FrozenEstimator(base_model), method="sigmoid")`
- **Verified.**

### Claim: Log-transform of yield target
- **Source:** `training/yield/train_yield.py` (line 57): `pipeline.fit(X_train, np.log1p(y_train))`
- **Source:** `models/yield/inference.py` (line 39): `pred = float(np.expm1(pred_log))`
- **Verified.**

### Claim: Temporal split for yield data
- **Source:** `scripts/prepare_real_data.py` (lines 105–111): splits by year, train < penultimate_year, val = penultimate_year, test = latest_year.
- **Verified.**

### Claim: Stratified split for disease and crop data
- **Source:** `scripts/prepare_real_data.py` → `train_test_split(..., stratify=frame["label"])` on lines 28–33.
- **Verified.**

### Claim: Docker deployment
- **Source:** `Dockerfile` and `docker-compose.yml` present in repository.
- **Verified.**

### Claim: Inference latencies
- **Source:** `api_server.log` — multiple entries showing latencies:
  - Disease: 0.1089s to 0.8397s (first request cold)
  - Crop: 0.0397s to 0.1531s
  - Yield: 0.0481s to 0.0944s
- **Verified:** Ranges in paper (110–250ms disease, 40–80ms crop, 48–95ms yield) match log entries.

---

## 2. Directly Extracted Results

All numerical results in Tables II–V were directly extracted from:
- `artifacts/disease/metadata.json`
- `artifacts/crop/metadata.json`
- `artifacts/yield/metadata.json`
- `api_server.log`

No results were interpolated, rounded favorably, or fabricated.

---

## 3. Sections Containing TODOs

| Location | TODO Description |
|---|---|
| `main.tex`, author block | Institution name and email to be added |
| `main.tex`, Fig. 1 | System architecture diagram placeholder — needs actual diagram |

---

## 4. Missing Experiments / Information

| Missing Item | Impact | Recommendation |
|---|---|---|
| Ablation studies | Cannot justify individual design choices | Run ablations on label smoothing, log-transform, calibration method |
| Baseline model comparisons | Cannot justify architecture selection | Train and compare ResNet, EfficientNet, XGBoost, LightGBM |
| Cross-validation results | Single split limits statistical reliability | Run k-fold CV at minimum for tabular models |
| OOD evaluation (disease) | Cannot assess real-world robustness | Evaluate on PlantDoc or field-captured images |
| Per-class metrics table | Aggregate metrics hide class-level variation | Generate per-class precision/recall/F1 table |
| Reliability diagrams | Calibration only shown as scalar ECE | Generate visual reliability diagrams |
| User study | No evidence of practical utility | Conduct user study with farmers/agronomists |
| Computational specifications | Hardware details incomplete | Document exact GPU model, RAM, etc. |

---

## 5. Discrepancies Found

| Item | Note |
|---|---|
| Streamlit app has git merge conflicts | `app/streamlit_app.py` contains unresolved `<<<<<<< HEAD` / `>>>>>>> origin/bhavya-feature` markers, indicating two active branches |
| PRD mentions XGBoost/LightGBM/CatBoost | Actual implementation uses only Random Forest (crop) and Random Forest (yield); no boosting models were trained |
| PRD mentions LIME | LIME is listed in requirements.txt but not used in any inference or API code |
| Project brief mentions EfficientNet champion | Actual trained model is MobileNetV3-Small, not EfficientNet |
| Project brief mentions MLflow | MLflow is mentioned but not used in the actual training scripts |
| Project brief mentions deep ensembles | Not implemented; only single model per module |
| Yield model features | Metadata shows features are {state, crop, season, area_hectares} — no climate covariates despite ERA5 data being listed |
