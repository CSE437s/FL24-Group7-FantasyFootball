// components/SignOutButton.tsx
import React from 'react';
import { signOut } from '@/api/yahoo-logOut';

const SignOutButton: React.FC = () => {
  return (
    <button onClick={signOut}>
      Sign Out
    </button>
  );
};

export default SignOutButton;
  
  