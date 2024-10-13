import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    console.log('Received sign-out request');
    
    // To avoid conflicts put any redirect/Absolute URL at the beginning
    const redirectUrl = new URL('/', request.url);

    // Clear the cookies
    const response = NextResponse.redirect(redirectUrl);
    response.cookies.set('accessToken', '', {
      httpOnly: true,
      maxAge: 0,
      path: '/',
    });
    response.cookies.set('refreshToken', '', {
      httpOnly: true,
      maxAge: 0,
      path: '/',
    });

    console.log('Successfully cleared cookies');
    return response;
  } catch (error) {
    console.error('Error during sign-out:', error);
    return NextResponse.json(
      { error: 'Failed to sign out' },
      { status: 500 }
    );
  }
}
