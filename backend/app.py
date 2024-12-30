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

# Import utility functions from utility.py
from utils.utility import preprocess_image, load_png, load_dicom, create_overlay, load_status_page

# Load the ensemble models
from utils.ensemble import load_ensemble

# Basic configuration
API_KEY = "mysecureapikey"  # Replace with a secure key

app = Flask('prostate_segmentation_server')
logging.basicConfig(level=logging.INFO)

# Load the ensemble models (array of models)
model = load_ensemble()

# Simple HTML template for server status page
STATUS_PAGE = load_status_page()

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


# TO DO: Refactor the following code to predict segmentation with the ensemble model
# Also We need other functions to preprocess the image and create the overlay
# And also integrate ESRGAN for super resolution

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
