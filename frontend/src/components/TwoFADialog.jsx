// src/components/TwoFADialog.jsx
import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button, Typography } from '@mui/material';
import { motion } from 'framer-motion';

export default function TwoFADialog({ open, onClose }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleVerify = () => {
    // Simulate 2FA verification
    if (code === '123456') { // Replace with actual verification
      onClose(true);
    } else {
      setError('Invalid 2FA code. Please try again.');
    }
  };

  const handleClose = () => {
    onClose(false);
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="xs">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <DialogTitle>Two-Factor Authentication</DialogTitle>
        <DialogContent>
          <Typography variant="body2" mb={2}>
            Please enter the 2FA code sent to your registered device.
          </Typography>
          <TextField
            label="2FA Code"
            fullWidth
            value={code}
            onChange={(e)=>setCode(e.target.value)}
            error={!!error}
            helperText={error}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleVerify}>Verify</Button>
        </DialogActions>
      </motion.div>
    </Dialog>
  );
}