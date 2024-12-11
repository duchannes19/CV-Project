import numpy as np
import bm3d
from skimage import exposure

def bm3d_denoise(image: np.ndarray) -> np.ndarray:
    # BM3D denoising for MRI. 
    # MRI images are often noisy, and BM3D is a state-of-the-art filter for denoising.
    # BM3D expects images in grayscale float format.
    # Note: Ensure correct normalization before BM3D (0-1 scale).
    sigma_psd = 0.05  # example noise level
    denoised = bm3d.bm3d(image, sigma_psd)
    return denoised

def normalize_image(image: np.ndarray, method: str = 'z-score') -> np.ndarray:
    # Normalization to ensure consistent intensity distribution
    if method == 'z-score':
        mean = np.mean(image)
        std = np.std(image)
        return (image - mean) / (std + 1e-8)
    elif method == 'minmax':
        min_val = np.min(image)
        max_val = np.max(image)
        return (image - min_val) / (max_val - min_val + 1e-8)
    else:
        raise ValueError("Unknown normalization method")
