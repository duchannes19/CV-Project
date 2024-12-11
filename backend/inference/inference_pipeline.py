import torch
from torch.nn.functional import softmax
import numpy as np
from ..utils.preprocessing import bm3d_denoise, normalize_image
from ..utils.postprocessing import postprocess_segmentation

def run_inference(model, image, device='cuda'):
    model.eval()
    with torch.no_grad():
        # Preprocess: denoise, normalize
        image = bm3d_denoise(image)
        image = normalize_image(image, 'z-score')
        # Assuming image shape: HxW. Convert to NCHW
        tensor = torch.from_numpy(image[np.newaxis, np.newaxis, ...]).float().to(device)
        pred = model(tensor)
        pred = softmax(pred, dim=1)
        pred_mask = torch.argmax(pred, dim=1).cpu().numpy()[0]
        pred_mask = postprocess_segmentation(pred_mask)
    return pred_mask