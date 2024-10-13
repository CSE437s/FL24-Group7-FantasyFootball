// src/app/api/yahoo-oauth/route.ts
import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');

  // Check if the code was provided
  if (!code) {
    console.error('No code provided in request');
    return NextResponse.json({ error: 'No code provided' }, { status: 400 });
  }
  
  try {
    // Exchange authorization code for access token
    const tokenResponse = await axios.post(
      'https://api.login.yahoo.com/oauth2/get_token',
      new URLSearchParams({
        client_id: process.env.YAHOO_CLIENT_ID!,
        client_secret: process.env.YAHOO_CLIENT_SECRET!,
        redirect_uri: process.env.YAHOO_REDIRECT_URI!,
        code: code,
        grant_type: 'authorization_code',
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    const { access_token, refresh_token } = tokenResponse.data;
    
     const response = NextResponse.redirect(new URL('/home', request.nextUrl.origin));

     // Set cookies for access and refresh tokens
     response.cookies.set('accessToken', access_token, {
       httpOnly: true,
       maxAge: 60 * 60, // 1 hour
       path: '/',
     });
 
     response.cookies.set('refreshToken', refresh_token, {
       httpOnly: true,
       maxAge: 60 * 60 * 24 * 30, // 30 days
       path: '/',
     });
  
     return response;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // Detailed Axios error logging
      console.error('Axios error occurred:', {
        message: error.message,
        code: error.code,
        config: error.config,
        responseData: error.response?.data, // Log the response from Yahoo if available
        responseStatus: error.response?.status, // HTTP status code from the response
      });
    } else {
      // General error logging
      console.error('An unexpected error occurred:', error);
    }

    // Return a more specific error message
    return NextResponse.json({ error: 'Failed to exchange code for token' }, { status: 500 });
  }
}
