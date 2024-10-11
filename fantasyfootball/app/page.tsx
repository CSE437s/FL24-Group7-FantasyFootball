"use client"; 
import { NextPage } from "next";
import Link from 'next/link';
import styles from '../styles/homePageLayout.module.css';
import { useState } from "react";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';


const HomePage: NextPage = () => {

  const [isMute, setIsMute] = useState<boolean>(false);

  

  const muteSound = () => {
    setIsMute(false);
  }
  return (
    <>
    <div className={styles.backdrop} />
      <AppBar position="static" className={styles.appBar}>
        <Toolbar>
          <Typography variant="h6" className={styles.title}>
            Fantasy Football Analytics
          </Typography>
          <div style={{ flexGrow: 1 }} /> {/* Spacer */}
          <Button onClick={muteSound} color="inherit">
            {isMute ? <VolumeMuteIcon /> : <VolumeUpIcon />}
          </Button>
          <Link href="/waiver-wire" passHref>
            <Button variant="contained" color="primary" className={styles.featureButton}>
              Waiver Wire Suggestions
            </Button>
          </Link>
          <Link href="/team-analyzer" passHref>
            <Button variant="contained" color="secondary" className={styles.featureButton}>
              Team Analyzer
            </Button>
          </Link>
          <Link href="/trade-builder" passHref>
            <Button variant="contained" color="success" className={styles.featureButton}>
              Trade Builder
            </Button>
          </Link>
        </Toolbar>
      </AppBar>
      <main>
        <div className={styles.App}>
          <h1 className={styles.bigtitle}>Welcome to Fantasy Football Analytics!</h1>
        </div>
      </main>
    </>
  );
}

export default HomePage;
