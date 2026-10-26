from __future__ import annotations
import os
import json
import time
import random
import pickle
import hashlib
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

# Set seeds
random.seed(42)
np.random.seed(42)

def calculate_ece(probs, labels, n_bins=10):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels)
    
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
            
    return float(ece)

def calculate_top_k_accuracy(probs, labels, k=3):
    top_k_preds = np.argsort(probs, axis=1)[:, -k:]
    correct = 0
    for i in range(len(labels)):
        if labels[i] in top_k_preds[i]:
            correct += 1
    return float(correct / len(labels))

FEATURE_COLUMNS = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN = "label"


def dataset_hash(data_dir: str) -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(data_dir).glob("*.csv")):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def train_crop_model(data_dir="data/processed/recommendation", artifact_dir="artifacts/crop"):
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Load data
    train_df = pd.read_csv(os.path.join(data_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(data_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test.csv"))
    
    missing_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(train_df.columns)
    if missing_columns:
        raise ValueError(f"Training data is missing columns: {sorted(missing_columns)}")

    X_train = train_df[FEATURE_COLUMNS].values
    y_train = train_df[TARGET_COLUMN].values
    
    X_val = val_df[FEATURE_COLUMNS].values
    y_val = val_df[TARGET_COLUMN].values
    
    X_test = test_df[FEATURE_COLUMNS].values
    y_test = test_df[TARGET_COLUMN].values
    
    # Label Encoder
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_val_encoded = le.transform(y_val)
    y_test_encoded = le.transform(y_test)
    
    # Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Base Random Forest model
    base_model = RandomForestClassifier(
        n_estimators=500,
        min_samples_leaf=1,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42
    )
    
    start_time = time.time()
    base_model.fit(X_train_scaled, y_train_encoded)
    
    # Calibrated Classifier
    # Sigmoid calibration is more stable than isotonic calibration for the 15
    # held-out samples available per class in this dataset.
    calibrated_model = CalibratedClassifierCV(
        estimator=FrozenEstimator(base_model),
        method="sigmoid"
    )
    calibrated_model.fit(X_val_scaled, y_val_encoded)
    training_duration = time.time() - start_time
    
    # Predict on test set
    test_probs = calibrated_model.predict_proba(X_test_scaled)
    test_preds = calibrated_model.predict(X_test_scaled)
    
    # Calculate metrics
    acc = accuracy_score(y_test_encoded, test_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test_encoded, test_preds, average="macro", zero_division=0)
    top_3_acc = calculate_top_k_accuracy(test_probs, y_test_encoded, k=3)
    top_5_acc = calculate_top_k_accuracy(test_probs, y_test_encoded, k=5)
    ece = calculate_ece(test_probs, y_test_encoded)
    conf_mat = confusion_matrix(y_test_encoded, test_preds).tolist()
    
    print(f"Test Accuracy: {acc:.4f}")
    print(f"Test Macro F1: {f1:.4f}")
    print(f"Top-3 Accuracy: {top_3_acc:.4f}")
    print(f"Test ECE: {ece:.4f}")
    
    # Save artifacts
    with open(os.path.join(artifact_dir, "model.pkl"), "wb") as f:
        pickle.dump(calibrated_model, f)
    with open(os.path.join(artifact_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    with open(os.path.join(artifact_dir, "label_encoder.pkl"), "wb") as f:
        pickle.dump(le, f)
        
    metadata = {
        "model_name": "random_forest_calibrated",
        "model_version": "crop_v2",
        "dataset": "Kaggle Crop Recommendation Dataset",
        "dataset_hash": dataset_hash(data_dir),
        "git_sha": git_sha(),
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": round(training_duration, 2),
        "random_seed": 42,
        "features": FEATURE_COLUMNS,
        "metrics": {
            "test_accuracy": float(acc),
            "macro_precision": float(precision),
            "macro_recall": float(recall),
            "macro_f1": float(f1),
            "top_3_accuracy": float(top_3_acc),
            "top_5_accuracy": float(top_5_acc),
            "ece": ece
        },
        "confusion_matrix": conf_mat,
        "classes": le.classes_.tolist()
    }
    
    with open(os.path.join(artifact_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    print("Crop model artifacts saved successfully!")

if __name__ == "__main__":
    train_crop_model()
