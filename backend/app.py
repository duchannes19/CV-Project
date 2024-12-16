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
    file = request.files.get('image')
    if file is None:
        print(f"{bcolors.FAIL}No image file uploaded{bcolors.ENDC}")
        return jsonify({"error": "No image file uploaded"}), 400
    
    # Check if image is DICOM or PNG (demo logic)
    if file.filename.endswith('.dcm') is False and file.filename.endswith('.png') is False:
        print(f"{bcolors.FAIL}Invalid file format. Must be DICOM or PNG{bcolors.ENDC}")
        return jsonify({"error": "Invalid file format. Must be DICOM or PNG"}), 400

    # Load image (assuming a grayscale PNG for this demonstration)
    file_bytes = np.frombuffer(file.read(), np.uint8)
    original_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    if original_img is None:
        print(f"{bcolors.FAIL}Could not read image{bcolors.ENDC}")
        return jsonify({"error": "Could not read image"}), 400

    # Keep original_img copy for overlay (resize to 256x256 to match model)
    original_resized = cv2.resize(original_img, (256,256))
    
    # Preprocess for inference
    img = original_resized.astype(np.float32)
    img = (img - np.mean(img)) / (np.std(img)+1e-8)
    
    # The model expects (1,16,256,256,1)
    img = np.expand_dims(img, axis=0)       # (1,256,256)
    img = np.expand_dims(img, axis=0)       # (1,1,256,256)
    img = np.repeat(img, 16, axis=1)        # (1,16,256,256)
    img = np.expand_dims(img, axis=-1)      # (1,16,256,256,1)
    
    # Run inference
    print(f"{bcolors.OKGREEN}Running inference...{bcolors.ENDC}")
    try:
        pred = model.predict(img)
        print(f"{bcolors.OKGREEN}Inference complete.{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}Inference failed: {e}{bcolors.ENDC}")
        return jsonify({"error": "Inference failed"}), 500
    
    # Use the middle slice (depth=8) as an example
    mask = (pred[0,8,:,:,0] > 0.5).astype(np.uint8)  # (256,256)
    
    # Overlay mask onto the original_resized image
    # Convert to BGR
    overlay_img = cv2.cvtColor(original_resized, cv2.COLOR_GRAY2BGR)
    
    # Create a red overlay where mask is 1
    # For pixels where mask==1, color them red
    # Red in BGR is (0,0,255)
    overlay_img[mask==1] = (0,0,255)
    
    # Encode to PNG base64
    _, buffer = cv2.imencode('.png', overlay_img)
    overlay_bytes = buffer.tobytes()
    overlay_base64 = "data:image/png;base64," + base64.b64encode(overlay_bytes).decode('utf-8')
    
    print(f"{bcolors.OKGREEN}Segmentation complete.{bcolors.ENDC}")
    return jsonify({"overlay": overlay_base64})
    
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
