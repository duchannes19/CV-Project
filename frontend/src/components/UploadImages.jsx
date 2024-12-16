import React, { useState } from 'react';
import { Box, Button, Typography, LinearProgress } from '@mui/material';
import { runSegmentation } from '../services/api';

// MOCKUP COMPONENT

export default function UploadImages() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);

  const handleFileUpload = async (files) => {
    // Simulate upload
    let progress = 0;

    try{
      const response = await runSegmentation(files[0]);

      if (response.status === 200) {
        progress = 100;
        setResult(response.data.overlay);
      } else {
        progress = 0;
      }
    }
    catch(error){
      progress = 0;
      console.error(error);
    }

  };

  return (
    <Box>
      <Typography variant="h5" mb={2}>Upload Medical Images</Typography>
      <Button variant="contained" component="label">
        Select Files
        <input type="file" hidden onChange={(e)=>handleFileUpload(e.target.files)} multiple />
      </Button>
      {uploadProgress > 0 && <LinearProgress variant="determinate" value={uploadProgress} sx={{mt:2}} />}
      {result && 
      <Box mt={2}>
        <Typography variant="h6">Segmentation Overlay</Typography>
        <img src={result} alt="Segmentation Overlay" style={{maxWidth:'100%', marginTop:8}} />
      </Box>
      }
    </Box>
  );
}