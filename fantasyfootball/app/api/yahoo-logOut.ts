import { NextResponse } from 'next/server';

export const signOut = () => {
  // Remove access token cookie
  document.cookie = 'accessToken=; Max-Age=0; path=/;'; // Clear the access token 

  // Redirect to the inital page 'localhost:3000'
  window.location.href = '/'; 
};
