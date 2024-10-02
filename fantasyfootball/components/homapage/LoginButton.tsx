// components/LoginButton.tsx
import { useState } from 'react';

const LoginButton: React.FC = () => {
  const redirectUri = encodeURIComponent(process.env.YAHOO_REDIRECT_URI as string);
  const yahooURL = `https://api.login.yahoo.com/oauth2/request_auth?client_id=${process.env.YAHOO_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code`;

  const handleLogin = () => {
    // Redirect to Yahoo login URL
    window.location.href = '/api/yahoo-oauth-initiate';
  };

  return (
    <div>
      <button onClick={handleLogin}>Login with Yahoo</button>
    </div>
  );
};

export default LoginButton;
