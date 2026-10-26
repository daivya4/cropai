from __future__ import annotations
import os
import json
import time
import random
import hashlib
import subprocess
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from PIL import Image
from pathlib import Path

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

ROOT = Path(__file__).resolve().parents[2]


class PlantVillageDataset(Dataset):
    """Load images from a CSV manifest with 'path' and 'label' columns."""

    def __init__(self, csv_path: str, class_to_idx: dict, transform=None):
        self.df = pd.read_csv(csv_path)
        self.class_to_idx = class_to_idx
        self.transform = transform
        self.root = ROOT

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.root / row["path"]
        label_idx = self.class_to_idx[row["label"]]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label_idx


def calculate_ece(probs, labels, n_bins=10):
    """Calculates the Expected Calibration Error (ECE)."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = predictions == labels

    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
    return float(ece)


def dataset_hash(data_dir: str) -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(data_dir).glob("*.csv")):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def train_model(
    manifest_dir="data/processed/disease",
    artifact_dir="artifacts/disease",
    epochs=5,
    batch_size=64,
):
    os.makedirs(artifact_dir, exist_ok=True)

    train_csv = os.path.join(manifest_dir, "train.csv")
    val_csv = os.path.join(manifest_dir, "val.csv")
    test_csv = os.path.join(manifest_dir, "test.csv")

    # Discover all classes from all splits
    all_df = pd.concat([pd.read_csv(train_csv), pd.read_csv(val_csv), pd.read_csv(test_csv)])
    classes = sorted(all_df["label"].unique().tolist())
    class_to_idx = {cls: i for i, cls in enumerate(classes)}
    class_mapping = {i: cls for cls, i in class_to_idx.items()}

    with open(os.path.join(artifact_dir, "class_mapping.json"), "w") as f:
        json.dump(class_mapping, f, indent=4)

    preprocessing_config = {
        "image_size": 224,
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
    }
    with open(os.path.join(artifact_dir, "preprocessing.json"), "w") as f:
        json.dump(preprocessing_config, f, indent=4)

    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_ds = PlantVillageDataset(train_csv, class_to_idx, transform=train_transform)
    val_ds = PlantVillageDataset(val_csv, class_to_idx, transform=val_transform)
    test_ds = PlantVillageDataset(test_csv, class_to_idx, transform=val_transform)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    num_classes = len(classes)
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
        
    print(f"Training on {len(train_ds)} images, {num_classes} classes, device: {device}")

    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    start_time = time.time()
    best_val_acc = -1.0

    for epoch in range(epochs):
        print(f"\nEpoch {epoch + 1}/{epochs}", flush=True)

        model.train()
        running_loss, running_corrects = 0.0, 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        train_acc = running_corrects.item() / len(train_ds)
        print(f"  train Loss: {running_loss / len(train_ds):.4f}  Acc: {train_acc:.4f}", flush=True)

        model.eval()
        val_corrects = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data)

        val_acc = val_corrects.item() / len(val_ds)
        print(f"  val   Acc: {val_acc:.4f}", flush=True)

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(artifact_dir, "model.pt"))
            print("  checkpoint saved.", flush=True)

        scheduler.step()

    training_duration = time.time() - start_time
    print(f"\nDone. Best val acc: {float(best_val_acc):.4f}, time: {training_duration:.0f}s")

    # Test evaluation
    model.load_state_dict(torch.load(os.path.join(artifact_dir, "model.pt"), map_location=device))
    model.eval()
    all_preds, all_labels, all_probs = [], [], []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    test_acc = float(np.mean(all_preds == all_labels))
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average="macro", zero_division=0
    )
    conf_mat = confusion_matrix(all_labels, all_preds).tolist()
    ece = calculate_ece(all_probs, all_labels)

    print(f"Test Accuracy : {test_acc:.4f}")
    print(f"Test Macro F1 : {f1:.4f}")
    print(f"Test ECE      : {ece:.4f}")

    metadata = {
        "model_name": "mobilenet_v3_small_imagenet_pretrained",
        "model_version": "disease_v2",
        "dataset": "PlantVillage (real, colour, 38 classes)",
        "dataset_hash": dataset_hash(manifest_dir),
        "git_sha": git_sha(),
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": round(training_duration, 2),
        "epochs": epochs,
        "batch_size": batch_size,
        "random_seed": 42,
        "num_classes": num_classes,
        "metrics": {
            "test_accuracy": test_acc,
            "macro_precision": float(precision),
            "macro_recall": float(recall),
            "macro_f1": float(f1),
            "ece": ece,
            "best_val_accuracy": float(best_val_acc),
        },
        "confusion_matrix": conf_mat,
        "classes": classes,
    }

    with open(os.path.join(artifact_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print("Artifacts saved to", artifact_dir)


if __name__ == "__main__":
    train_model()
