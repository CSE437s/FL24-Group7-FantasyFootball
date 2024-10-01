// src/app/api/yahoo-oauth/route.ts
import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export async function GET(request: NextRequest) {
  console.log('API route hit');
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');

  if (!code) {
    console.log('No code provided');
    return NextResponse.json({ error: 'No code provided' }, { status: 400 });
  }

  try {
    const tokenResponse = await axios.post('https://api.login.yahoo.com/oauth2/get_token', new URLSearchParams({
      client_id: process.env.YAHOO_CLIENT_ID!,
      client_secret: process.env.YAHOO_CLIENT_SECRET!,
      redirect_uri: process.env.YAHOO_REDIRECT_URI!,
      code,
      grant_type: 'authorization_code',
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token } = tokenResponse.data;
    console.log('Access Token:', access_token);

    const response = NextResponse.redirect('/home');
    response.cookies.set('accessToken', access_token, {
      httpOnly: true,
      maxAge: 60 * 60,
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('Failed to get access token:', error);
    return NextResponse.json({ error: 'Failed to get access token' }, { status: 500 });
  }
}
