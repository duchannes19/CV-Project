// Background.jsx
import React, { useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

const Background = () => {
  const { scene } = useThree(); // Access the scene using useThree
  const colorRef = useRef(new THREE.Color(Math.random(), Math.random(), Math.random()));
  const targetColor = useRef(new THREE.Color(Math.random(), Math.random(), Math.random()));
  const clock = useRef(new THREE.Clock());

  useFrame(() => {
    const delta = clock.current.getDelta();
    
    // Smoothly transition to target color
    colorRef.current.lerp(targetColor.current, delta * 0.1);
    scene.background = colorRef.current;
    scene.fog.color = colorRef.current;

    // Randomly change target color every few seconds
    if (Math.random() < delta * 0.1) {
      targetColor.current = new THREE.Color(Math.random(), Math.random(), Math.random());
    }
  });

  useEffect(() => {
    // Initialize fog with the initial background color
    scene.fog = new THREE.FogExp2(colorRef.current, 0.5);
  }, [scene]);

  return null; // This component doesn't render anything itself
};

const BackgroundCanvas = () => (
  <Canvas
    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
    camera={{ position: [0, 0, 5] }} // Adjust camera position as needed
  >
    <Background />
    {/* Add other 3D objects or components here if needed */}
  </Canvas>
);

export default BackgroundCanvas;