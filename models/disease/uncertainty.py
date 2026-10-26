import numpy as np
import torch

def enable_dropout(model):
    """
    Keep dropout layers active during evaluation for MC Dropout.
    """
    for m in model.modules():
        if m.__class__.__name__.startswith('Dropout'):
            m.train()

def calculate_mc_uncertainty(model, input_tensor, device, num_passes=10):
    """
    Calculates predictions and uncertainty using MC Dropout.
    Returns average probabilities and predictive entropy.
    """
    model.eval()
    enable_dropout(model)  # Force dropout to remain active
    
    all_probs = []
    
    with torch.no_grad():
        for _ in range(num_passes):
            outputs = model(input_tensor.to(device))
            probs = torch.softmax(outputs, dim=1)
            all_probs.append(probs.cpu().numpy()[0])
            
    # Average probabilities over multiple passes
    avg_probs = np.mean(all_probs, axis=0)
    
    # Calculate predictive entropy: -sum(p * log2(p))
    # Add a small epsilon to avoid log(0)
    eps = 1e-9
    entropy = -np.sum(avg_probs * np.log2(avg_probs + eps))
    
    # Max possible entropy for 3 classes is log2(3) = 1.585
    # Normalize entropy between 0 and 1
    max_entropy = np.log2(len(avg_probs))
    normalized_entropy = float(entropy / max_entropy)
    
    # Determine reliability rating
    reliability = "High" if normalized_entropy < 0.4 else ("Medium" if normalized_entropy < 0.7 else "Low")
    
    return avg_probs, {
        "entropy": float(entropy),
        "normalized_entropy": normalized_entropy,
        "reliability": reliability,
        "method": "mc_dropout"
    }
