import React, { useState } from 'react';
import { Box, Button, Typography, LinearProgress } from '@mui/material';

export default function UploadImages() {
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileUpload = (files) => {
    // Simulate upload
    setUploadProgress(30);
    setTimeout(()=>setUploadProgress(60), 1000);
    setTimeout(()=>setUploadProgress(100), 2000);
  };

  return (
    <Box>
      <Typography variant="h5" mb={2}>Upload Medical Images</Typography>
      <Button variant="contained" component="label">
        Select Files
        <input type="file" hidden onChange={(e)=>handleFileUpload(e.target.files)} multiple />
      </Button>
      {uploadProgress > 0 && <LinearProgress variant="determinate" value={uploadProgress} sx={{mt:2}} />}
    </Box>
  );
}