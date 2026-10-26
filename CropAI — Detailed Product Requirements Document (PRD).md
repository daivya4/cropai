# CropAI — Detailed Product Requirements Document

**Version:** 1.0  
**Status:** Implementation Ready  
**Product:** CropAI  
**Primary Platform:** Web application  
**Backend:** FastAPI  
**Frontend:** Streamlit  
**ML Stack:** PyTorch / scikit-learn / XGBoost  
**Deployment Target:** Dockerized application  
**Primary Objective:** Build an explainable, uncertainty-aware agricultural AI platform that provides crop disease diagnosis, crop recommendation, and yield prediction from structured and visual agricultural data.

---

# 1. Product Overview

CropAI is an AI-powered agricultural decision-support platform consisting of three independent but complementary ML modules:

1. **Crop Disease Diagnosis**
   - Input: crop leaf image
   - Output: predicted disease/class, confidence, uncertainty, and visual explanation

2. **Crop Recommendation**
   - Input: soil and environmental parameters
   - Output: recommended crop with probability/confidence and explanation

3. **Yield Prediction**
   - Input: agricultural/environmental parameters
   - Output: predicted crop yield with uncertainty interval and feature contribution explanation

The platform must prioritize:

- Prediction quality
- Explainability
- Uncertainty estimation
- Calibration
- Reproducibility
- Clean modular architecture
- Practical usability
- API-first ML serving
- Clear separation between training and inference

---

# 2. Problem Statement

Agricultural decisions often depend on incomplete information, expert judgment, and manual inspection.

CropAI aims to provide a single interface through which a user can:

- Identify crop diseases from leaf images
- Determine suitable crops based on soil and environmental conditions
- Estimate expected crop yield
- Understand why a model produced a prediction
- Determine how reliable that prediction is

The system is intended as a **decision-support tool**, not as an autonomous replacement for agricultural experts.

---

# 3. Goals

## 3.1 Primary Goals

The system must:

- Provide three production-style ML inference pipelines.
- Expose all models through a FastAPI backend.
- Provide an accessible Streamlit frontend.
- Store trained model artifacts separately from source code.
- Produce explanations alongside predictions.
- Produce uncertainty estimates where applicable.
- Evaluate and calibrate model confidence.
- Include automated tests for important components.
- Be reproducible from a clean environment.
- Run through Docker.

## 3.2 Secondary Goals

The system should:

- Provide useful visualization of predictions.
- Display model metrics.
- Provide confidence/uncertainty indicators.
- Support model versioning.
- Support future replacement of individual models without redesigning the application.

## 3.3 Non-Goals

The first version will not:

- Automatically control irrigation systems.
- Automatically apply pesticides/fertilizers.
- Guarantee agricultural outcomes.
- Replace professional agronomists.
- Provide financial or insurance recommendations.
- Require real-time IoT hardware.
- Build a complete farm-management platform.

---

# 4. Target Users

## 4.1 Farmer

Primary needs:

- Identify disease from a leaf image.
- Understand whether the diagnosis is reliable.
- Get crop recommendations from soil/environmental conditions.
- Estimate potential yield.

## 4.2 Agricultural Student / Researcher

Needs:

- Experiment with agricultural ML models.
- Inspect predictions and explanations.
- Compare model performance.
- Study uncertainty and calibration.

## 4.3 Agricultural Professional

Needs:

- Rapid preliminary diagnosis.
- Data-driven crop recommendations.
- Yield estimates.
- Model explanations that can be reviewed before taking action.

## 4.4 Developer / ML Engineer

Needs:

- Clean training pipelines.
- Reproducible experiments.
- Modular inference APIs.
- Testable model components.
- Easy model replacement.

---

# 5. Product Architecture

The system follows a modular architecture:

```text
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      Disease Service    Crop Service      Yield Service
             │                 │                 │
             ▼                 ▼                 ▼
       CNN / ViT Model   Tabular Model      Regression Model
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                     Explanation Layer
                               │
                               ▼
                    Uncertainty Layer
                               │
                               ▼
                       Model Artifacts
```

---

# 6. Repository Structure

The implementation should follow:

```text
cropai/
│
├── api/
│   ├── main.py
│   ├── routes/
│   │   ├── disease.py
│   │   ├── crop.py
│   │   └── yield.py
│   ├── schemas/
│   ├── services/
│   └── dependencies.py
│
├── models/
│   ├── disease/
│   │   ├── model.py
│   │   ├── inference.py
│   │   ├── explainability.py
│   │   └── uncertainty.py
│   │
│   ├── crop/
│   │   ├── model.py
│   │   ├── inference.py
│   │   ├── explainability.py
│   │   └── uncertainty.py
│   │
│   └── yield/
│       ├── model.py
│       ├── inference.py
│       ├── explainability.py
│       └── uncertainty.py
│
├── training/
│   ├── disease/
│   ├── crop/
│   └── yield/
│
├── evaluation/
│   ├── metrics.py
│   ├── calibration.py
│   └── reports.py
│
├── app/
│   ├── streamlit_app.py
│   ├── pages/
│   │   ├── disease.py
│   │   ├── crop.py
│   │   └── yield.py
│   └── components/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── artifacts/
│   ├── disease/
│   ├── crop/
│   └── yield/
│
├── tests/
│   ├── test_api.py
│   ├── test_disease.py
│   ├── test_crop.py
│   └── test_yield.py
│
├── configs/
│   └── config.yaml
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 7. Core Product Modules

# 7.1 Module A — Crop Disease Diagnosis

## Objective

Classify a crop leaf image into the appropriate disease/category.

## Input

The user uploads an image.

Supported formats:

- JPG
- JPEG
- PNG
- WebP

The API should validate:

- File type
- File size
- Image readability
- Minimum image dimensions

## Processing Pipeline

```text
Upload Image
     ↓
Validate Image
     ↓
Resize
     ↓
Normalize
     ↓
Model Inference
     ↓
Probability Distribution
     ↓
Prediction
     ↓
Uncertainty Estimation
     ↓
Grad-CAM / Explanation
     ↓
Response
```

## Model Requirements

The system should support a transfer-learning CNN.

Recommended baseline:

- EfficientNet-B0/B1
- ResNet18/34
- MobileNetV3

A lightweight architecture should be preferred for deployment.

Optional advanced model:

- Vision Transformer

## Training Requirements

Training pipeline must include:

- Dataset loading
- Train/validation/test split
- Class balancing if required
- Image augmentation
- Model initialization
- Training
- Validation
- Checkpointing
- Early stopping
- Metric logging
- Final evaluation

Recommended augmentations:

- Random crop
- Horizontal flip
- Small rotation
- Color jitter
- Random resized crop

Augmentation must not destroy disease-specific visual features.

## Required Metrics

At minimum:

- Accuracy
- Precision
- Recall
- F1-score
- Macro F1
- Confusion matrix

For imbalanced datasets:

- Balanced accuracy
- Per-class recall

## Output

The API must return:

```json
{
  "prediction": "Tomato___Late_blight",
  "confidence": 0.94,
  "top_predictions": [
    {
      "class": "Tomato___Late_blight",
      "probability": 0.94
    },
    {
      "class": "Tomato___Early_blight",
      "probability": 0.03
    }
  ],
  "uncertainty": {
    "method": "entropy",
    "score": 0.12
  },
  "explanation_available": true
}
```

## Explainability

The system must generate a Grad-CAM heatmap.

The UI should show:

- Original image
- Predicted disease
- Heatmap
- Overlay of heatmap on original image

The purpose is to indicate which regions influenced the prediction.

The explanation must not be presented as proof that the model is correct.

## Uncertainty

At minimum implement one uncertainty method.

Preferred options:

- Predictive entropy
- Monte Carlo dropout
- Deep ensemble

The production baseline should use calibrated confidence where possible.

---

# 7.2 Module B — Crop Recommendation

## Objective

Recommend a suitable crop using structured agricultural/environmental data.

## Input Features

The system should support the available dataset features, potentially including:

- Nitrogen
- Phosphorus
- Potassium
- Temperature
- Humidity
- pH
- Rainfall

Additional features may be supported if present in the selected dataset.

## Input Validation

Each feature must have:

- Required/optional status
- Numeric type
- Valid range

Invalid values should generate a clear API validation error.

Example:

```json
{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "temperature": 21.5,
  "humidity": 82,
  "ph": 6.5,
  "rainfall": 202
}
```

## Model Options

Candidate models:

- Random Forest
- XGBoost
- LightGBM
- CatBoost
- Neural Network

The initial implementation should establish a strong tree-based baseline.

Preferred baseline:

**XGBoost or Random Forest**

## Training Pipeline

```text
Raw Dataset
     ↓
Validation
     ↓
Missing-value handling
     ↓
Feature analysis
     ↓
Train/Validation/Test Split
     ↓
Model Training
     ↓
Hyperparameter Optimization
     ↓
Evaluation
     ↓
Calibration
     ↓
Artifact Export
```

## Required Metrics

- Accuracy
- Macro F1
- Weighted F1
- Precision
- Recall
- Confusion matrix

Additional:

- Top-3 accuracy
- Top-5 accuracy

Top-k accuracy is particularly useful because multiple crops may be reasonable under similar conditions.

## Output

Example:

```json
{
  "recommended_crop": "Rice",
  "confidence": 0.87,
  "top_recommendations": [
    {
      "crop": "Rice",
      "probability": 0.87
    },
    {
      "crop": "Maize",
      "probability": 0.06
    },
    {
      "crop": "Cotton",
      "probability": 0.03
    }
  ],
  "explanation": {
    "top_features": [
      {
        "feature": "rainfall",
        "importance": 0.31
      },
      {
        "feature": "humidity",
        "importance": 0.21
      }
    ]
  }
}
```

## Explainability

Preferred method:

- SHAP

The UI should show:

- Top positive features
- Top negative features
- Feature importance visualization

Example:

```text
Rainfall       ████████████
Humidity       █████████
Nitrogen       ███████
Temperature    █████
pH             ███
```

---

# 7.3 Module C — Yield Prediction

## Objective

Predict expected crop yield from agricultural and environmental variables.

## Input

Potential features include:

- Crop
- State/region
- Season
- Area
- Production-related historical variables
- Rainfall
- Temperature
- Fertilizer usage
- Pesticide usage
- Soil parameters

The exact feature set must match the selected dataset.

## Important Requirement

The system must avoid target leakage.

Features that directly reveal the target or are generated after the target event must not be used.

## Model Candidates

Baseline:

- Linear Regression
- Random Forest Regressor

Advanced:

- XGBoost Regressor
- LightGBM
- CatBoost
- Neural Network

The selected final model must be justified through evaluation.

## Metrics

Required:

- MAE
- RMSE
- R²

Optional:

- MAPE
- Median Absolute Error

## Output

```json
{
  "predicted_yield": 4.82,
  "unit": "tonnes/hectare",
  "interval": {
    "lower": 4.12,
    "upper": 5.54,
    "confidence_level": 0.90
  },
  "explanation": {
    "top_features": [
      {
        "feature": "rainfall",
        "importance": 0.28
      },
      {
        "feature": "area",
        "importance": 0.19
      }
    ]
  }
}
```

## Uncertainty

Yield predictions must include an uncertainty estimate.

Preferred methods:

- Quantile regression
- Conformal prediction
- Bootstrap prediction intervals

The initial production implementation should use **conformal prediction** if feasible because it provides an interpretable prediction interval.

---

# 8. Dataset Requirements

Each module must document:

- Dataset name
- Dataset source
- License
- Number of samples
- Number of classes/features
- Train/validation/test split
- Preprocessing
- Known limitations

Dataset licenses must permit the intended usage.

Dataset provenance must be documented in:

```text
data/README.md
```

No dataset should be committed to Git unless its size and license permit it.

Large datasets should be downloaded separately.

---

# 9. Data Processing Requirements

All preprocessing required during training must be reproducible during inference.

The system must avoid:

```text
Training preprocessing ≠ Inference preprocessing
```

Instead:

```text
Raw Input
    ↓
Shared preprocessing
    ↓
Model
```

For tabular models, preprocessing artifacts must be saved.

Examples:

- StandardScaler
- LabelEncoder
- OneHotEncoder
- Feature ordering
- Imputation values

For image models:

- Image size
- Normalization constants
- Color-space assumptions
- Class mapping

must be stored alongside the model.

---

# 10. Model Artifact Requirements

Every trained model must have a corresponding artifact directory.

Example:

```text
artifacts/disease/
├── model.pt
├── class_names.json
├── preprocessing.json
├── config.json
└── metadata.json
```

For tabular models:

```text
artifacts/crop/
├── model.pkl
├── scaler.pkl
├── encoder.pkl
├── feature_schema.json
└── metadata.json
```

Metadata should include:

```json
{
  "model_name": "xgboost",
  "version": "1.0",
  "dataset": "dataset-name",
  "trained_at": "timestamp",
  "features": [],
  "metrics": {},
  "calibration": {}
}
```

---

# 11. Explainability Requirements

Explainability is a core product requirement rather than an optional visualization.

## Disease Model

Use:

- Grad-CAM

Output:

- Heatmap
- Overlay

## Crop Recommendation

Use:

- SHAP

Output:

- Global feature importance
- Individual prediction explanation

## Yield Prediction

Use:

- SHAP

Output:

- Feature contributions
- Prediction explanation

The system must clearly distinguish:

**Prediction**

from

**Explanation of model behavior**

The UI must not claim that explanations establish causal relationships.

---

# 12. Uncertainty Requirements

Confidence must not automatically be treated as correctness.

The platform should distinguish:

- Confidence
- Uncertainty
- Calibration

## Disease

Possible implementation:

- Softmax confidence
- Predictive entropy
- MC Dropout

## Crop Recommendation

Possible implementation:

- Calibrated class probabilities
- Temperature scaling
- Isotonic regression

## Yield

Preferred:

- Conformal prediction interval

Example UI:

```text
Prediction: Rice
Confidence: 87%

Confidence level:
█████████████████░░░

Reliability:
High
```

For uncertain cases:

```text
Prediction: Rice
Confidence: 51%

Reliability:
Low

Consider collecting additional soil/environmental information.
```

---

# 13. Calibration Requirements

The system should measure whether predicted probabilities correspond to actual correctness.

Required metrics where applicable:

- Expected Calibration Error (ECE)
- Brier score
- Reliability diagram

Calibration should be performed on a validation/calibration split and never using the final test set.

The final test set must remain untouched until final evaluation.

---

# 14. API Requirements

FastAPI is the central serving layer.

Base path:

```text
/api/v1
```

## Health Endpoint

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Disease Endpoint

```http
POST /api/v1/disease/predict
```

Content type:

```text
multipart/form-data
```

Input:

```text
image=<file>
```

Response:

```json
{
  "prediction": "...",
  "confidence": 0.94,
  "top_predictions": [],
  "uncertainty": {},
  "explanation": {}
}
```

## Crop Recommendation Endpoint

```http
POST /api/v1/crop/recommend
```

Input:

```json
{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "temperature": 21.5,
  "humidity": 82,
  "ph": 6.5,
  "rainfall": 202
}
```

## Yield Prediction Endpoint

```http
POST /api/v1/yield/predict
```

Input:

```json
{
  "crop": "Rice",
  "season": "Kharif",
  "rainfall": 1200,
  "temperature": 28,
  "area": 2.5
}
```

The exact schema must be adapted to the final dataset.

---

# 15. API Error Handling

The API must return meaningful errors.

Examples:

### Invalid Image

```http
400 Bad Request
```

```json
{
  "detail": "Unsupported image format."
}
```

### Missing Feature

```http
422 Unprocessable Entity
```

```json
{
  "detail": "Field 'rainfall' is required."
}
```

### Model Failure

```http
500 Internal Server Error
```

The API should log the internal exception while returning a safe user-facing message.

---

# 16. Streamlit Requirements

The Streamlit application acts as the user-facing interface.

## Main Navigation

```text
CropAI
│
├── Disease Diagnosis
├── Crop Recommendation
└── Yield Prediction
```

---

# 17. Disease Diagnosis UI

The page must include:

### Input

- Image uploader
- Supported format information
- Predict button

### Output

- Uploaded image
- Predicted disease
- Confidence
- Top predictions
- Uncertainty
- Grad-CAM visualization
- Explanation text

Example layout:

```text
┌──────────────────────┐
│ Upload Leaf Image    │
└──────────────────────┘

        [Predict]

Prediction
Tomato Late Blight

Confidence
94%

Top Predictions
1. Late Blight      94%
2. Early Blight      3%
3. Healthy           2%

Explanation
[Grad-CAM Image]
```

---

# 18. Crop Recommendation UI

Input form:

```text
Nitrogen
Phosphorus
Potassium
Temperature
Humidity
pH
Rainfall
```

Button:

```text
Recommend Crop
```

Output:

- Recommended crop
- Confidence
- Top recommendations
- Feature importance
- SHAP explanation

---

# 19. Yield Prediction UI

Input form should contain the required dataset-specific features.

Output:

- Predicted yield
- Unit
- Prediction interval
- Confidence level
- Feature contribution chart
- Important input factors

---

# 20. User Experience Requirements

The UI should:

- Be simple.
- Avoid unnecessary agricultural jargon.
- Clearly label units.
- Display validation errors beside relevant inputs.
- Display loading state during inference.
- Avoid showing raw model outputs without explanation.
- Never imply certainty where uncertainty exists.

The system should remain usable on a normal laptop screen.

---

# 21. Model Loading

Models must be loaded once when the application starts.

The system must not reload the model for every request.

Preferred pattern:

```text
Application startup
       ↓
Load model artifacts
       ↓
Keep models in memory
       ↓
Receive requests
       ↓
Run inference
```

For Streamlit, use appropriate caching mechanisms for model objects.

---

# 22. Performance Requirements

Target inference latency on a typical development machine:

### Disease

Target:

**< 2 seconds/image**

### Crop Recommendation

Target:

**< 500 ms**

### Yield Prediction

Target:

**< 500 ms**

These targets exclude large network upload delays.

The application should avoid unnecessary repeated preprocessing.

---

# 23. Security Requirements

The API must:

- Validate uploaded files.
- Restrict maximum image size.
- Reject unsupported formats.
- Avoid executing uploaded content.
- Sanitize filenames.
- Avoid exposing internal stack traces.
- Validate numerical ranges.

The service should not persist user-uploaded images unless explicitly required.

---

# 24. Logging

Application logs should include:

- Request timestamp
- Endpoint
- Request status
- Inference duration
- Model version
- Error information

Do not log sensitive user data unnecessarily.

Example:

```text
2026-08-20 15:42:11
POST /api/v1/disease/predict
model=disease_v1
latency=0.82s
status=200
```

---

# 25. Testing Requirements

Tests are mandatory.

## Unit Tests

Test:

- Preprocessing
- Input validation
- Model loading
- Prediction formatting
- Uncertainty calculations
- Explanation generation

## API Tests

Test:

```text
GET /health
POST /disease/predict
POST /crop/recommend
POST /yield/predict
```

Include:

- Valid input
- Missing input
- Invalid input
- Invalid file
- Model failure

## Model Tests

At minimum:

- Model loads successfully.
- Input dimensions are correct.
- Output dimensions are correct.
- Prediction probabilities sum appropriately where applicable.
- Regression output is numeric.

---

# 26. Evaluation Requirements

Each model must produce an evaluation report.

## Disease Report

Include:

- Accuracy
- Precision
- Recall
- Macro F1
- Confusion matrix
- Per-class performance
- Calibration
- Example Grad-CAM outputs

## Crop Report

Include:

- Accuracy
- Macro F1
- Top-k accuracy
- Confusion matrix
- Calibration
- SHAP analysis

## Yield Report

Include:

- MAE
- RMSE
- R²
- Prediction interval coverage
- Mean interval width
- SHAP analysis

---

# 27. Experiment Tracking

Each training run should record:

```text
Experiment ID
Dataset version
Model architecture
Hyperparameters
Training duration
Metrics
Random seed
Preprocessing configuration
Artifact location
```

At minimum, these can be stored in JSON/CSV files.

Optional future integration:

- MLflow
- Weights & Biases

---

# 28. Reproducibility

Training must use explicit random seeds where possible.

Example:

```text
seed = 42
```

The project should provide documented commands for:

```text
Install dependencies
Download datasets
Prepare datasets
Train models
Evaluate models
Run API
Run Streamlit
Run tests
Run Docker
```

---

# 29. Docker Requirements

The project must be runnable through Docker.

Expected services:

```text
docker-compose
│
├── api
└── frontend
```

Example:

```text
Browser
   ↓
Streamlit
   ↓
FastAPI
   ↓
Models
```

Environment-specific configuration should be handled through environment variables/configuration rather than hardcoded values.

---

# 30. Configuration

Configuration should include:

```yaml
models:
  disease:
    path: artifacts/disease/model.pt

  crop:
    path: artifacts/crop/model.pkl

  yield:
    path: artifacts/yield/model.pkl

api:
  host: 0.0.0.0
  port: 8000
```

Do not hardcode local machine paths.

---

# 31. Model Versioning

Every model must have a version.

Example:

```text
disease_v1
crop_v1
yield_v1
```

API responses should optionally expose:

```json
{
  "model_version": "disease_v1"
}
```

This is important when predictions need to be reproduced later.

---

# 32. Documentation Requirements

The README must contain:

## Project Overview

What CropAI does.

## Architecture

System architecture diagram.

## Setup

Installation instructions.

## Dataset Setup

Where datasets come from and how to obtain them.

## Training

Commands for training each model.

## Evaluation

Commands for generating metrics.

## Running API

Example:

```bash
uvicorn api.main:app --reload
```

## Running UI

Example:

```bash
streamlit run app/streamlit_app.py
```

## Docker

Commands for building and running the system.

## API Documentation

Endpoints and example requests.

## Model Limitations

Known weaknesses and appropriate usage boundaries.

---

# 33. Acceptance Criteria

The project is considered complete when all of the following are true.

## Disease

- [ ] User can upload a supported leaf image.
- [ ] API returns a disease prediction.
- [ ] API returns confidence.
- [ ] API returns top-k predictions.
- [ ] Uncertainty is calculated.
- [ ] Grad-CAM explanation is generated.
- [ ] Model metrics are documented.
- [ ] Calibration is evaluated.

## Crop Recommendation

- [ ] User can enter soil/environmental parameters.
- [ ] API validates the inputs.
- [ ] Model returns a crop recommendation.
- [ ] Top-k recommendations are available.
- [ ] Confidence is displayed.
- [ ] SHAP explanation is available.
- [ ] Calibration is evaluated.

## Yield Prediction

- [ ] User can enter required agricultural inputs.
- [ ] API validates the inputs.
- [ ] Model returns a numeric yield estimate.
- [ ] Unit is displayed.
- [ ] Prediction interval is returned.
- [ ] Feature contributions are displayed.
- [ ] Regression metrics are documented.

## Platform

- [ ] FastAPI backend works.
- [ ] Streamlit frontend works.
- [ ] API documentation works.
- [ ] Models load successfully.
- [ ] Unit tests pass.
- [ ] API tests pass.
- [ ] Docker build succeeds.
- [ ] Dockerized application runs.
- [ ] README contains complete setup instructions.

---

# 34. Development Phases

## Phase 1 — Project Setup

Tasks:

- Create repository.
- Create Python environment.
- Configure dependencies.
- Create directory structure.
- Configure Git.
- Create initial README.
- Add configuration system.

Deliverable:

**Runnable empty application skeleton.**

---

# Phase 2 — Dataset Preparation

Tasks:

- Select datasets.
- Document licenses.
- Download datasets.
- Inspect distributions.
- Identify missing values.
- Identify class imbalance.
- Build preprocessing pipelines.
- Create reproducible train/validation/test splits.

Deliverable:

**Clean, reproducible datasets.**

---

# Phase 3 — Disease Model

Tasks:

1. Implement dataset loader.
2. Implement image preprocessing.
3. Train baseline CNN.
4. Evaluate baseline.
5. Add transfer learning.
6. Compare models.
7. Select final model.
8. Implement Grad-CAM.
9. Implement uncertainty.
10. Evaluate calibration.
11. Export artifact.

Deliverable:

**Complete disease inference pipeline.**

---

# Phase 4 — Crop Recommendation Model

Tasks:

1. Load dataset.
2. Validate features.
3. Perform exploratory analysis.
4. Train baseline model.
5. Train stronger tree-based model.
6. Compare metrics.
7. Calibrate probabilities.
8. Implement SHAP.
9. Export artifact.

Deliverable:

**Complete crop recommendation pipeline.**

---

# Phase 5 — Yield Model

Tasks:

1. Load dataset.
2. Identify target.
3. Remove leakage.
4. Build preprocessing.
5. Train baseline regression model.
6. Train advanced regression model.
7. Compare metrics.
8. Implement uncertainty intervals.
9. Implement SHAP.
10. Export artifact.

Deliverable:

**Complete yield prediction pipeline.**

---

# Phase 6 — FastAPI

Tasks:

- Create FastAPI application.
- Create Pydantic schemas.
- Create model loading layer.
- Implement disease endpoint.
- Implement crop endpoint.
- Implement yield endpoint.
- Implement health endpoint.
- Add error handling.
- Add logging.
- Add API tests.

Deliverable:

**Complete ML API.**

---

# Phase 7 — Streamlit

Tasks:

- Create navigation.
- Build disease page.
- Build crop recommendation page.
- Build yield page.
- Add result visualization.
- Add explanations.
- Add uncertainty indicators.
- Connect frontend to API.

Deliverable:

**Complete user-facing application.**

---

# Phase 8 — Integration

Tasks:

- Connect all models.
- Validate API/UI contracts.
- Test model loading.
- Test error handling.
- Test complete workflows.
- Fix latency issues.
- Validate explanations.

Deliverable:

**End-to-end CropAI application.**

---

# Phase 9 — Docker

Tasks:

- Create Dockerfile.
- Create docker-compose configuration.
- Configure environment variables.
- Build containers.
- Run complete application.
- Test API from container.
- Test frontend from container.

Deliverable:

**Reproducible containerized deployment.**

---

# 35. Final User Workflow

## Disease Workflow

```text
User opens CropAI
        ↓
Disease Diagnosis
        ↓
Uploads leaf image
        ↓
Clicks Predict
        ↓
API validates image
        ↓
Disease model predicts
        ↓
Uncertainty calculated
        ↓
Grad-CAM generated
        ↓
Result displayed
```

## Crop Workflow

```text
User opens CropAI
        ↓
Crop Recommendation
        ↓
Enters soil/environment values
        ↓
Clicks Recommend
        ↓
API validates input
        ↓
Model predicts
        ↓
Probabilities calibrated
        ↓
SHAP explanation generated
        ↓
Top recommendations displayed
```

## Yield Workflow

```text
User opens CropAI
        ↓
Yield Prediction
        ↓
Enters agricultural data
        ↓
Clicks Predict
        ↓
API validates input
        ↓
Yield model predicts
        ↓
Prediction interval generated
        ↓
SHAP explanation generated
        ↓
Yield + uncertainty displayed
```

---

# 36. Quality Gates

Before moving between phases, the following gates must be satisfied.

## ML Quality Gate

A model cannot be integrated into the API until:

- It beats or reasonably matches the baseline.
- Test evaluation is completed.
- Preprocessing is reproducible.
- Artifact loading works.
- Prediction schema is defined.

## Explainability Quality Gate

Explanations must:

- Generate successfully.
- Correspond to the predicted class/output.
- Not crash on valid inputs.
- Be visually interpretable.

## API Quality Gate

API must:

- Validate inputs.
- Return predictable schemas.
- Handle invalid inputs.
- Load models once.
- Pass automated tests.

## Deployment Quality Gate

Docker must:

- Build successfully.
- Start successfully.
- Load all required artifacts.
- Expose API and frontend.
- Work from a clean environment.

---

# 37. Engineering Principles

The implementation should follow these principles:

### 1. Modular ML

Each model must be independently trainable and deployable.

### 2. Reproducibility

Training should always be reproducible from documented inputs and configuration.

### 3. No Data Leakage

Preprocessing and feature engineering must respect train/test boundaries.

### 4. API-First Inference

Streamlit should not directly implement model logic.

Correct:

```text
Streamlit → FastAPI → Model
```

Avoid:

```text
Streamlit → Model directly
```

### 5. Explainability by Default

Every prediction should provide an explanation where technically applicable.

### 6. Uncertainty by Default

Predictions should communicate reliability rather than presenting raw confidence as absolute truth.

### 7. Model-Agnostic Interfaces

API contracts should remain stable even if the underlying model changes.

### 8. Configuration Over Hardcoding

Paths, model versions, thresholds, and deployment settings should be configurable.

---

# 38. Future Enhancements

These are outside the initial MVP but should be considered during architecture design.

## Advanced Disease Detection

- Object detection
- Segmentation
- Multi-disease classification
- Smartphone camera integration

## Advanced Recommendations

- Fertilizer recommendation
- Irrigation recommendation
- Weather-aware recommendations
- Regional recommendations

## Advanced Yield Prediction

- Time-series forecasting
- Satellite imagery
- Weather APIs
- Historical farm data

## Advanced ML

- Model ensembles
- Bayesian neural networks
- Deep ensembles
- Conformal prediction
- Federated learning

## Platform

- User accounts
- Prediction history
- Farm profiles
- Database
- Cloud deployment
- Monitoring
- Model drift detection
- Automated model retraining

---

# 39. Success Criteria

CropAI succeeds as an MVP when a user can complete all three workflows from one application:

```text
Leaf Image
    ↓
Disease + Confidence + Explanation

Soil/Environment
    ↓
Crop Recommendation + Confidence + Explanation

Agricultural Data
    ↓
Yield + Prediction Interval + Explanation
```

The system should demonstrate not merely that an ML model can make predictions, but that those predictions can be **served, explained, evaluated, calibrated, and communicated responsibly** through a complete software product.

---

# 40. Final Deliverables

The completed repository must contain:

- [ ] Source code
- [ ] Three trained ML models
- [ ] Preprocessing artifacts
- [ ] Model metadata
- [ ] Dataset documentation
- [ ] Training scripts
- [ ] Evaluation scripts
- [ ] Explainability implementation
- [ ] Uncertainty implementation
- [ ] Calibration analysis
- [ ] FastAPI backend
- [ ] Streamlit frontend
- [ ] Automated tests
- [ ] Docker configuration
- [ ] README
- [ ] API documentation
- [ ] Evaluation reports
- [ ] Example inputs/outputs

The final product should be runnable using documented commands without requiring undocumented manual configuration.