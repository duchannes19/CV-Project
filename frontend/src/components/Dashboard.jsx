// src/components/Dashboard.jsx
import React, { useState } from 'react';
import { Box, AppBar, Toolbar, IconButton, Typography, Drawer, List, ListItem, ListItemText, Button } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { motion, AnimatePresence } from 'framer-motion';
import UploadImages from './UploadImages';
import CasesList from './CasesList';
import CaseReview from './CaseReview';
import ExportModal from './ExportModal';
import { logout } from '../services/auth';

export default function Dashboard({ onLogout }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentSection, setCurrentSection] = useState('upload'); // 'upload', 'cases', 'export', 'review'
  const [selectedCase, setSelectedCase] = useState(null);
  const [exportOpen, setExportOpen] = useState(false);

  const handleMenuClick = (section) => {
    setCurrentSection(section);
    setDrawerOpen(false);
  };

  const handleSelectCase = (caseData) => {
    setSelectedCase(caseData);
    setCurrentSection('review');
  };

  const handleExport = () => {
    setExportOpen(true);
    setDrawerOpen(false);
  };

  const handleLogoutClick = () => {
    logout();
    onLogout();
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" color="primary" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton color="inherit" onClick={() => setDrawerOpen(true)} edge="start" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Prostate MRI/CT Segmentation Tool
          </Typography>
          <Button color="inherit" onClick={handleLogoutClick}>Logout</Button>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 250 }} role="presentation" onClick={() => setDrawerOpen(false)} onKeyDown={() => setDrawerOpen(false)}>
          <List style={{ cursor: 'pointer' }}>
            <ListItem button onClick={() => handleMenuClick('upload')} style={{ marginTop: '3.5rem' }}>
              <ListItemText primary="Upload Images" />
            </ListItem>
            <ListItem button onClick={() => handleMenuClick('cases')}>
              <ListItemText primary="Review Cases" />
            </ListItem>
            <ListItem button onClick={handleExport}>
              <ListItemText primary="Export Results" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <AnimatePresence mode='wait'>
          {currentSection === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              transition={{ duration: 0.5 }}
            >
              <UploadImages />
            </motion.div>
          )}

          {currentSection === 'cases' && (
            <motion.div
              key="cases"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              transition={{ duration: 0.5 }}
            >
              <CasesList onSelectCase={handleSelectCase} />
            </motion.div>
          )}

          {currentSection === 'review' && selectedCase && (
            <motion.div
              key="review"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              transition={{ duration: 0.5 }}
            >
              <CaseReview caseData={selectedCase} />
            </motion.div>
          )}
        </AnimatePresence>
      </Box>

      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </Box>
  );
}