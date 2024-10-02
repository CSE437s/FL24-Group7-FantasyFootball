// src/app/api/yahoo-oauth-initiate/route.ts
import { NextResponse } from 'next/server';
import crypto from 'crypto';

// Generate code verifier and challenge for PKCE
function generateCodeVerifier() {
  return crypto.randomBytes(32).toString('base64url');
}

async function generateCodeChallenge(verifier: string) {
  const hash = crypto.createHash('sha256').update(verifier).digest();
  return hash.toString('base64url');
}

export async function GET() {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);

  // Store the code verifier in a cookie or session (using a simple cookie here for example)
  const response = NextResponse.redirect(
    `https://api.login.yahoo.com/oauth2/request_auth?client_id=${process.env.YAHOO_CLIENT_ID}&redirect_uri=${encodeURIComponent(process.env.YAHOO_REDIRECT_URI as string)}&response_type=code&code_challenge=${codeChallenge}&code_challenge_method=S256`
  );

  // Store the code verifier in a secure cookie to retrieve later
  response.cookies.set('codeVerifier', codeVerifier, {
    httpOnly: true,
    maxAge: 300,
    path: '/',
  });

  return response;
}
