'use client';
import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/teamAnalyzer.module.css';
import { useEffect, useState } from "react";

interface Player {
  Player: string; // Player name
  Pos: string;    // Player Position
  Rankbypos: number; // Player Position rank
  week1_points: number; 
  week2_points: number; 
  week3_points: number; 
  week4_points: number; 
  week5_points: number; 
  week6_points: number;
}



const analyzePlayer = (Player: Player) => {
  if (Player.Pos === 'QB' || Player.Pos === 'TE') {
    if (Player.Rankbypos === 1) {
      return 'A+: best at Position!';
    } else if (Player.Rankbypos >= 2 && Player.Rankbypos <= 5) {
      return 'A:';
    } else if (Player.Rankbypos > 5 && Player.Rankbypos <= 10) {
      return 'B';
    } else if (Player.Rankbypos > 10 && Player.Rankbypos <= 15) {
      return 'C';
    } else if (Player.Rankbypos > 15 && Player.Rankbypos <= 20) {
      return 'D';
    } else {
      return 'F';
    }
  } else if (Player.Pos === 'WR' || Player.Pos === 'RB') {
    if (Player.Rankbypos === 1) {
      return 'A+';
    } else if (Player.Rankbypos > 2 && Player.Rankbypos <= 5) {
      return 'A';
    } else if (Player.Rankbypos > 5 && Player.Rankbypos <= 10) {
      return 'B';
    } else if (Player.Rankbypos > 10 && Player.Rankbypos <= 15) {
      return 'C';
    } else if (Player.Rankbypos > 15 && Player.Rankbypos <= 20) {
      return 'D';
    } else {
      return 'F';
    }
  }
  return 'N/A';
};

const calculateConsistency = (Player: Player): [string, number | null] => {
  const weeklyPoints = [
    Player.week1_points,
    Player.week2_points,
    Player.week3_points,
    Player.week4_points,
    Player.week5_points,
    Player.week6_points,
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
  const [Players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await fetch('/api/players'); // Fetch from the API route
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        let data = await response.json(); // Parse the JSON
        
        data.sort((a: Player, b: Player) => {
          // First sort by Player name


          if (a.Pos < b.Pos) return -1;
          if (a.Pos > b.Pos) return 1;


          if (a.Player < b.Player) return -1;
          if (a.Player > b.Player) return 1;
        
          // If Player names are the same, sort by Pos
          
        
          // If both Player name and Pos are the same, sort by Rankbypos
          return a.Rankbypos - b.Rankbypos;
        });

        setPlayers(data); // Update state with fetched Players
        console.log(data); // Log the fetched data for debugging
      } catch (err) {
        setError('Failed to load Players data');
      }
    };

    fetchPlayers(); // Call the function to fetch Players
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
  <table className={styles.PlayerTable}>
    <thead>
      <tr>
        <th>Name</th>
        <th>Position</th>
        <th>Analysis</th> {/* New column for Rankbypos */}
        <th>Consistency Rating</th> {/* New column for Rankbypos */}
      </tr>
    </thead>
    <tbody>
  {Players.map((Player, index) => {

    return (
      <tr key={index}>
        <td className={styles.td}>{Player.Player}</td>
        <td className={styles.td}>{Player.Pos}</td> {/* Will show "N/A" if under 40 */}
        <td className={styles.td}>{analyzePlayer(Player)}</td> {/* Player rating */}
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

// <td className={styles.td}>{calculateConsistency(Player)}</td> {/* You can implement this based on stdDev */}


/*
Notes for Team Analyzer:
Thinking maybe offer three insights per waiver wire Player
--> (1): strengths and weaknesses by Position
--> (2): top place for improvement (and suggestions to achieve)

For your Team Analyzer page, here are a few suggestions to enhance the insights you want to offer:

Strengths and Weaknesses by Position:

Analyze each Position (QB, RB, WR, etc.) on the user’s team by comparing their Players to the league averages or median scores for that Position.
Provide a Positional rating (on a scale or percentile) to show how the user’s roster stacks up in each category.
You could use color coding (green for strong, yellow for average, red for weak) to highlight each Position's status at a glance.
Top Place for Improvement:

Identify the weakest Position based on current performance, projected future matchups, or Player injury risk.
Suggest waiver wire or trade options to improve the weakest Position, with detailed recommendations such as potential free agents or trade targets.
Additional features:

Bench Depth Analysis: Analyze bench Players and determine if any underperforming or injury-prone Players should be dropped or replaced with better options.
Bye Week Gaps: Highlight any bye week gaps, where multiple key Players are out in the same week, and suggest planning moves to mitigate that.
Injury Risk Alerts: Include a health check, flagging injury risks or currently injured Players and suggesting suitable replacements.


*/

