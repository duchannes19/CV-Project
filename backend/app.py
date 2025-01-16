#!/usr/bin/env python3
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from utils.bcolors import bcolors

# Import utility functions from utility.py
from utils.utility import load_status_page

# Load the ensemble models
from utils.ensemble import load_ensemble, get_prediction

# Load the upscale function
from utils.upscale import upscale_overlays

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
# Also We need other functions to preprocess the image and create the overlay in the utility.py file

@app.route("/predict", methods=["POST"])
def predict_segmentation():
    if 'files' not in request.files:
        return jsonify({"error": "No image files uploaded"}), 400

    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({"error": "No files selected"}), 400

    print(bcolors.OKBLUE + f"Received {len(files)} files" + bcolors.ENDC)

    # Get the prediction from the ensemble model
    try:
        overlays = get_prediction(files, model)
    except Exception as e:
        print(bcolors.FAIL + f"Prediction failed: {e}" + bcolors.ENDC)
        return jsonify({"error": "Prediction failed"}), 500

    print(bcolors.OKGREEN + f"Prediction completed" + bcolors.ENDC)

    # Upscale the overlays by a factor of 4
    print(bcolors.OKBLUE + f"Upscaling overlays" + bcolors.ENDC)

    upscaled_list = upscale_overlays(overlays, scale_factor=2)

    print(bcolors.OKGREEN + f"Upscaling completed" + bcolors.ENDC)

    return jsonify({"overlays": upscaled_list}), 200
    
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
