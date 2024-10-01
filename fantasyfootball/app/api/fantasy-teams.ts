import { NextRequest, NextResponse } from 'next/server';
import YahooFantasy from 'yahoo-fantasy/dist/YahooFantasy.mjs';

const yf = new YahooFantasy(process.env.YAHOO_CLIENT_ID, process.env.YAHOO_CLIENT_SECRET);

export async function GET(request: NextRequest) {
  const token = request.headers.get('Authorization');

  if (!token) {
    return NextResponse.json({ error: 'No token provided' }, { status: 401 });
  }

  yf.setUserToken(token);

  try {
    const teams = await yf.user.game_teams('nfl');
    return NextResponse.json({ teams });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch teams' }, { status: 500 });
  }
}
