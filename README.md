# CV Project

<p align="center">
    <img src="cv.png" alt="Image" width="30%" height="30%">
</p>

## General Idea

Hello!

This project aims to simplify and assist in the recognition of the prostate through a user-friendly frontend and a Python backend that handles convolutional neural network (CNN) processing. Specifically, it is a Python backend and Vite.js frontend application focused on the automatic segmentation of prostate cancer regions in MRI and CT images.

Key Features:
- Employs convolutional neural networks (Unet CNNs) and their variants for segmentation.
- Informed by the findings in the paper 'Recent Automatic Segmentation Algorithms of MRI Prostate Regions: A Review.'

The frontend, built with Vite.js, provides an intuitive interface for users to upload and visualize MRI and CT images. The backend, developed in Python, processes these images using CNN models to automatically segment and highlight regions affected by prostate cancer.

## Dependencies for Backend

- Python 3.9
- Anaconda
- Intall the required envioronment using the following command:
```bash
conda env create -f environment.yml
```

## Dependencies for Frontend

- Install the required packages using the following command:
```bash
npm install
```

## How to run the project

- Run the backend using the following command:
```bash
python app.py
```

- Run the frontend using the following command:
```bash
npm run dev
```