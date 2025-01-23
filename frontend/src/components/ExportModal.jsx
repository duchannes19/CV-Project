import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  CircularProgress,
  Typography,
} from '@mui/material';
import { motion } from 'framer-motion';
import JSZip from 'jszip';

// Helper function to extract base64 from Data URL and convert to Uint8Array
function dataURLToUint8Array(dataURL) {
  const base64Index = dataURL.indexOf(',') + 1;
  const base64 = dataURL.substring(base64Index);
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

export default function ExportModal({ open, onClose, results }) {
  const [format, setFormat] = useState('PNG');
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState('');

  const fileAvailable = results.length > 0;

  const handleExport = async () => {
    setError('');
    setIsExporting(true);
    try {
      if (!fileAvailable) {
        alert('No results to export.');
        onClose();
        return;
      }

      const zip = new JSZip();
      const formatExtension = {
        DICOM: 'dcm',
        NIfTI: 'nii',
        PNG: 'png',
      }[format] || 'bin';

      // Process files in parallel
      const files = results.map((dataURL, index) => {
        const binaryData = dataURLToUint8Array(dataURL);
        const filename = `image_${index + 1}.${formatExtension}`;
        return zip.file(filename, binaryData);
      });

      // Wait for all files to be added (optional, as JSZip handles it internally)
      await Promise.all(files);

      // Generate ZIP file
      const zipBlob = await zip.generateAsync({ type: 'blob' });

      // Trigger download
      const url = URL.createObjectURL(zipBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `segmentation_results_${format}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      onClose();
    } catch (err) {
      console.error('Export error:', err);
      setError('Export failed. Please check the console for details.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <DialogTitle>Export Results</DialogTitle>
        <DialogContent dividers>
          <FormControl fullWidth margin="normal">
            <FormLabel>Format</FormLabel>
            <Select value={format} onChange={(e) => setFormat(e.target.value)}>
              <MenuItem value="DICOM">DICOM</MenuItem>
              <MenuItem value="NIfTI">NIfTI</MenuItem>
              <MenuItem value="PNG">PNG</MenuItem>
            </Select>
          </FormControl>
          {error && (
            <Typography color="error" variant="body2">
              {error}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button variant="outlined" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleExport}
            disabled={!fileAvailable || isExporting}
            startIcon={isExporting && <CircularProgress size={20} />}
          >
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        </DialogActions>
      </motion.div>
    </Dialog>
  );
}
