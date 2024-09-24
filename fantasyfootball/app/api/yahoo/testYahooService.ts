// testYahooService.ts
import { getYahooFantasyData } from './yahooService';


export const testYahooService = async () => {
  try {
    const endpoint = 'users;use_login=1'; // Replace with a valid endpoint
    const params = {}; // Replace with any necessary parameters

    const data = await getYahooFantasyData(endpoint, params);
    console.log('Yahoo Fantasy Data:', data);
  } catch (error) {
    console.error('Test failed:', error);
  }
};

testYahooService();