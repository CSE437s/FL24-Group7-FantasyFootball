// src/app/api/yahoo-oauth/route.ts
import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  // Retrieve the codeVerifier cookie as a RequestCookie object
  const codeVerifierCookie = request.cookies.get('codeVerifier');

  // Check if the code was provided
  if (!code) {
    return NextResponse.json({ error: 'No code provided' }, { status: 400 });
  }

  // Check if codeVerifier cookie exists and extract its value
  if (!codeVerifierCookie || !codeVerifierCookie.value) {
    return NextResponse.json({ error: 'No code verifier provided' }, { status: 400 });
  }

  // Get the actual string value of codeVerifier
  const codeVerifier = codeVerifierCookie.value; // Now this is the string

  try {
    // Exchange authorization code for access token
    const tokenResponse = await axios.post(
      'https://api.login.yahoo.com/oauth2/get_token',
      new URLSearchParams({
        client_id: process.env.YAHOO_CLIENT_ID!,
        client_secret: process.env.YAHOO_CLIENT_SECRET!,
        redirect_uri: process.env.YAHOO_REDIRECT_URI!,
        code,
        grant_type: 'authorization_code',
        code_verifier: codeVerifier, // Use the stored code verifier
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    console.log(tokenResponse.data);
    const { access_token, refresh_token } = tokenResponse.data;

    // Set cookies
    const response = NextResponse.json({ success: true }); // Create a response object
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

    // Redirect user after setting cookies
    response.headers.set('Location', '/home'); // Set the location header
    response.status = 302; // Set status to 302 for redirection

    return response;
  } catch (error) {
    console.error('Failed to exchange code for access token:', error);
    return NextResponse.json({ error: 'Failed to exchange code for token' }, { status: 500 });
  }
}
