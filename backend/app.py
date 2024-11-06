# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
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
        model = None
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

# Preprocess the image with OpenCV to adapt the image to the model input (Image is in OpenCV BGR format)
def preprocess_image(image):    
    # Print initial image shape
    print(image.shape)
    
    # Resize the image depending on how large the image is keeping the ratio of the image
    if image.shape[0] > 300 or image.shape[1] > 300:
        if image.shape[0] > image.shape[1]:
            new_height = 300
            new_width = int(image.shape[1] * (new_height / image.shape[0]))
        else:
            new_width = 300
            new_height = int(image.shape[0] * (new_width / image.shape[1]))
        image = cv2.resize(image, (new_width, new_height))
    
    # Convert BGR to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect face (WARNING: Sometimes the face is not detected, even if it is in the image)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return None
    
    x, y, w, h = faces[0]
    face = gray[y:y+h, x:x+w]
    # Resize to match model input
    face = cv2.resize(face, (48, 48))
    # Normalize to [0,1]
    face = face.astype('float32') / 255.0
    # Add channel and batch dimensions
    face = np.expand_dims(face, axis=-1)  # Shape: (48, 48, 1)
    face = np.expand_dims(face, axis=0)   # Shape: (1, 48, 48, 1)
    return face

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
            # Read image file stream as bytes
            img_bytes = file.read()
            # Convert bytes to numpy array
            img_array = np.frombuffer(img_bytes, np.uint8)
            # Decode image as OpenCV format (BGR)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                print(f"{Bcolors.WARNING}Warning: Unable to decode image.{Bcolors.ENDC}")
                return jsonify({'error': 'Unable to decode image.'}), 400

            # Preprocess the image
            img = preprocess_image(img)
            if img is None:
                print(f"{Bcolors.WARNING}Warning: No face detected in the image.{Bcolors.ENDC}")
                return jsonify({'error': 'No face detected in the image.'}), 400

            if model is None:
                print(f"{Bcolors.FAIL}Error: Model is not loaded.{Bcolors.ENDC}")
                return jsonify({'error': 'Model is not loaded.'}), 500

            # Perform prediction
            predictions = model.predict(img)
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
    app.run()