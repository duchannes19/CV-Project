import numpy as np
import cv2

def postprocess_segmentation(mask):
    # Morphological closing to smooth boundaries
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    return mask