"use client";
import { NextPage } from "next";
import styles from '../styles/homePageLayout.module.css';
import { useState, useRef, useEffect } from "react";
import { Button } from "@mui/material";
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import ReactAudioPlayer from 'react-audio-player';

const HomePage: NextPage = () => {
  const [isMute, setIsMute] = useState(false);
  const audioRef = useRef<ReactAudioPlayer>(null);

  const toggleMute = () => {
    setIsMute(!isMute);
  };

  const handleUserInteraction = () => {
    if (audioRef.current && audioRef.current.audioEl.current) {
      audioRef.current.audioEl.current.play();
    }
  };

  useEffect(() => {
    // Trigger autoplay by simulating user interaction
    const handleInteraction = () => {
      handleUserInteraction();
      window.removeEventListener('click', handleInteraction);
      window.removeEventListener('keypress', handleInteraction);
    };

    // Listen for user interaction to enable sound
    window.addEventListener('click', handleInteraction);
    window.addEventListener('keypress', handleInteraction);

    return () => {
      window.removeEventListener('click', handleInteraction);
      window.removeEventListener('keypress', handleInteraction);
    };
  }, []);
  

  return (
    <>
      <main>
        <div className={styles.App}>
          <h1 className={styles.title}>Hello World</h1>
          <ReactAudioPlayer
            src="/HomePage/FoxFootballSong.mp3"
            ref={audioRef}
            autoPlay
            muted={isMute}
          />
          <Button onClick={toggleMute}>
            {isMute ? <VolumeMuteIcon /> : <VolumeUpIcon />}
          </Button>
        </div>
      </main>
    </>
  );
};

export default HomePage;
