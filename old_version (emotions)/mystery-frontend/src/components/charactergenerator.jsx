// CharacterGenerator.jsx
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Webcam from 'react-webcam';
import axios from 'axios';
import BackgroundCanvas from './background';
import { Button } from '@mui/material';

import '../styles/styles.css';

const sentences = [
  "Imagine you're facing a mighty dragon...",
  "Now, think of your happiest memory...",
  "Show us your determination in battle...",
  // Add more sentences as needed
];

const CharacterGenerator = () => {
  const [stage, setStage] = useState('start'); // stages: start, instructions, capture, result
  const [currentSentence, setCurrentSentence] = useState(0);
  const [emotions, setEmotions] = useState([]);
  const webcamRef = useRef(null);

  const handleStart = () => {
    setStage('instructions');
  };

  const handleCapture = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      try {
        const formData = new FormData();
        // Convert base64 to blob
        const res = await fetch(imageSrc);
        const blob = await res.blob();
        formData.append('image', blob, 'image.jpg');

        const response = await axios.post('http://localhost:5000/predict', formData);
        const { emotion } = response.data;

        setEmotions([...emotions, emotion]);

        if (currentSentence < sentences.length - 1) {
          setCurrentSentence(currentSentence + 1);
        } else {
          setStage('result');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('There was an error processing your image. Please try again.');
      }
    }
  };

  const handleRetake = () => {
    setEmotions([]);
    setCurrentSentence(0);
    setStage('start');
  };

  // Begin capturing after showing instructions, needs to add distinct stages
  useEffect(() => {
    if (stage === 'instructions') {
        const timer = setTimeout(() => {
            setStage('capture');
            handleCapture();
        }, 5000);
        return () => clearTimeout(timer);
    }}, [stage]);

  // Estimate character based on emotions
  const estimateCharacter = () => {
    // Simple logic to determine character type and class
    // This should be replaced with your actual logic
    const emotionCounts = emotions.reduce((acc, emotion) => {
      acc[emotion] = (acc[emotion] || 0) + 1;
      return acc;
    }, {});

    const maxEmotion = Object.keys(emotionCounts).reduce((a, b) =>
      emotionCounts[a] > emotionCounts[b] ? a : b
    );

    let characterType = 'Human';
    let characterClass = 'Warrior';

    if (maxEmotion === 'Happy') {
      characterType = 'Elf';
      characterClass = 'Bard';
    } else if (maxEmotion === 'Angry') {
      characterType = 'Orc';
      characterClass = 'Barbarian';
    } else if (maxEmotion === 'Sad') {
      characterType = 'Dwarf';
      characterClass = 'Cleric';
    }
    // Add more mappings as needed

    return { characterType, characterClass };
  };

  return (
    <div style={{ position: 'relative', height: '100vh' }}>
      <BackgroundCanvas />

      <AnimatePresence>
        {stage === 'start' && (
          <motion.div
            key="start"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
            }}
          >
            <h1>Mystery</h1>
            <Button variant="contained" color="primary" onClick={handleStart}>
                Start
            </Button>
          </motion.div>
        )}

        {stage === 'instructions' && (
          <motion.div
            key="instructions"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'absolute',
              top: '10%',
              left: '50%',
              transform: 'translateX(-50%)',
              textAlign: 'center',
            }}
          >
            <h2>{sentences[currentSentence]}</h2>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              style={{
                marginTop: '20px',
                marginBottom: '50px',
              }}
            />
          </motion.div>
        )}

        {stage === 'result' && (
          <motion.div
            key="result"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
            }}
          >
            <h2>Your DnD Character</h2>
            <p>Analyzing your emotions...</p>
            {(() => {
              const { characterType, characterClass } = estimateCharacter();
              return (
                <>
                  <h3>Race: {characterType}</h3>
                  <h3>Class: {characterClass}</h3>
                </>
              );
            })()}
            <button onClick={handleRetake}>Try Again</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CharacterGenerator;
