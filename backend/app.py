#!/usr/bin/env python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from flask import Flask, request, jsonify, render_template_string, abort
from flask_cors import CORS
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import logging
import base64
import pydicom
import io
from bcolors import bcolors

# Basic configuration
API_KEY = "mysecureapikey"  # Replace with a secure key

# Load model
try:
    model = load_model("prostate_segmentation.keras", compile=False)    
    # Loggin with bcolors
    print(f"{bcolors.OKGREEN}Model loaded successfully.{bcolors.ENDC}")
    logging.info(f"{bcolors.OKGREEN}Model loaded successfully.{bcolors.ENDC}")
except Exception as e:
    logging.error(f"Could not load model: {e}")
    exit(1)

app = Flask('prostate_segmentation_server')
logging.basicConfig(level=logging.INFO)

# Simple HTML template for server status page
STATUS_PAGE = """
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

# Enable CORS for all domains on all routes

CORS(app, resources={r"/*": {"origins": "*"}}, 
     allow_headers=["Content-Type", "x-api-key"])

CORS(app)

# Middleware for security (Not working)
#@app.before_request
#def check_api_key():
#    # Secure specific endpoints that require model inference
#    if request.endpoint == 'predict_segmentation':
#        key = request.headers.get('x-api-key')
#        print(request.headers)
#        print(key)
#        if key != API_KEY:
#            app.logger.warning("Unauthorized access attempt.")
#            abort(401, description="Unauthorized: Invalid API key")

@app.route("/")
def index():
    # A cute page which says the status of the server
    return STATUS_PAGE

@app.route("/predict", methods=["POST"])
def predict_segmentation():
    if 'files' not in request.files:
        return jsonify({"error": "No image files uploaded"}), 400

    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({"error": "No files selected"}), 400

    overlays = []
    for file in files:
        filename = file.filename.lower()
        if filename.endswith('.dcm'):
            # DICOM
            try:
                original_img = load_dicom(file)
            except Exception as e:
                print(bcolors.FAIL + f"Could not read DICOM file: {e}" + bcolors.ENDC)
                return jsonify({"error": f"Could not read DICOM file: {e}"}), 400
        elif filename.endswith('.png'):
            # PNG
            original_img = load_png(file)
            if original_img is None:
                print(bcolors.FAIL + "Could not read PNG image" + bcolors.ENDC)
                return jsonify({"error": "Could not read PNG image"}), 400
        else:
            return jsonify({"error": "Invalid file format. Must be DICOM or PNG"}), 400

        # Preprocess for inference
        preprocessed = preprocess_image(original_img)

        # Run inference
        try:
            pred = model.predict(preprocessed)
            # See confidence of prediction
            print(f"Prediction confidence: {np.mean(pred)}")
        except Exception as e:
            return jsonify({"error": f"Inference failed: {e}"}), 500

        # Use middle slice in depth dimension:
        mask = (pred[0,8,:,:,0] > 0.5).astype(np.uint8) # (256,256)

        # Create overlay
        # Note: original_img should be resized as well to match the overlay
        # original_resized = cv2.resize(original_img, (256,256))
        # overlay_base64 = create_overlay(original_resized, mask)
        
        # Format the mask as a base64 image
        _, buffer = cv2.imencode('.png', mask*255)
        mask_bytes = buffer.tobytes()
        mask_base64 = "data:image/png;base64," + base64.b64encode(mask_bytes).decode('utf-8')
        
        overlays.append(mask_base64)

    return jsonify({"overlays": overlays}), 200
    
# Error handlers
@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e)), 401

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Not Found"), 404

if __name__ == "__main__":
    # Running on a given port
    app.run(host='0.0.0.0', port=5000, debug=False)
