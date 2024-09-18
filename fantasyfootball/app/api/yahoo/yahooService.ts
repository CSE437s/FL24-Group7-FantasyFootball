// app/api/yahoo/yahooService.ts
import axios from 'axios';

const YAHOO_API_BASE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2';

export const getYahooFantasyData = async (endpoint: string, params: any) => {
  try {
    const response = await axios.get(`${YAHOO_API_BASE_URL}/${endpoint}`, {
      params,
      headers: {
        Authorization: `Bearer ${process.env.YAHOO_API_TOKEN}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching Yahoo Fantasy data:', error);
    throw error;
  }
};