import os
import torch
from torch import nn
import PIL.Image
import PIL.ImageEnhance
import utils
import safetensors.torch

def relative_file(file):
    """Get absolute path to a file relative to this module"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, file)
    
    # If file exists at the computed path, return it
    if os.path.exists(full_path):
        return full_path
    
    # Try current working directory as fallback
    cwd_path = os.path.join(os.getcwd(), file)
    if os.path.exists(cwd_path):
        return cwd_path
    
    # Return original computation (for error reporting)
    return full_path

class VAEApproxCheap(nn.Module):
    def __init__(self):
        super(VAEApproxCheap, self).__init__()
        self.conv = nn.Conv2d(4, 3, kernel_size=5, padding='same')
        self.loaded = False
    
    def forward(self, x):
        return self.conv(x)

class VAEApprox(nn.Module):
    def __init__(self):
        super(VAEApprox, self).__init__()
        self.conv1 = nn.Conv2d(4, 8, (7, 7))
        self.conv2 = nn.Conv2d(8, 16, (5, 5))
        self.conv3 = nn.Conv2d(16, 32, (3, 3))
        self.conv4 = nn.Conv2d(32, 64, (3, 3))
        self.conv5 = nn.Conv2d(64, 32, (3, 3))
        self.conv6 = nn.Conv2d(32, 16, (3, 3))
        self.conv7 = nn.Conv2d(16, 8, (3, 3))
        self.conv8 = nn.Conv2d(8, 3, (3, 3))
        self.loaded = False

    def forward(self, x):
        extra = 11
        x = nn.functional.interpolate(x, (x.shape[2] * 2, x.shape[3] * 2))
        x = nn.functional.pad(x, (extra, extra, extra, extra))

        for layer in [self.conv1, self.conv2, self.conv3, self.conv4, self.conv5, self.conv6, self.conv7, self.conv8, ]:
            x = layer(x)
            x = nn.functional.leaky_relu(x, 0.1)

        return x
    
    def load_state_dict(self, state_dict):
        super().load_state_dict(state_dict)
        self.loaded = True

CHEAP_MODEL = VAEApproxCheap()
CHEAP_MODEL_PATH = os.path.join("approx", "VAE-cheap.safetensors")

APPROX_MODEL = VAEApprox()
APPROX_MODEL_PATH = os.path.join("approx", "VAE-approx.pt")

def cheap_preview(latents, vae):
    if not CHEAP_MODEL.loaded:
        model_file = relative_file(CHEAP_MODEL_PATH)
        if not os.path.exists(model_file):
            # Fallback to full_preview if cheap model not available
            print(f"Warning: VAE cheap model not found at {model_file}, using full preview instead")
            return full_preview(latents, vae)
        try:
            CHEAP_MODEL.conv.load_state_dict(safetensors.torch.load_file(model_file))
        except Exception as e:
            print(f"Warning: Failed to load VAE cheap model: {e}, using full preview instead")
            return full_preview(latents, vae)
    
    CHEAP_MODEL.to(latents.device).to(latents.dtype)
    outputs = CHEAP_MODEL(latents) / vae.scaling_factor
    if vae.model_type == "SDXL-Base":
        outputs = [o.flip(0) for o in outputs]
    outputs = [utils.FROM_TENSOR(((o + 1)/2).clamp(0,1)) for o in outputs]

    return outputs

def model_preview(latents, vae):
    if not APPROX_MODEL.loaded:
        model_file = relative_file(APPROX_MODEL_PATH)
        if not os.path.exists(model_file):
            # Fallback to full_preview if approx model not available
            print(f"Warning: VAE approx model not found at {model_file}, using full preview instead")
            return full_preview(latents, vae)
        try:
            APPROX_MODEL.load_state_dict(utils.load_pickle(model_file, map_location='cpu'))
        except Exception as e:
            print(f"Warning: Failed to load VAE approx model: {e}, using full preview instead")
            return full_preview(latents, vae)
    
    APPROX_MODEL.to(latents.device).to(latents.dtype)
    outputs = APPROX_MODEL(latents)
    if vae.model_type == "SDXL-Base":
        outputs = [o.flip(0) for o in outputs]
    outputs = utils.postprocess_images(outputs)
    return outputs

def full_preview(latents, vae):
    return utils.postprocess_images(vae.decode(latents.to(vae.dtype)).sample / vae.scaling_factor)