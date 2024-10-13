'use client';
import { useEffect, useState } from 'react';
import { YahooFantasy as YahooFantasyWrapper } from '../../lib/yahoo-fantasy-wrapper';
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
    <div>
      <h1>User Data</h1>
      <pre>{JSON.stringify(userData, null, 2)}</pre>
      {error && <p>Error: {error}</p>}
      <SignOutButton />
    </div>
  );
};

export default HomePage;
