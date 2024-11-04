import { useState } from 'react'
import './App.css'

import EmotionDetector from './components/emotions'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <EmotionDetector />
    </>
  )
}

export default App
