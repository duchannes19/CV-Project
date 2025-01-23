// src/App.jsx
import React, { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AnimatePresence, motion } from 'framer-motion';
import theme from './theme';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import { isAuthenticated } from './services/auth';

export default function App() {
  const [currentView, setCurrentView] = useState('login'); // 'login' or 'dashboard'
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (isAuthenticated()) {
      setCurrentView('dashboard');
    }
  }, []);

  const handleLogin = () => {
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setCurrentView('login');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AnimatePresence mode="wait">
        {currentView === 'login' ? (
          <motion.div
            key="login"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
          >
            <LoginPage onLoginSuccess={handleLogin} />
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.5 }}
          >
            <Dashboard onLogout={handleLogout} results={results} setResults={setResults} />
          </motion.div>
        )}
      </AnimatePresence>
    </ThemeProvider>
  );
}