// pages/api/yahoo/fantasy.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { getYahooFantasyData } from './yahooService';

// export default async function handler(req: NextApiRequest, res: NextApiResponse) {
//   const { endpoint, params } = req.query;

//   try {
//     const data = await getYahooFantasyData(endpoint as string, params);
//     res.status(200).json(data);
//   } catch (error) {
//     res.status(500).json({ error: 'Failed to fetch data from Yahoo Fantasy API' });
//   }
// }



export 