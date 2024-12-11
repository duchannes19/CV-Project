import React from 'react';
import { Box, Typography, Button } from '@mui/material';

export default function CaseReview({ caseData }) {
  // In a real scenario, load images, show annotations, etc.
  return (
    <Box>
      <Typography variant="h5">Review Case: {caseData.patient}</Typography>
      <Typography variant="body2">Uploaded on {caseData.date}</Typography>
      <Box mt={2}>
        {/* Placeholder for MRI viewer and segmentation overlays */}
        <Typography variant="body1" mb={2}>MRI/CT Images with segmentation overlays would appear here.</Typography>
        <Button variant="outlined">Adjust Segmentation</Button>
      </Box>
    </Box>
  );
}