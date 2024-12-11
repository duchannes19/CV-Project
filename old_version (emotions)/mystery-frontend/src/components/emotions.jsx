// src/components/EmotionDetector.jsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { UploadFile } from '@mui/icons-material';

const EmotionDetector = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [emotion, setEmotion] = useState('');
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleButtonClick = () => {
    document.getElementById('fileInput').click();
  };

  const handleFileChange = async (event) => {
    setError(null);
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      await sendImage(file);
    }
  };

  const sendImage = async (file) => {
    setLoading(true);
    setEmotion('');
    setConfidence(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Error in server response');
      }

      const data = await response.json();
      setEmotion(data.emotion);
      setConfidence((data.confidence * 100).toFixed(2));
    } catch (err) {
      setError('Failed to get emotion prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100vh"
    >

      {selectedFile && (
        <Box mt={3}>
          <img
            src={URL.createObjectURL(selectedFile)}
            alt="Selected"
            style={{ width: '300px' }}
          />
        </Box>
      )}
      <input
        type="file"
        id="fileInput"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <Button
        variant="contained"
        color="primary"
        onClick={handleButtonClick}
        startIcon={<UploadFile />}
        disabled={loading}
        size="large"
      >
        Upload Image
      </Button>

      {loading && (
        <Box mt={3}>
          <CircularProgress />
          <Typography variant="body1" mt={2}>
            Analyzing image...
          </Typography>
        </Box>
      )}

      {emotion && (
        <Box mt={3} textAlign="center">
          <Typography variant="h5">Detected Emotion:</Typography>
          <Typography variant="h4" color="secondary">
            {emotion}
          </Typography>
          <Typography variant="body1">
            Confidence: {confidence}%
          </Typography>
        </Box>
      )}

      {error && (
        <Box mt={3}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}
    </Box>
  );
};

export default EmotionDetector;
