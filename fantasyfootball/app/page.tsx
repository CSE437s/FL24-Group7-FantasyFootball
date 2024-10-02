"use client";
import { NextPage } from "next";
import styles from '../styles/homePageLayout.module.css';
import { use, useEffect, useState } from "react";
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import { Button, Snackbar } from '@mui/material';
import LoginButton from "../components/homapage/LoginButton";

const HomePage: NextPage = () => {
  
  const [open, setOpen] = useState(false);
  const [isMute, setIsMute] = useState<boolean>(false);

  const muteSound = () => {
    setIsMute(false);
  }

  const handleSnackBarClick = () => {
    setOpen(true);
  };
  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  };

  useEffect(() => {
    document.cookie = 'accessToken=; Max-Age=0; path=/;';
  })

  useEffect(() => {
    console.log(process.env.YAHOO_REDIRECT_URI);
  }, []);
  return (
    <>
      <main>
        <div className={styles.App}>
          <h1 className={styles.title}>Hello World</h1>
          {isMute ? (
            <Button onClick={muteSound}><VolumeMuteIcon /></Button>
          ) : (
            <Button onClick={muteSound}><VolumeUpIcon /></Button>
          )
          }
         <LoginButton />
        </div>
      </main>
    </>
  );
}



export default HomePage;
