import base64
import cv2
import numpy as np
from typing import List

def upscale_overlays(overlays: List[str], scale_factor: int = 4) -> List[str]:
    """
    Upscale each base64-encoded overlay image by the given scale factor using Lanczos interpolation.
    
    Args:
        overlays: A list of base64-encoded PNG images (e.g., shape (128,128,3)).
        scale_factor: The integer factor by which to upscale each dimension (default is 4).
    
    Returns:
        A new list of base64-encoded PNG images, each upscaled to (128 * scale_factor, 128 * scale_factor).
    """
    upscaled_overlays = []
    
    for overlay_base64 in overlays:
        # 1) Decode base64 to OpenCV image
        #    overlay_base64 is a string like "data:image/png;base64,...."
        #    so we split off the prefix and decode the remainder
        if "," in overlay_base64:
            prefix, b64_data = overlay_base64.split(",", 1)
        else:
            # fallback if the prefix is absent
            b64_data = overlay_base64
        
        decoded_bytes = base64.b64decode(b64_data)
        np_img = np.frombuffer(decoded_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)  # shape: (H, W, 3)
        
        if img is None:
            # If decoding fails, skip or handle appropriately
            upscaled_overlays.append(overlay_base64)
            continue
        
        # 2) Determine new size based on scale_factor
        height, width = img.shape[:2]
        new_width = width * scale_factor
        new_height = height * scale_factor
        
        # 3) Resize using Lanczos interpolation (cv2.INTER_LANCZOS4)
        upscaled_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # 4) Encode back to PNG base64
        _, buffer = cv2.imencode('.png', upscaled_img)
        upscaled_bytes = buffer.tobytes()
        # Reattach prefix if desired
        # Typically: "data:image/png;base64,<encoded>"
        upscaled_b64 = base64.b64encode(upscaled_bytes).decode('utf-8')
        upscaled_overlay = f"data:image/png;base64,{upscaled_b64}"
        
        # 5) Append to results
        upscaled_overlays.append(upscaled_overlay)
    
    return upscaled_overlays