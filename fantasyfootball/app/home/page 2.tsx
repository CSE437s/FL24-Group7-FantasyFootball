// src/app/home/page.tsx
'use client';
import { useEffect, useState } from 'react';
import YahooFantasy from 'yahoo-fantasy';

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

      fetch('/api/get-cookies')
        .then(res => res.json())
        .then(data => {
          setData(data as Cookies);
        })
        .catch(err => console.error(err));
      
      const yf = new YahooFantasy(
        process.env.YAHOO_CLIENT_ID, // Yahoo! Application Key
        process.env.YAHOO_CLIENT_SECRET, // Yahoo! Application Secret
      );

      yf.setUserToken(
        data?.accessToken
      );

      yf.setRefreshToken(
        data?.refreshToken
      );
      


      setLoading(false);
    };

    fetchUserData();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>User Data</h1>
      <pre>{JSON.stringify(userData, null, 2)}</pre>
    </div>
  );
};

export default HomePage;
