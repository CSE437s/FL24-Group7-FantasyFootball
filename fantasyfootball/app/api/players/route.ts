// // app/api/players/route.ts
// import { NextResponse } from 'next/server';
// import { Pool } from 'pg';

// const pool = new Pool({
//   user: process.env.DB_USER || 'postgres',
//   host: process.env.DB_HOST || 'localhost',
//   database: process.env.DB_NAME || 'fantasy_football_db',
//   password: process.env.DB_PASSWORD || 'h2810039',
// });

// export async function GET() {
//   try {
//     const res = await pool.query('SELECT player, pos, rank_by_pos FROM seasonstats');
//     return NextResponse.json(res.rows); // Return the player names as JSON
//   } catch (err) {
//     console.error('Error querying players:', err);
//     return NextResponse.json({ error: 'Failed to load players data' }, { status: 500 });
//   }
// }


