#!/usr/bin/env python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from flask import Flask, request, jsonify, render_template_string, abort
import tensorflow as tf
import numpy as np
import cv2
import logging
from bcolors import bcolors

# Basic configuration
API_KEY = "mysecureapikey"  # Replace with a secure key

# Load model
try:
    model = tf.keras.models.load_model("prostate_segmentation.keras", compile=False)    
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

# Middleware for security
@app.before_request
def check_api_key():
    # Secure specific endpoints that require model inference
    if request.endpoint == 'predict_segmentation':
        key = request.headers.get('X-API-KEY')
        if key != API_KEY:
            app.logger.warning("Unauthorized access attempt.")
            abort(401, description="Unauthorized: Invalid API key")

@app.route("/")
def index():
    # A cute page which says the status of the server
    return STATUS_PAGE

@app.route("/predict", methods=["POST"])
def predict_segmentation():
    # Expect a file in the request (e.g., DICOM or Nifti or PNG)
    # For simplicity, let's assume PNG or Numpy image transmitted as bytes
    file = request.files.get('image')
    if file is None:
        return jsonify({"error": "No image file uploaded"}), 400

    # Load image (assuming a grayscale png for demonstration)
    # In real cases, decode DICOM or other format properly
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return jsonify({"error": "Could not read image"}), 400

    # Preprocess image
    img = cv2.resize(img, (256,256))
    img = img.astype(np.float32)
    # Simple normalization (assuming trained that way)
    img = (img - np.mean(img)) / (np.std(img)+1e-8)
    img = np.expand_dims(img, axis=(0,-1))  # (1, H, W, 1)

    # Run inference
    pred = model.predict(img)
    mask = (pred[0,:,:,0] > 0.5).astype(np.uint8)

    # Return mask as a list of lists or some encoded form
    mask_list = mask.tolist()
    return jsonify({"mask": mask_list})

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
