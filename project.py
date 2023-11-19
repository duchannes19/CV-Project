#Import the libraries

import cv2
#import os
from matplotlib import pyplot as plt
import numpy as np
from skimage import feature as ft
from sklearn import svm
from sklearn.model_selection import train_test_split


photos_folder_path = 'photos'
photos = []  # Initialize the photos list

def load_photos():
    # Load the photos using a while inside the photos folder for each of the images inside the folder
    i = 1
    while True:
        # Load the image
        path = photos_folder_path + '/' + str(i) + '.jpg'
        img = cv2.imread(path)
        # If the image is not loaded, break the loop
        if img is None:
            break
        # Resize the image
        img = cv2.resize(img, (300, 300))
        # Convert the image to grayscale
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Append the image to the list
        i += 1
        photos.append(img)
    

load_photos()

print(photos)

# Shows the firt three images
#Comment bottom 3 lines to see all images
#for i in range(3):
#    cv2.imshow('image', photos[i])
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

def gradient_hue(img):
    # Convert the image to the HSL color space
    hsl_img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    
    # Extract the Hue, Lightness, and Saturation components
    hue = hsl_img[:, :, 0]
    lightness = hsl_img[:, :, 1]
    saturation = hsl_img[:, :, 2]
    
    # Calculate the gradient of the Hue component
    gradient_hue = np.gradient(hue)
    
    # Convert the gradient_hue list to a NumPy array
    gradient_hue = np.array(gradient_hue)
    
    # Apply thresholding to enhance the contrast
    threshold = 50
    gradient_hue[gradient_hue < threshold] = 0
    gradient_hue[gradient_hue >= threshold] = 255

    # Resize the lightness array to match the dimensions of gradient_hue
    lightness_resized = cv2.resize(lightness, (gradient_hue.shape[1], gradient_hue.shape[0]))

    # Combine the gradient of the Hue and Lightness components
    edges = cv2.bitwise_and(gradient_hue, lightness_resized)

    return edges

edges = gradient_hue(photos[0])

plt.subplot(121),plt.imshow(photos[0],cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])

plt.subplot(122),plt.imshow(edges,cmap = 'gray')

plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
