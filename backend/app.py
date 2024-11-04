# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from PIL import Image
import io
from Bcolors import Bcolors
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize and load the model
def init_model(path_name):
    try:
        model = load_model(path_name)
        print(f"{Bcolors.OKGREEN}Success: Model loaded successfully from {path_name}.{Bcolors.ENDC}")
    except Exception as e:
        print(f"{Bcolors.FAIL}Error: Failed to load model. {str(e)}{Bcolors.ENDC}")
        model = None  # You might want to handle this differently
    return model

model_path = 'model/mystery.h5'  # Update this path if necessary
model = init_model(model_path)

# Define emotion labels (ensure these match your training labels)
emotion_labels = {
    0: 'Angry',
    1: 'Disgust',
    2: 'Fear',
    3: 'Happy',
    4: 'Sad',
    5: 'Surprised',
    6: 'Neutral'
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    print(f"{Bcolors.OKBLUE}Health Check: Server is running.{Bcolors.ENDC}")
    return jsonify({'status': 'Model is up and running.'}), 200

@app.route('/predict', methods=['POST'])
def predict_emotion():
    if 'image' not in request.files:
        print(f"{Bcolors.WARNING}Warning: No image file provided in the request.{Bcolors.ENDC}")
        return jsonify({'error': 'No image file provided.'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        print(f"{Bcolors.WARNING}Warning: No file selected for uploading.{Bcolors.ENDC}")
        return jsonify({'error': 'No selected file.'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read image file stream
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes)).convert('L')  # Convert to grayscale
            img = img.resize((48, 48))  # Resize to match model input
            img_array = np.array(img)
            img_array = img_array.astype('float32') / 255.0  # Normalize to [0,1]
            img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension
            img_array = np.expand_dims(img_array, axis=0)   # Add batch dimension
            
            print(f"{Bcolors.OKCYAN}Info: Image preprocessed successfully.{Bcolors.ENDC}")

            if model is None:
                print(f"{Bcolors.FAIL}Error: Model is not loaded.{Bcolors.ENDC}")
                return jsonify({'error': 'Model is not loaded.'}), 500

            # Perform prediction
            predictions = model.predict(img_array)
            predicted_class = np.argmax(predictions, axis=1)[0]
            emotion = emotion_labels.get(predicted_class, 'Unknown')
            confidence = float(np.max(predictions))
            
            print(f"{Bcolors.OKGREEN}Prediction: {emotion} with confidence {confidence:.2f}{Bcolors.ENDC}")
            
            return jsonify({
                'emotion': emotion,
                'confidence': confidence
            }), 200
        
        except Exception as e:
            print(f"{Bcolors.FAIL}Error: An exception occurred during prediction. {str(e)}{Bcolors.ENDC}")
            return jsonify({'error': 'Error processing the image.'}), 500
    else:
        print(f"{Bcolors.WARNING}Warning: Unsupported file type uploaded.{Bcolors.ENDC}")
        return jsonify({'error': 'Unsupported file type.'}), 400

if __name__ == '__main__':
    # Run the Flask app
    print(f"{Bcolors.HEADER}Starting Flask server...{Bcolors.ENDC}")
    app.run(host='0.0.0.0', port=5000, debug=False)
