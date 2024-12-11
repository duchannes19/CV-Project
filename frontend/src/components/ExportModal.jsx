import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';
import { motion } from 'framer-motion';

export default function ExportModal({ open, onClose }) {
  const [format, setFormat] = useState('DICOM');
  const [password, setPassword] = useState('');

  const handleExport = () => {
    // Implement secure export logic
    // Encrypt files with the given password or passphrase
    alert(`Exporting as ${format} with password: ${password ? 'Provided' : 'None'}`);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <motion.div initial={{ scale:0.9, opacity:0 }} animate={{scale:1, opacity:1}} transition={{duration:0.3}}>
        <DialogTitle>Export Results</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Format</InputLabel>
            <Select value={format} onChange={(e)=>setFormat(e.target.value)}>
              <MenuItem value="DICOM">DICOM</MenuItem>
              <MenuItem value="NIfTI">NIfTI</MenuItem>
              <MenuItem value="PNG">PNG</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="Encryption Password (optional)"
            fullWidth
            type="password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            helperText="Set a password/passphrase for secure encryption."
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button variant="outlined" onClick={onClose}>Cancel</Button>
          <Button variant="contained" onClick={handleExport}>Export</Button>
        </DialogActions>
      </motion.div>
    </Dialog>
  );
}