import React, { useState } from 'react';
import { Box, Button, Typography, LinearProgress, Modal } from '@mui/material';
import { runSegmentation } from '../services/api';

export default function UploadImages({ results, setResults }) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadColor, setUploadColor] = useState('primary');
  // Get the results from the session storage if available
  const [currentSlice, setCurrentSlice] = useState(0); // Track the current image slice
  const [showSingleElements, setShowSingleElements] = useState(false);
  const [fullScreenImage, setFullScreenImage] = useState(null); // Track the image to display full screen

  const [showAdvancements, setShowAdvancements] = useState('');

  const handleFileUpload = async (files) => {
    setUploadColor('primary');
    setUploadProgress(0);
    setResults([]);
    setCurrentSlice(0);

    if (files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    const config = {
      headers: {
        'content-type': 'multipart/form-data',
      },
      onUploadProgress: function (progressEvent) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(progress);
      },
    };

    try {
      setShowAdvancements('Uploading files...');
      const response = await runSegmentation(formData, config);

      if (response.status === 200) {
        // response.data.overlays is expected to be an array of base64 strings
        setResults(response.data.overlays);
        // Save the results to the session storage
        //localStorage.setItem('segmentationResults', JSON.stringify(response.data.overlays));
        setShowAdvancements('Upload successful!');
        setUploadColor('success');
      } else {
        setUploadColor('error');
        setShowAdvancements('Upload failed. Please try again.');
        console.log('Upload failed with status:', response.data.error);
      }
    } catch (error) {
      setUploadColor('error');
      setShowAdvancements('Upload failed. Please try again.');
      console.error(error);
    }
  };

  const handleScroll = (event) => {
    if (results.length > 0) {
      if (event.deltaX > 0) {
        setCurrentSlice((prev) => Math.min(prev + 1, results.length - 1));
      } else if (event.deltaX < 0) {
        setCurrentSlice((prev) => Math.max(prev - 1, 0));
      }
    }
  };

  const openFullScreen = (image) => {
    setFullScreenImage(image);
  };

  const closeFullScreen = () => {
    setFullScreenImage(null);
  };

  return (
    <Box sx={{ margin: 'auto', textAlign: 'center', mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <img src="/cv.png" alt="Logo" style={{ width: '5rem', height: '5rem' }} />
        <Typography variant="h5" mb={2}>
          Upload MRI
        </Typography>
        {/*Mirror the first image*/}
        <img src="/cv.png" alt="Logo" style={{ width: '5rem', height: '5rem', transform: 'scaleX(-1)' }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', marginBottom: '2rem', marginTop: '5rem' }}>
        <Button variant="contained" component="label">
          Select Files
          <input type="file" hidden multiple onChange={(e) => handleFileUpload(e.target.files)} />
        </Button>
        {results.length > 0 && (
          <Button
            variant="contained"
            color="secondary"
            component="label"
            onClick={() => setShowSingleElements((prev) => !prev)}
          >
            {showSingleElements ? 'Show All' : 'Show Single'}
          </Button>
        )}
      </Box>
      {uploadProgress > 0 && (
        <LinearProgress
          variant="determinate"
          value={uploadProgress}
          sx={{ mt: 2 }}
          color={uploadColor}
        />
      )}
      {uploadProgress > 0 &&
        <Typography variant="h6" mt={2}>
          {showAdvancements}
        </Typography>
      }
      {!showSingleElements && results.length > 0 && (
        <Box mt={8} onWheel={handleScroll} sx={{ textAlign: 'center' }}>
          <Typography variant="h6" mb={2}>
            Slice {currentSlice + 1} / {results.length}
          </Typography>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '40rem', // Adjust height as needed
              overflow: 'hidden',
            }}
          >
            <img
              src={results[currentSlice]}
              alt={`Segmentation Overlay ${currentSlice}`}
              style={{ maxHeight: '100%', maxWidth: '100%', cursor: 'pointer' }}
              onClick={() => openFullScreen(results[currentSlice])}
            />
          </Box>
        </Box>
      )}

      {showSingleElements && results.length > 0 && (
        <Box mt={8} sx={{ textAlign: 'center' }}>
          {results.map((result, index) => (
            <Box key={index} sx={{ mt: 2 }}>
              <Typography variant="h6" mb={2}>
                Slice {index + 1} / {results.length}
              </Typography>
              <img
                src={result}
                alt={`Segmentation Overlay ${index}`}
                style={{ maxHeight: '40rem', maxWidth: '100%', cursor: 'pointer' }}
                onClick={() => openFullScreen(result)}
              />
            </Box>
          ))}
        </Box>
      )}

      {fullScreenImage && (
        <Modal open={true} onClose={closeFullScreen}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
            }}
          >
            <img
              src={fullScreenImage}
              alt="Full Screen View"
              style={{ maxHeight: '100%', maxWidth: '100%' }}
              onClick={closeFullScreen}
            />
          </Box>
        </Modal>
      )}
    </Box>
  );
}