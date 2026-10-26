import io
import json
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models

from models.disease.uncertainty import calculate_mc_uncertainty
from models.disease.explainability import GradCAM, overlay_heatmap


class DiseaseInferenceService:
    def __init__(self, config_path="configs/config.yaml"):
        import yaml

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.model_path = self.config["models"]["disease"]["path"]
        self.class_mapping_path = self.config["models"]["disease"]["class_mapping_path"]
        self.preprocessing_path = self.config["models"]["disease"]["preprocessing_path"]

        with open(self.class_mapping_path) as f:
            raw = json.load(f)
            self.class_mapping = {int(k): v for k, v in raw.items()}

        with open(self.preprocessing_path) as f:
            self.pre_config = json.load(f)

        num_classes = len(self.class_mapping)
        if torch.cuda.is_available():
            self.device = torch.device("cuda:0")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        # Build the exact same architecture used in training
        self.model = models.mobilenet_v3_small(weights=None)
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, num_classes)
        self.model.load_state_dict(
            torch.load(self.model_path, map_location=self.device)
        )
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self.pre_config["image_size"]),
            transforms.ToTensor(),
            transforms.Normalize(self.pre_config["mean"], self.pre_config["std"]),
        ])

        # Target layer for Grad-CAM (last conv block in MobileNetV3-Small features)
        self.target_layer = self.model.features[-1][0]

    def predict(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0)

        # MC Dropout uncertainty
        avg_probs, uncertainty_info = calculate_mc_uncertainty(
            self.model, input_tensor, self.device, num_passes=10
        )

        predicted_idx = int(avg_probs.argmax())
        prediction_label = self.class_mapping[predicted_idx]
        confidence = float(avg_probs[predicted_idx])

        top_predictions = sorted(
            [
                {"class": self.class_mapping[i], "probability": float(p)}
                for i, p in enumerate(avg_probs)
            ],
            key=lambda x: x["probability"],
            reverse=True,
        )

        # Grad-CAM
        self.model.eval()
        grad_cam = GradCAM(self.model, self.target_layer)
        try:
            heatmap = grad_cam.generate_heatmap(input_tensor.to(self.device), predicted_idx)
            overlay_img = overlay_heatmap(image, heatmap, alpha=0.5)
            img_buf = io.BytesIO()
            overlay_img.save(img_buf, format="PNG")
            overlay_bytes = img_buf.getvalue()
        finally:
            grad_cam.remove_hooks()

        return {
            "prediction": prediction_label,
            "confidence": confidence,
            "top_predictions": top_predictions,
            "uncertainty": uncertainty_info,
            "overlay_bytes": overlay_bytes,
            "model_version": "disease_v2",
        }
