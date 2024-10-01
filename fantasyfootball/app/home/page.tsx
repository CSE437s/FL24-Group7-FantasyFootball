// src/app/home/page.tsx
import { useEffect, useState } from 'react';

const HomePage: React.FC = () => {
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      const response = await fetch('https://fantasysports.yahooapis.com/fantasy/v2/user', {
        headers: {
          Authorization: `Bearer ${document.cookie
            .split('; ')
            .find(row => row.startsWith('accessToken='))
            ?.split('=')[1]}`, // Extract access token from cookies
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      } else {
        setError('Failed to fetch user data');
      }
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
