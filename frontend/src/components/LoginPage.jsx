// src/components/LoginPage.jsx
import React, { useState } from 'react';
import { Box, TextField, Typography, Button, Paper, IconButton, InputAdornment, Snackbar, Alert } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { login } from '../services/auth';
import TwoFADialog from './TwoFADialog';

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [twoFAOpen, setTwoFAOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'error' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      // Optionally show 2FA
      setTwoFAOpen(true);
    } else {
      setSnackbar({ open: true, message: 'Invalid credentials. Please try again.', severity: 'error' });
    }
  };

  const handle2FAVerification = (verified) => {
    setTwoFAOpen(false);
    if (verified) {
      onLoginSuccess();
    } else {
      setSnackbar({ open: true, message: '2FA Verification failed.', severity: 'error' });
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" height="100vh" bgcolor="#f0f2f5">
      <Paper elevation={6} sx={{ p: 4, borderRadius: 2, width: '400px' }}>
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} transition={{ duration: 0.5 }}>
          <Typography variant="h5" mb={2} align="center">Doctor Login</Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              label="Username (Hospital ID)"
              variant="outlined"
              fullWidth
              margin="normal"
              required
              value={username}
              onChange={(e)=>setUsername(e.target.value)}
            />
            <TextField
              label="Password"
              variant="outlined"
              type={showPassword ? 'text' : 'password'}
              fullWidth
              margin="normal"
              required
              value={password}
              onChange={(e)=>setPassword(e.target.value)}
              helperText="Use at least 8 characters, including letters, numbers, and symbols."
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={()=>setShowPassword(!showPassword)} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt:2 }}>
              Login
            </Button>
          </form>
        </motion.div>
      </Paper>
      <TwoFADialog open={twoFAOpen} onClose={handle2FAVerification} />
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
