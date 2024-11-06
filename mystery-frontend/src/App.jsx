// App.jsx
import React from 'react';
import CharacterGenerator from './components/charactergenerator';
import EmotionDetector from './components/emotions';
import { Button, Box, Alert } from '@mui/material';
import axios from 'axios';

function App() {
  const [choice, setChoice] = React.useState(0);
  const [isOnline, setIsOnline] = React.useState(true);

  React.useEffect(() => {
    const checkOnlineStatus = async () => {
      try {
        await axios.get('http://localhost:5000');
      } catch (error) {
        setIsOnline(false);
      }
    };

    checkOnlineStatus();
  } , []);

  return (
    <>
      {!isOnline && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 , position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%, -50%)'}}>
          <Alert severity='error'>The server is offline. Please try again later.</Alert>
        </Box>
      )}
      {choice === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 , position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)'}}>
          <Button variant='contained' onClick={() => setChoice(1)} disabled={!isOnline}>Character Generator</Button>
          <Button variant='contained' onClick={() => setChoice(2)} disabled={!isOnline}>Emotion Detector</Button>
        </Box>
      )}
      {choice === 1 && <CharacterGenerator />}
      {choice === 2 && <EmotionDetector />}
      {choice !== 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 , position: 'absolute', bottom: 0, left: '95%', transform: 'translate(-20%, -30%)'}}>
          <Button variant='contained' color='error' onClick={() => setChoice(0)}>Back</Button>
        </Box>
      )}
    </>
  );
}

export default App;