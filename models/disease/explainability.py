import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from matplotlib import colormaps

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        
        # Register hooks
        self.forward_hook = target_layer.register_forward_hook(self.save_activation)
        self.backward_hook = target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def remove_hooks(self):
        self.forward_hook.remove()
        self.backward_hook.remove()

    def generate_heatmap(self, input_tensor, class_idx):
        # Determine device from model parameters
        device = next(self.model.parameters()).device
        input_tensor = input_tensor.to(device)
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        # Calculate loss/gradient for the target class
        score = output[0, class_idx]
        score.backward()
        
        # Get activations and gradients
        activations = self.activations.detach().cpu()
        gradients = self.gradients.detach().cpu()
        
        # Pool gradients (Global Average Pooling)
        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
        
        # Linear combination of activations and weights
        grad_cam = torch.sum(weights * activations, dim=1, keepdim=True)
        
        # Apply ReLU to retain only positive contributions
        grad_cam = F.relu(grad_cam)
        
        # Normalize between 0 and 1
        grad_cam_min, grad_cam_max = grad_cam.min(), grad_cam.max()
        if grad_cam_max > grad_cam_min:
            grad_cam = (grad_cam - grad_cam_min) / (grad_cam_max - grad_cam_min)
        else:
            grad_cam = torch.zeros_like(grad_cam)
            
        heatmap = grad_cam.squeeze().numpy()
        return heatmap

def overlay_heatmap(original_image, heatmap, alpha=0.5):
    """
    Overlays a Grad-CAM heatmap onto a PIL original image.
    Returns: PIL Image containing the overlay.
    """
    # Convert original PIL image to numpy array
    img = np.array(original_image)
    h, w, c = img.shape
    
    # Resize heatmap to match image size using PIL
    heatmap_pil = Image.fromarray(np.uint8(255 * heatmap))
    heatmap_pil = heatmap_pil.resize((w, h), Image.Resampling.BILINEAR)
    heatmap_resized = np.array(heatmap_pil) / 255.0
    
    # Convert heatmap to color map using matplotlib
    colormap = colormaps['jet']
    heatmap_color = colormap(heatmap_resized)[:, :, :3]
    heatmap_color = np.uint8(255 * heatmap_color)
    
    # Superimpose heatmap
    overlay = np.uint8(img * (1.0 - alpha) + heatmap_color * alpha)
    
    return Image.fromarray(overlay)
