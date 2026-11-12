import os

os.environ.setdefault("USE_TF", "0")

import torch
import torch.nn.functional as functional
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


LEAF_PROMPTS = [
    "a close-up photograph of a plant leaf",
    "a close-up photograph of a diseased crop leaf",
    "a close-up photograph of a healthy crop leaf",
    "a photograph of a tomato plant leaf",
    "a photograph of a potato plant leaf",
    "a photograph of a corn plant leaf",
]

NON_LEAF_PROMPTS = [
    "a photograph of a person's face",
    "a photograph of a person",
    "a photograph of an animal",
    "a photograph of a landscape",
    "a photograph of a building",
    "a photograph of an everyday object",
]

NOT_LEAF_MESSAGE = (
    "The uploaded image does not appear to show a plant leaf. "
    "Please upload a clear crop leaf image."
)


class NotLeafImageError(ValueError):
    """Raised when an uploaded image is not recognized as a plant leaf."""


class LeafImageValidator:
    def __init__(self, model_name: str):
        if torch.cuda.is_available():
            self.device = torch.device("cuda:0")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

        self.text_inputs = self.processor(
            text=LEAF_PROMPTS + NON_LEAF_PROMPTS,
            return_tensors="pt",
            padding=True,
        )
        self.text_inputs = {
            key: value.to(self.device) for key, value in self.text_inputs.items()
        }
        with torch.inference_mode():
            text_features = self.model.get_text_features(**self.text_inputs)
            self.text_features = functional.normalize(text_features, dim=-1)

    def validate(self, image: Image.Image) -> float:
        image_inputs = self.processor(images=image, return_tensors="pt")
        pixel_values = image_inputs["pixel_values"].to(self.device)

        with torch.inference_mode():
            image_features = self.model.get_image_features(pixel_values=pixel_values)
            image_features = functional.normalize(image_features, dim=-1)
            similarities = image_features @ self.text_features.T

            positive_score = similarities[:, :len(LEAF_PROMPTS)].max(dim=1).values
            negative_score = similarities[:, len(LEAF_PROMPTS):].max(dim=1).values
            logits = torch.stack((positive_score, negative_score), dim=1)
            logits = logits * self.model.logit_scale.exp()
            leaf_probability = float(logits.softmax(dim=1)[0, 0].item())

        if leaf_probability < 0.5:
            raise NotLeafImageError(NOT_LEAF_MESSAGE)
        return leaf_probability
