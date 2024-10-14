const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',        // DB username
  host: process.env.DB_HOST || 'localhost',       // DB host
  database: process.env.DB_NAME || 'fantasy_football_db',  // Your database name
  password: process.env.DB_PASSWORD || 'h2810039',  // DB password
  port: process.env.DB_PORT || 5432,              
});

export const getPlayers = async () => {
    try {
      // Fetch only the player names
      const res = await pool.query('SELECT name FROM week1stats'); 
      return res.rows; // Assuming res.rows contains an array of objects with 'name' key
    } catch (err) {
      console.error('Error querying players:', err);
      throw err; // Re-throw error for handling in the caller
    }
};
