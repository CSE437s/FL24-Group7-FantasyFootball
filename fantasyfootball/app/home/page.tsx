'use client';
import { useEffect, useState } from 'react';
import { NextPage } from "next";
import Link from 'next/link';
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';
import { YahooFantasy as YahooFantasyWrapper } from '../../lib/yahoo-fantasy-wrapper';
import styles from '../../styles/loggedIn.module.css'
import SignOutButton from '../../components/homapage/SignOutButton';
interface Cookies {
  accessToken: string;
  refreshToken: string;
}

const HomePage: React.FC = () => {
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<Cookies>();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const res = await fetch('/api/get-cookies');
        const data = await res.json();
        setData(data as Cookies);

        const YahooFantasy = await YahooFantasyWrapper();
        const yf = new YahooFantasy(
          process.env.YAHOO_CLIENT_ID!,
          process.env.YAHOO_CLIENT_SECRET!
        );

        yf.setUserToken(data.accessToken);
        yf.setRefreshToken(data.refreshToken);


        // Using the API fetch Data here ------
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError('Failed to load user data.');
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
      <>
      <div className={styles.backdrop} />
        <AppBar position="static" className={styles.appBar}>
          <Toolbar>
            <Typography variant="h6" className={styles.title}>
              Fantasy Football Analytics
            </Typography>
            <div style={{ flexGrow: 1 }} /> {/* Spacer */}
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
            <pre>{JSON.stringify(userData, null, 2)}</pre>
            {error && <p>Error: {error}</p>}
            <SignOutButton />
          </div>
        </main>
      </>
    );
};

export default HomePage;


