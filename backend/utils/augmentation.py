import random
import numpy as np
import cv2

def random_flip(image, mask):
    # Random horizontal flip
    if random.random() < 0.5:
        image = np.flip(image, axis=1)
        mask = np.flip(mask, axis=1)
    # Random vertical flip
    if random.random() < 0.5:
        image = np.flip(image, axis=0)
        mask = np.flip(mask, axis=0)
    return image, mask

def random_rotate(image, mask):
    # Rotate by random angle in multiples of 90 degrees
    k = random.choice([0,1,2,3])
    image = np.rot90(image, k)
    mask = np.rot90(mask, k)
    return image, mask

def random_scale(image, mask):
    # Simple scaling by random factor close to 1
    scale = random.uniform(0.9, 1.1)
    height, width = image.shape[:2]
    new_h, new_w = int(height*scale), int(width*scale)
    image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    mask = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    # Crop or pad back to original size
    diff_h = new_h - height
    diff_w = new_w - width
    # Simple center crop/pad
    image = image[max(0, diff_h//2):max(0, diff_h//2)+height,
                  max(0, diff_w//2):max(0, diff_w//2)+width]
    mask = mask[max(0, diff_h//2):max(0, diff_h//2)+height,
                max(0, diff_w//2):max(0, diff_w//2)+width]
    return image, mask