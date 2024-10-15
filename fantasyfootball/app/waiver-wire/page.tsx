'use client';
import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/waiverWire.module.css';
import { useEffect, useState } from "react";

interface Player {
  Player: string; // Player name
  Pos: string;    // Player Position
  Rankbypos: number; // Player Position rank
  WK1Pts: number; 
  WK2Pts: number; 
  WK3Pts: number; 
  WK4Pts: number; 
  WK5Pts: number; 
  WK6Pts: number; 
}

const calculateWeekPerformance = (player: Player): string => {
  const weekPoints = [
    player.WK1Pts,
    player.WK2Pts,
    player.WK3Pts,
    player.WK4Pts,
    player.WK5Pts,
  ];
  
  const totalPoints = weekPoints.reduce((acc, points) => acc + points, 0);
  const averagePoints = totalPoints / weekPoints.length;
  const difference = player.WK6Pts - averagePoints;
  const performanceDescriptor = difference > 0 ? "above average" : "below average";
  
  return `${difference > 0 ? '+' : ''}${difference.toFixed(2)} pts ${performanceDescriptor}`;
};

const getStrengthsAndWeaknesses = (player: Player): string => {
  if (player.WK6Pts > 15) return "Strong performance";
  if (player.WK6Pts > 10) return "Average performance";
  return "Weak performance";
};

const WaiverWirePage: NextPage = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await fetch('/api/players'); // Fetch from the API route
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json(); // Parse the JSON
        
        // Filter players based on your criteria
        const filteredPlayers = data.filter((player: Player) => {
          const totalPoints = player.WK1Pts + player.WK2Pts + player.WK3Pts + player.WK4Pts + player.WK5Pts + player.WK6Pts;
          return totalPoints >= 10 && totalPoints < 50;
        });

        // Sort filtered players by position and name
        filteredPlayers.sort((a: Player, b: Player) => {
          const averageA = (a.WK1Pts + a.WK2Pts + a.WK3Pts + a.WK4Pts + a.WK5Pts) / 5;
          const averageB = (b.WK1Pts + b.WK2Pts + b.WK3Pts + b.WK4Pts + b.WK5Pts) / 5;
          const diffA = a.WK6Pts - averageA;
          const diffB = b.WK6Pts - averageB;
  
          return diffB - diffA; // Sort by the largest increase (Week 6 vs. average of previous weeks)
        });

        setPlayers(filteredPlayers); // Update state with fetched players
        console.log(filteredPlayers); // Log the fetched data for debugging
      } catch (err) {
        setError('Failed to load Waiver Wire data: ' + (err as Error).message);
      }
    };

    fetchPlayers(); // Call the function to fetch players
  }, []);

  if (error) {
    return <div className={styles.error}>{error}</div>; // Display error message if there's an error
  }

  return (
    <div className={styles.App}>
      <h1 className={styles.title}>Waiver Wire Insights</h1>
      <Link href="/" passHref>
        <button className={styles.homeButton}>Back to Homepage</button>
      </Link>
      <div className={styles.content}>
        <table className={styles.PlayerTable}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Position</th>
              <th>Week 6 Performance</th>
              <th>Analysis</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => {
              const strengthWeakness = getStrengthsAndWeaknesses(player); // Get strengths and weaknesses
              const weekPerformance = calculateWeekPerformance(player); // Calculate Week 6 performance

              return (
                <tr key={index}>
                  <td className={styles.td}>{player.Player}</td>
                  <td className={styles.td}>{player.Pos}</td>
                  <td className={styles.td}>{weekPerformance}</td> {/* Display Week 6 performance */}
                  <td className={styles.td}>{strengthWeakness}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default WaiverWirePage;


/*
Notes for waiver wire page:
Thinking maybe offer three insights per waiver wire player
--> (1): boom/bust --> is the player a consistent scorer, or more volatile. Maybe on scale of 1/10
--> (2): avg score of past position against opponent --> maybe percentile or ranking teams? (ex: Colts are 28th against WRs, so WRs may be a good play)
--> (3): team-fit score --> does the player fit in to your team, or do already have similar type of players?
Additional: maybe Watch list players to track, sort by insights (ex: boom players, consistent players)

Here are some suggestions for enhancing your waiver wire feature:

Boom/Bust Rating (1-10 scale):

Integrate historical data and use metrics like standard deviation of past performances to calculate a boom/bust score.
Add a color-coded visual indicator (green for consistent players, red for volatile ones) next to the score to help users quickly identify risky pickups.
Average Score Against Upcoming Opponent:

Pull in opponent defense data and calculate position-specific averages (e.g., RB fantasy points allowed per game).
Include a ranking or percentile system that compares the player's upcoming opponent with other teams, e.g., "28th out of 32 teams against WRs."
Team-Fit Score:

Compare the waiver wire player’s projected points to your team’s current players in the same position.
Consider adding filters based on team needs: if a user has an injury-prone player, suggest players with a higher availability or less risk.
Additionally:

Allow users to sort players by these insights.
Implement an “add to watchlist” button that allows users to track players they’re interested in but not ready to pick up.

*/

