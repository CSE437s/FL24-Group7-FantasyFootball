// app/api/yahoo/yahooService.ts
import axios from 'axios';
import { getYahooAccessToken } from './oauthService';

const YAHOO_API_BASE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2';

export const getYahooFantasyData = async (endpoint: string, params: any) => {
  try {
    const accessToken = await getYahooAccessToken();
    const response = await axios.get(`${YAHOO_API_BASE_URL}/${endpoint}`, {
      params,
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching Yahoo Fantasy data:', error);
    throw error;
  }
};