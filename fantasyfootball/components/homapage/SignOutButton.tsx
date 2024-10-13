import React from 'react';

const SignOutButton: React.FC = () => {

  const signOut = async () => {
    const res = await fetch('/api/sign-out');
    if(res.ok){
      // window.location.href = '/'; // We could comment this back in if we are loggin our users first through our website then connecting it to yahoo
      window.location.href = 'https://login.yahoo.com/config/login?logout=1&.direct=1'; // Does not redirect back to our website although we could do a set interval that will wait a couple of seconds to redirect them back here
    } else {
      console.log(res);
    }
  }

  return (
    <button onClick={signOut}>
      Sign Out
    </button>
  );
};

export default SignOutButton;

