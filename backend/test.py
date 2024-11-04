import cv2
import numpy as np

def preprocess_image(image):
    # Image is in OpenCV BGR format
    
    # Resize the image
    image = cv2.resize(image, (300, 300))
    
    # Convert BGR to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Print the shape of the grayscale image
    print(gray.shape)
    
    # Detect face
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

# Load the image
image = cv2.imread('test.jpg')
# Preprocess the image
processed_image = preprocess_image(image)

# Print the shape of the processed image
print(processed_image)