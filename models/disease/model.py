import torch
import torch.nn as nn
from torchvision import models

class DiseaseMobileNetV3(nn.Module):
    def __init__(self, num_classes=3):
        super(DiseaseMobileNetV3, self).__init__()
        self.model = models.mobilenet_v3_small(weights=None)
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.model(x)

def get_disease_model(num_classes=3):
    return DiseaseMobileNetV3(num_classes=num_classes)
