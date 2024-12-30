import cv2
import numpy as np
import pydicom
import io
import base64

# Utility functions
def preprocess_image(img):
    # Preprocess image as done before
    img = cv2.resize(img, (256,256))
    img = img.astype(np.float32)
    img = (img - np.mean(img)) / (np.std(img)+1e-8)
    # Shape model expects: (1,16,256,256,1)
    img = np.expand_dims(img, axis=0)       # (1,256,256)
    img = np.expand_dims(img, axis=0)       # (1,1,256,256)
    img = np.repeat(img, 16, axis=1)        # (1,16,256,256)
    img = np.expand_dims(img, axis=-1)      # (1,16,256,256,1)
    return img

def load_png(file):
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    return img

def load_dicom(file):
    # Read all file bytes
    file_bytes = file.read()
    # Reset pointer if needed
    file.seek(0)
    # Create a file-like object from the bytes
    file_like = io.BytesIO(file_bytes)

    # Use dcmread with the file-like object directly
    dicom_data = pydicom.dcmread(file_like, force=True)
    
    img = dicom_data.pixel_array.astype(np.float32)
    # If 3D volume, select a slice:
    if img.ndim > 2:
        mid_slice = img.shape[0] // 2
        img = img[mid_slice]
    return img

def create_overlay(original, mask):
    # Overlay mask (red) onto original grayscale image
    overlay_img = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    overlay_img[mask==1] = (0,0,255)
    _, buffer = cv2.imencode('.png', overlay_img)
    overlay_bytes = buffer.tobytes()
    overlay_base64 = "data:image/png;base64," + base64.b64encode(overlay_bytes).decode('utf-8')
    return overlay_base64

def load_status_page():
    return """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Prostate Segmentation Server Status</title>
            <style>
            body { font-family: Arial, sans-serif; margin: 2rem; }
            h1 { color: #4CAF50; }
            p { font-size: 1.2rem; }
            </style>
            </head>
            <body>
            <h1>Server is running.</h1>
            <p>This server provides segmentation predictions for prostate MRI images.</p>
            </body>
            </html>
            """