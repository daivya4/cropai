# CropAI Implementation Presentation Notes

## 1. Project Introduction

CropAI is an explainable and uncertainty-aware agricultural decision-support platform. It provides three machine-learning utilities:

1. Disease diagnosis from a crop leaf image.
2. Crop recommendation from soil and environmental measurements.
3. Agricultural yield prediction from location, crop, season, and cultivated area.

The main design principle is that the system should not only provide a prediction. It should also communicate:

- Why the model made the prediction.
- How confident or uncertain the model is.
- What information influenced the result.

CropAI is decision-support software. It does not replace agronomists, laboratory testing, or professional agricultural advice.

---

## 2. High-Level System Architecture

```text
React/Vite Website
        |
        | Axios HTTP requests
        v
FastAPI Backend
        |
        +-- Disease inference service
        +-- Crop recommendation service
        +-- Yield prediction service
        |
        +-- Serialized model artifacts
        +-- Explainability layer
        +-- Uncertainty layer
```

The backend application is implemented in `api/main.py`. The React client communicates with it through `frontend/src/api/client.js`.

The main API routes are:

```text
GET  /health
POST /api/v1/disease/predict
POST /api/v1/crop/recommend
POST /api/v1/yield/predict
```

### Backend startup flow

When FastAPI starts:

1. The application enters its lifespan startup function.
2. The disease, crop, and yield services are loaded.
3. Model artifacts are read from the `artifacts/` directory.
4. Models remain in memory so every request does not need to reload them.
5. `/health` can report whether the services are available.

This architecture keeps the user interface separate from machine-learning implementation. A model can be replaced without redesigning the complete frontend.

---

## 3. Data Sources and Dataset Sizes

### Disease data

The disease pipeline uses the colour PlantVillage dataset.

- 54,305 processed image records.
- 38 disease or healthy classes.
- Each CSV row contains an image path and its class label.
- Images remain in the raw data directory; processed CSV files act as manifests.

Examples of classes include Apple scab, Apple black rot, Tomato late blight, Tomato healthy, Corn common rust, and Potato early blight.

### Crop recommendation data

The crop recommendation dataset contains 2,200 records and 22 crop classes. Its input columns are:

- Nitrogen.
- Phosphorus.
- Potassium.
- Temperature.
- Humidity.
- Soil pH.
- Rainfall.
- Crop label.

### Yield data

The yield dataset contains Indian agricultural production records with:

- State.
- District.
- Year.
- Season.
- Crop.
- Cultivated area.
- Production.

Yield is derived as:

```text
yield tonnes/hectare = production tonnes / cultivated area hectares
```

The current live yield model uses state, crop, season, and area. The current implementation does not use rainfall or temperature, although those features appear in the broader product documentation.

---

## 4. Data Cleaning and Splitting

The preparation code is in `scripts/prepare_real_data.py`.

### Recommendation cleaning

The original columns `N`, `P`, and `K` are renamed to `nitrogen`, `phosphorus`, and `potassium`. Crop labels are stripped of surrounding whitespace and converted to lowercase. The script verifies that expected columns exist and rejects missing values.

The data uses a deterministic stratified 70/15/15 split:

- Training: 1,540 rows.
- Validation: 330 rows.
- Test: 330 rows.

Stratification preserves the 22 crop classes across the partitions.

### Disease cleaning

The preparation script searches the PlantVillage class folders and accepts JPG, JPEG, and PNG images. It checks that images exist and that every class has enough samples for splitting.

The disease data also uses a deterministic stratified 70/15/15 split:

- Training: 38,013 images.
- Validation: 8,146 images.
- Test: 8,146 images.

### Yield cleaning

The yield preparation process:

1. Renames source columns.
2. Trims whitespace from text fields.
3. Removes rows with missing required values.
4. Removes rows with zero or negative cultivated area.
5. Removes rows with negative production.
6. Calculates yield per hectare.
7. Creates a chronological split.

The yield split is not random:

- Training: years before 2014.
- Validation: 2014.
- Test: 2015.

This is important because a model should not learn from future years when it is evaluated on earlier years. It reduces temporal leakage.

The processed yield files contain:

- Training: 230,985 rows.
- Validation: 10,815 rows.
- Test: 561 rows.

---

## 5. Utility One: Disease Diagnosis

### User input

The user uploads a JPG, PNG, or WebP image. The API also enforces a maximum file size of 5 MB.

### Preprocessing

The image is:

1. Converted to RGB.
2. Resized to 256 pixels.
3. Centre-cropped to 224 x 224 pixels.
4. Converted to a tensor.
5. Normalized using ImageNet mean and standard deviation values.

During training, augmentation is used:

- Random resized crop.
- Random horizontal flip.
- Colour jitter.
- Normalization.

Augmentation helps the model handle changes in orientation, brightness, contrast, and image composition.

### Model

The implemented model is MobileNetV3-Small pretrained on ImageNet and fine-tuned for the 38 PlantVillage classes.

MobileNetV3-Small is a lightweight convolutional neural network. It learns visual patterns through convolutional layers, such as:

- Edges.
- Textures.
- Leaf shape.
- Discolouration.
- Spots and lesions.

The final classifier layer is replaced so it outputs 38 agricultural classes instead of ImageNet classes.

Training uses:

- Cross-entropy loss.
- Label smoothing of 0.1.
- AdamW optimizer.
- Learning rate of 3e-4.
- Weight decay of 1e-4.
- Cosine learning-rate schedule.
- Five epochs.
- Random seed 42.

### Reported performance

The saved disease metadata reports:

- Test accuracy: approximately 99.17%.
- Macro F1: approximately 98.46%.
- Macro precision: approximately 99.02%.
- Macro recall: approximately 98.10%.
- Best validation accuracy: approximately 99.25%.

These results are based on PlantVillage-style data. Real mobile photographs may be more difficult because of lighting, backgrounds, camera quality, and disease variation.

---

## 6. Disease Uncertainty: MC Dropout

The disease service runs Monte Carlo Dropout uncertainty estimation.

The process is:

1. Dropout layers are kept active during inference.
2. The same image is evaluated ten times.
3. Each pass produces a slightly different probability distribution.
4. The ten distributions are averaged.
5. The averaged probabilities are used for the final prediction.

The system calculates predictive entropy:

```text
entropy = -sum(probability * log2(probability))
```

Low entropy means the probability is concentrated around one class. High entropy means the model is uncertain because several classes have similar probabilities.

The API returns:

- Entropy.
- Normalized entropy.
- Reliability rating.
- The method name: `mc_dropout`.

The reliability rating is:

- High when normalized entropy is below 0.4.
- Medium when normalized entropy is below 0.7.
- Low otherwise.

### Presentation wording

“MC Dropout gives us a practical estimate of predictive uncertainty by observing how much the model’s output changes over multiple stochastic passes.”

---

## 7. Disease Explainable AI: Grad-CAM

Grad-CAM is used because disease diagnosis is an image problem. It produces a spatial explanation rather than only a list of feature values.

The process is:

1. Select the final convolutional layer.
2. Run the image through the model.
3. Select the score of the predicted class.
4. Backpropagate that score.
5. Capture the feature activations and their gradients.
6. Calculate importance weights from the gradients.
7. Combine the feature maps.
8. Apply ReLU to retain positive evidence.
9. Normalize the heatmap.
10. Resize and overlay the heatmap on the original image.

The website shows this as a coloured overlay. Bright regions indicate areas that contributed more strongly to the model’s prediction.

Important limitation:

> Grad-CAM explains which image regions influenced the model. It does not prove that those regions are biologically causal or that the diagnosis is clinically confirmed.

---

## 8. Utility Two: Crop Recommendation

### User input

The website provides sliders for:

- Nitrogen.
- Phosphorus.
- Potassium.
- Temperature.
- Humidity.
- Soil pH.
- Rainfall.

The API validates the input ranges before inference.

### Preprocessing

The input vector is ordered consistently and transformed with `StandardScaler`:

```text
z = (value - training mean) / training standard deviation
```

The crop labels are encoded into numeric class IDs using `LabelEncoder`.

### Model

The implemented classifier is a calibrated Random Forest.

A Random Forest is an ensemble of decision trees. Each tree learns different threshold-based relationships between soil/weather values and crop labels. The forest combines the decisions of all trees.

The implementation uses:

- 500 decision trees.
- Balanced class weights.
- Random seed 42.

The model produces a probability distribution across all 22 crops.

### Probability calibration

Raw model probabilities may not represent real-world correctness. For example, a raw 90% probability does not always mean the prediction is correct 90% of the time.

The system applies sigmoid calibration using `CalibratedClassifierCV`. This adjusts the output probabilities to better match observed validation behaviour.

The UI calls this value the calibrated probability.

### Reported performance

The crop model metadata reports:

- Test accuracy: 100%.
- Macro F1: 100%.
- Top-3 accuracy: 100%.
- Top-5 accuracy: 100%.
- Expected Calibration Error: approximately 0.0755.

The perfect test scores should be interpreted carefully because the dataset is clean and structured. Field performance may be lower.

---

## 9. Crop Explainable AI: SHAP

SHAP means Shapley Additive Explanations. It explains how individual input features affected a particular crop recommendation.

For example:

- High rainfall may push the prediction toward rice.
- A certain pH value may support or oppose a crop.
- Temperature may reduce the probability of a cool-season crop.
- Nitrogen, phosphorus, or potassium may increase suitability.

A positive SHAP value pushes the prediction toward the selected crop. A negative SHAP value pushes it away from the selected crop.

The website displays:

- Recommended crop.
- Calibrated probability.
- Top three alternative crops.
- SHAP feature attribution chart.
- Input values beside the feature names.

This helps answer:

> “Why did the model recommend this crop for these conditions?”

---

## 10. Utility Three: Yield Prediction

### User input

The yield screen accepts:

- State.
- Crop.
- Season.
- Cultivated area in hectares.
- Requested confidence level: 80%, 90%, or 95%.

### Preprocessing

Categorical variables are one-hot encoded:

- State.
- Crop.
- Season.

The numeric area feature is standardized.

### Model

The implemented model is a Random Forest regressor inside a scikit-learn pipeline.

Each tree predicts a numerical yield. The forest averages the predictions from all trees.

The model uses:

- 150 trees.
- Maximum depth of 14.
- Minimum two samples per leaf.
- Random seed 42.

### Log transformation

Yield values can have a large range. The model is trained on:

```text
log1p(yield)
```

The prediction is converted back with:

```text
expm1(prediction)
```

This makes the model less sensitive to extreme yield values.

### Reported performance

The saved metadata reports:

- MAE: approximately 1.14.
- RMSE: approximately 2.99.
- R-squared: approximately 0.947.
- 90% conformal coverage: approximately 94.83%.
- Average interval width: approximately 7.41 tonnes/hectare.

---

## 11. Yield Uncertainty: Conformal Prediction

The yield model stores absolute validation residuals:

```text
residual = absolute(actual yield - predicted yield)
```

The residual distribution is used to calculate an error margin for a requested confidence level.

The final interval is:

```text
lower bound = predicted yield - error margin
upper bound = predicted yield + error margin
```

The lower bound is clipped at zero because yield cannot be negative.

For example:

```text
Predicted yield: 4.8 tonnes/hectare
90% interval:    3.2 to 6.4 tonnes/hectare
```

The interval communicates that the model’s point estimate has uncertainty around it.

Accurate presentation wording:

> “The conformal interval is calibrated using validation errors and is intended to achieve the requested empirical coverage under similar data conditions.”

Avoid claiming that every individual prediction is mathematically guaranteed to contain the true yield.

---

## 12. Yield Explainable AI: SHAP

SHAP is applied to the Random Forest regressor after preprocessing.

The explanation can include encoded features such as:

- `state_Punjab`.
- `crop_Rice`.
- `season_Kharif`.
- `area_hectares`.

Positive SHAP values push the predicted yield upward. Negative SHAP values push it downward.

The website displays a feature influence chart showing which inputs had the largest effect on that particular yield estimate.

---

## 13. Website Walkthrough

The React application is in `frontend/src/`.

It contains four views:

1. Overview.
2. Disease Diagnosis.
3. Crop Recommendation.
4. Yield Prediction.

### Header and navigation

The header displays:

- CropAI brand.
- Version label.
- Decoupled ML serving platform description.
- Light/dark theme toggle.

The navigation bar contains four tabs:

- Overview.
- Disease Diagnosis.
- Crop Recommendation.
- Yield Prediction.

### Overview dashboard

The overview displays:

- Crop recommendation metric.
- Disease diagnosis metric.
- Yield R-squared metric.
- Conformal coverage metric.
- Launch cards for the three utilities.

The metric values on this page are currently hardcoded display values rather than being fetched dynamically from the backend.

### Disease Diagnosis page

The user:

1. Uploads or drops a leaf image.
2. Sees a preview.
3. Clicks Execute Diagnosis.
4. Receives the API response.

The page displays:

- Predicted disease.
- Confidence score.
- Predictive entropy.
- Normalized entropy.
- Reliability rating.
- Top four probability predictions.
- Grad-CAM visual explanation.

The image response contains the Grad-CAM overlay as a Base64-encoded PNG. The browser converts that Base64 value into an image.

### Crop Recommendation page

The user adjusts soil and climate sliders, then clicks Compute Crop Recommendation.

The page displays:

- Recommended crop.
- Calibrated probability.
- Top three alternatives.
- SHAP feature attribution chart.

The chart uses positive and negative visual styles to indicate whether a feature supports or opposes the selected crop.

### Yield Prediction page

The user selects a state, crop, season, area, and confidence level.

The page displays:

- Point yield estimate.
- Conformal lower and upper bounds.
- Confidence level.
- Explanation of feature influence using SHAP.

---

## 14. API Request Flow

### Disease request

The browser sends a multipart form containing the image:

```text
POST /api/v1/disease/predict
```

The backend validates the file, runs inference, generates MC Dropout uncertainty, creates Grad-CAM, converts the overlay to Base64, and returns JSON.

### Crop request

The browser sends JSON containing the seven numeric features:

```text
POST /api/v1/crop/recommend
```

The backend validates the request, scales the values, predicts probabilities, calibrates the result, computes SHAP contributions, and returns JSON.

### Yield request

The browser sends JSON containing state, crop, season, area, and confidence level:

```text
POST /api/v1/yield/predict
```

The backend predicts yield, constructs the conformal interval, computes SHAP contributions, and returns JSON.

---

## 15. Validation and Tests

The tests are in `tests/test_api.py`.

They cover:

- Health endpoint.
- Valid crop recommendation.
- Invalid crop values.
- Missing crop parameters.
- Valid yield prediction.
- Invalid yield area.
- Invalid disease file format.
- Valid disease image.

The tests check both HTTP status codes and response content, including uncertainty and explanation fields.

---

## 16. Deployment Notes

The project includes Docker configuration for an API service on port 8000 and a frontend service on port 8501.

There are currently two frontend implementations in the repository:

1. React/Vite under `frontend/`.
2. Streamlit under `app/`.

The existing Docker Compose file currently launches Streamlit, while the more developed website interface is the React/Vite application.

The Streamlit entry file currently contains unresolved merge-conflict markers, so this should be mentioned as a repository cleanup item rather than presented as a finished deployment path.

---

## 17. Important Limitations

- The system is decision-support software, not an autonomous farming system.
- PlantVillage performance may not represent real-world mobile images.
- Crop recommendation results depend on the coverage and quality of the recommendation dataset.
- The current yield model does not use rainfall or temperature.
- Grad-CAM shows model influence, not biological causation.
- SHAP explains model behaviour, not guaranteed agronomic relationships.
- Confidence and uncertainty are different concepts.
- Conformal intervals provide calibrated coverage under similar data conditions, not an absolute guarantee for every prediction.
- Overview dashboard metrics are currently hardcoded.
- The product documentation mentions additional models and techniques, but the live implementation uses MobileNetV3-Small, calibrated Random Forest classification, and Random Forest regression with conformal residual intervals.

---

## 18. Recommended Presentation Script

“CropAI is an API-first agricultural decision-support platform with three independent machine-learning pipelines. The frontend collects either an image or structured agricultural inputs and sends them to FastAPI. FastAPI validates the request and forwards it to the appropriate inference service.

For disease diagnosis, we use a fine-tuned MobileNetV3-Small model for 38 PlantVillage classes. We use MC Dropout to estimate predictive uncertainty and Grad-CAM to show which image regions influenced the diagnosis.

For crop recommendation, we use a calibrated Random Forest classifier on soil and environmental features. The model returns a recommended crop and alternatives. SHAP explains the contribution of nitrogen, phosphorus, potassium, pH, rainfall, temperature, and humidity.

For yield prediction, we use a Random Forest regressor with one-hot encoding for categorical variables and a log-transformed target. Instead of returning only a point estimate, we use conformal residuals to produce a prediction interval. SHAP explains which encoded input features influenced the estimate.

The main value of CropAI is that it combines prediction, explanation, and uncertainty in one interface. This is important in agriculture because users need to understand not only what the model predicts, but also how reliable that prediction is and what influenced it.”

---

## 19. Source Files to Show During the Presentation

- Architecture and startup: `api/main.py`
- Disease API route: `api/routes/disease.py`
- Crop API route: `api/routes/crop.py`
- Yield API route: `api/routes/yield.py`
- Disease training: `training/disease/train_disease.py`
- Crop training: `training/crop/train_crop.py`
- Yield training: `training/yield/train_yield.py`
- Data preparation: `scripts/prepare_real_data.py`
- Disease inference and MC Dropout: `models/disease/inference.py`, `models/disease/uncertainty.py`
- Grad-CAM: `models/disease/explainability.py`
- Crop inference and SHAP: `models/crop/inference.py`, `models/crop/explainability.py`
- Yield inference and SHAP: `models/yield/inference.py`, `models/yield/explainability.py`
- React application: `frontend/src/App.jsx`
- API client: `frontend/src/api/client.js`
- Disease screen: `frontend/src/pages/DiseaseDiagnosis.jsx`
- Crop screen: `frontend/src/pages/CropRecommendation.jsx`
- Yield screen: `frontend/src/pages/YieldPrediction.jsx`
- API tests: `tests/test_api.py`
