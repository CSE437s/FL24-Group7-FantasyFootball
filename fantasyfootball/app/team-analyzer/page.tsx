'use client';
import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/teamAnalyzer.module.css';
import { useEffect, useState } from "react";

interface Player {
  player: string; // Player name
  pos: string;    // Player position
  posrank: number; // Player position rank
  week1_points: number; 
  week2_points: number; 
  week3_points: number; 
  week4_points: number; 
  week5_points: number; 
  week6_points: number;
}



const analyzePlayer = (player: Player) => {
  if (player.pos === 'QB' || player.pos === 'TE') {
    if (player.posrank === 1) {
      return 'A+: best at position!';
    } else if (player.posrank >= 2 && player.posrank <= 5) {
      return 'A:';
    } else if (player.posrank > 5 && player.posrank <= 10) {
      return 'B';
    } else if (player.posrank > 10 && player.posrank <= 15) {
      return 'C';
    } else if (player.posrank > 15 && player.posrank <= 20) {
      return 'D';
    } else {
      return 'F';
    }
  } else if (player.pos === 'WR' || player.pos === 'RB') {
    if (player.posrank === 1) {
      return 'A+';
    } else if (player.posrank > 2 && player.posrank <= 5) {
      return 'A';
    } else if (player.posrank > 5 && player.posrank <= 10) {
      return 'B';
    } else if (player.posrank > 10 && player.posrank <= 15) {
      return 'C';
    } else if (player.posrank > 15 && player.posrank <= 20) {
      return 'D';
    } else {
      return 'F';
    }
  }
  return 'N/A';
};

const calculateConsistency = (player: Player): [string, number | null] => {
  const weeklyPoints = [
    player.week1_points,
    player.week2_points,
    player.week3_points,
    player.week4_points,
    player.week5_points,
    player.week6_points,
  ];

  const totalPoints = weeklyPoints.reduce((acc, points) => acc + points, 0);
  
  // If total points are less than 40, return "N/A" and null for stdDev
  if (totalPoints < 40) {
    return ["N/A", null];
  }

  // Calculate standard deviation for consistency
  const mean = totalPoints / weeklyPoints.length;
  const variance =
    weeklyPoints.reduce((acc, points) => acc + Math.pow(points - mean, 2), 0) /
    weeklyPoints.length;

  const stdDev = Math.sqrt(variance);
  return [totalPoints.toString(), stdDev]; // Convert totalPoints to string for rendering
};



const TeamAnalyzerPage: NextPage = () => {
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
        setPlayers(data); // Update state with fetched players
        console.log(data); // Log the fetched data for debugging
      } catch (err) {
        setError('Failed to load players data');
      }
    };

    fetchPlayers(); // Call the function to fetch players
  }, []);

  if (error) {
    return <div className={styles.error}>{error}</div>; // Display error message if there's an error
  }

  return (
    <div className={styles.App}>
      <h1 className={styles.title}>Team Analyzer</h1>
      <h2 className={styles.leagueteam}>**League Name**: **Team Name**</h2>
      <Link href="/" passHref>
        <button className={styles.homeButton}>Back to Homepage</button>
      </Link>
      <div className={styles.content}>
  <table className={styles.playerTable}>
    <thead>
      <tr>
        <th>Name</th>
        <th>Position</th>
        <th>Analysis</th> {/* New column for PosRank */}
        <th>Consistency Rating</th> {/* New column for PosRank */}
      </tr>
    </thead>
    <tbody>
  {players.map((player, index) => {

    return (
      <tr key={index}>
        <td className={styles.td}>{player.player}</td>
        <td className={styles.td}>{player.pos}</td> {/* Will show "N/A" if under 40 */}
        <td className={styles.td}>{analyzePlayer(player)}</td> {/* Player rating */}
        <td className={styles.td}>{calculateConsistency(player)}</td> {/* You can implement this based on stdDev */}
      </tr>
    );
  })}
</tbody>
  </table>
</div>
    </div>
  );
};

export default TeamAnalyzerPage;


/*
Notes for Team Analyzer:
Thinking maybe offer three insights per waiver wire player
--> (1): strengths and weaknesses by position
--> (2): top place for improvement (and suggestions to achieve)

For your Team Analyzer page, here are a few suggestions to enhance the insights you want to offer:

Strengths and Weaknesses by Position:

Analyze each position (QB, RB, WR, etc.) on the user’s team by comparing their players to the league averages or median scores for that position.
Provide a positional rating (on a scale or percentile) to show how the user’s roster stacks up in each category.
You could use color coding (green for strong, yellow for average, red for weak) to highlight each position's status at a glance.
Top Place for Improvement:

Identify the weakest position based on current performance, projected future matchups, or player injury risk.
Suggest waiver wire or trade options to improve the weakest position, with detailed recommendations such as potential free agents or trade targets.
Additional features:

Bench Depth Analysis: Analyze bench players and determine if any underperforming or injury-prone players should be dropped or replaced with better options.
Bye Week Gaps: Highlight any bye week gaps, where multiple key players are out in the same week, and suggest planning moves to mitigate that.
Injury Risk Alerts: Include a health check, flagging injury risks or currently injured players and suggesting suitable replacements.


*/

