import numpy as np
import cv2
import base64
import pydicom
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

from utils.bcolors import bcolors  # For colored prints, if desired

############################
# Custom Losses & Metrics #
############################

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    """
    Computes the Dice Coefficient.
    """
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

def dice_loss(y_true, y_pred):
    """
    Computes the Dice Loss = 1 - Dice Coefficient.
    """
    return 1 - dice_coefficient(y_true, y_pred)

#########################
#  Model Loading Logic  #
#########################

def load_ensemble():
    """
    Loads multiple Keras models for ensemble inference.
    Adjust model_paths to match your environment.
    """
    model_paths = [
        "best_model_residual_spatial_dropout.keras",
        "best_model_residual_attention.keras",
        "best_model_residual_se.keras"
    ]

    ensemble_models = []
    for idx, path in enumerate(model_paths, 1):
        try:
            model = load_model(
                path,
                custom_objects={
                    'dice_loss': dice_loss,
                    'dice_coefficient': dice_coefficient
                }
            )
            ensemble_models.append(model)
            print(f"[Ensemble] Loaded Model {idx} from '{path}'.")
        except Exception as e:
            print(f"[Ensemble] Error loading Model {idx} from '{path}': {e}")
    
    return ensemble_models

##################################
#  Helper Functions for Inference
##################################

def load_dicom(file):
    """
    Loads a DICOM file (can be single or multi-slice).
    Returns a numpy array of shape (depth, height, width).
    """
    try:
        dcm = pydicom.dcmread(file, force=True)
        arr = dcm.pixel_array.astype(np.float32)
        # If there's a slope/intercept
        slope = getattr(dcm, 'RescaleSlope', 1.0)
        intercept = getattr(dcm, 'RescaleIntercept', 0.0)
        arr = arr * slope + intercept
        
        # If single slice, shape = (height, width).
        # If multi-slice, shape = (num_slices, height, width).
        if arr.ndim == 2:
            # Expand to shape (1, height, width)
            arr = np.expand_dims(arr, axis=0)
        return arr
    except Exception as e:
        raise IOError(f"Failed to load DICOM: {e}")

def preprocess_slice_2d(slice_2d, target_size=(128, 128)):
    """
    Preprocess a single 2D slice:
      - Resize to target_size
      - Normalize intensities
      - Expand dims to (1, H, W, 1) for model inference
    """
    # Resize to (128, 128)
    resized = cv2.resize(slice_2d, target_size, interpolation=cv2.INTER_LINEAR)

    # Simple normalization: (img - mean) / std
    mean_val = np.mean(resized)
    std_val = np.std(resized) + 1e-8
    normalized = (resized - mean_val) / std_val

    # Expand dims to (1, H, W, 1)
    input_4d = np.expand_dims(normalized, axis=(0, -1))  # shape: (1, 128, 128, 1)
    return input_4d

def ensemble_predict_slice(models, slice_2d):
    """
    Generate ensemble prediction for a single 2D slice.
    1) Preprocess the slice.
    2) Each model predicts -> average them.
    3) Return the binarized mask (0/1).
    """
    inp = preprocess_slice_2d(slice_2d, target_size=(128, 128))
    preds = []
    for model in models:
        p = model.predict(inp)  # Expect shape: (1, 128, 128, 1)
        preds.append(p)
    avg_pred = np.mean(preds, axis=0)  # shape: (1, 128, 128, 1)
    mask_2d = (avg_pred[0, :, :, 0] > 0.5).astype(np.uint8)  # shape: (128,128)
    return mask_2d

def create_overlay(original_slice, predicted_mask, target_size=(128, 128)):
    """
    Create an overlay image by placing `predicted_mask` (red) on top of `original_slice`.
    Both are 2D arrays (H, W).
    Return base64-encoded PNG of shape (H, W, 3).
    """
    
    # Resize the predicted mask to match the original slice size, use the smoothest interpolation
    predicted_mask = cv2.resize(predicted_mask, original_slice.shape[::-1], interpolation=cv2.INTER_LINEAR)
    
    # Normalize to 0-255 for display
    original_8u = cv2.normalize(original_slice, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Convert grayscale to BGR
    overlay_img = cv2.cvtColor(original_8u, cv2.COLOR_GRAY2BGR)
    # Color mask in red
    overlay_img[predicted_mask == 1] = (0, 0, 255)

    # Encode to PNG base64
    _, buffer = cv2.imencode('.png', overlay_img)
    overlay_bytes = buffer.tobytes()
    overlay_base64 = "data:image/png;base64," + base64.b64encode(overlay_bytes).decode('utf-8')
    return overlay_base64

#######################
# Main Prediction Logic
#######################

def get_prediction(files, ensemble_models):
    """
    Use ensemble_models to predict segmentation on DICOM files (single or multi-slice).
    Return an array of overlay base64 strings, one per slice across all files.
    
    Args:
        files: list of file-like objects (Flask file uploads).
        ensemble_models: list of loaded Keras models for ensemble.
    
    Returns:
        overlays: list of base64-encoded PNG images (the overlay of each slice).
    """
    overlays = []
    
    for file in files:
        filename = file.filename.lower()
        if not filename.endswith('.dcm'):
            print(bcolors.FAIL + f"Unsupported file format for '{filename}'" + bcolors.ENDC)
            continue
        
        try:
            volume = load_dicom(file)  # shape: (depth, height, width)
        except Exception as e:
            print(bcolors.FAIL + f"Could not read DICOM file: {e}" + bcolors.ENDC)
            continue
        
        depth = volume.shape[0]
        for slice_idx in range(depth):
            original_slice = volume[slice_idx]  # shape: (height, width)
            
            # Ensemble Predict on 2D slice
            predicted_mask_2d = ensemble_predict_slice(ensemble_models, original_slice)
            
            # Create overlay
            overlay_base64 = create_overlay(original_slice, predicted_mask_2d, target_size=(128, 128))
            overlays.append(overlay_base64)
            
            
    
    return overlays