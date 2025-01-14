import React, { useState } from 'react';
import { Box, Button, Typography, LinearProgress } from '@mui/material';
import { runSegmentation } from '../services/api';

export default function UploadImages() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadColor, setUploadColor] = useState('primary');
  const [results, setResults] = useState([]);

  const handleFileUpload = async (files) => {
    setUploadColor('primary');
    setUploadProgress(0);
    setResults([]);

    if (files.length === 0) return;

    const formData = new FormData();
    for (let i=0; i<files.length; i++) {
      formData.append('files', files[i]);
    }

    const config = {
      headers: {
        'content-type': 'multipart/form-data'
      },
      onUploadProgress: function(progressEvent) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(progress);
      }
    };

    try {
      const response = await runSegmentation(formData, config);

      if (response.status === 200) {
        // response.data.overlays is expected to be an array of base64 strings
        setResults(response.data.overlays);
        setUploadColor('success');
      } else {
        setUploadColor('error');
        console.log("Upload failed with status:", response.data.error);
      }
    } catch (error) {
      setUploadColor('error'); 
      setUploadColor(100);
      console.error(error);
      console.log(response.data.error);
    }
  };

  return (
    <Box sx={{ margin: 'auto', textAlign: 'center', mt: 4}}>
      <Typography variant="h5" mb={2}>Upload Medical Images</Typography>
      <Button variant="contained" component="label" style={{marginTop: '1rem'}}>
        Select Files
        <input type="file" hidden multiple onChange={(e)=>handleFileUpload(e.target.files)} />
      </Button>
      {uploadProgress > 0 && <LinearProgress variant="determinate" value={uploadProgress} sx={{mt:2}} color={uploadColor} />}
      {results.length > 0 &&
      <Box mt={8}>
        <Typography variant="h6" mb={6} >Segmentation Overlays</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 5, mt: 2, width: '100%', justifyContent: 'center' }}>
          {results.map((overlay, idx) => (
            <Box key={idx} sx={{ border: '1px solid #ccc', p:1 }}>
              <img src={overlay} alt={`Segmentation Overlay ${idx}`} style={{maxWidth:'100%'}} />
            </Box>
          ))}
        </Box>
      </Box>
      }
    </Box>
  );
}