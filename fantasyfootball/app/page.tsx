"use client";
import { NextPage } from "next";
import styles from '../styles/homePageLayout.module.css';
import { useState } from "react";
import { Button } from "@mui/material";
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import testYahooService from "./api/yahoo/testYahooService";

const HomePage: NextPage = () => {

  const [isMute, setIsMute] = useState<boolean>(false);



  const muteSound = () => {
    setIsMute(false);
  }

  const runTestYahooService = async () => {
    try {
      const result = await testYahooService();
      console.log(result);
    } catch (error) {
      console.error("Error running handler:", error);
    }
  }


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
          <Button onClick={runTestYahooService}>Run API Test</Button>
        </div>
      </main>
    </>
  );
}



export default HomePage;
