'use client';
import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/teamAnalyzer.module.css';
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

const calculateWeek6Performance = (Player: Player): string => {
  const weekPoints = [
    Player.WK1Pts,
    Player.WK2Pts,
    Player.WK3Pts,
    Player.WK4Pts,
    Player.WK5Pts,
  ];
  
  const averagePoints = weekPoints.reduce((acc, points) => acc + points, 0) / weekPoints.length;
  const difference = Player.WK6Pts - averagePoints;
  const performanceDescriptor = difference > 0 ? "above average" : "below average";
  
  return `${difference > 0 ? '+' : ''}${difference.toFixed(2)} pts ${performanceDescriptor}`;
};

const getConsistencyGrade = (stdDev: number | null): string => {
  if (stdDev === null) return "N/A"; // Handle case for players with less than 40 total points

  if (stdDev <= 4) return 'A+';  // Most consistent
  if (stdDev <= 4.75) return 'A';  // Most consistent
  if (stdDev <= 5.5) return 'A-';  // Most consistent
  if (stdDev <= 6.25) return 'B+';  // Most consistent
  if (stdDev <= 7) return 'B';  // Most consistent
  if (stdDev <= 7.75) return 'B-';  // Most consistent
  if (stdDev <= 8.50) return 'C+';  // Most consistent
  if (stdDev <= 9.25) return 'C';  
  if (stdDev <= 10) return 'C-';  
  if (stdDev <= 12) return 'D';  
  return 'F'; // Least consistent
};

const analyzePlayer = (Player: Player) => {
  if (Player.Pos === 'QB' || Player.Pos === 'TE') {
    if (Player.Rankbypos === 1) {
      return 'A+';
    } else if (Player.Rankbypos >= 2 && Player.Rankbypos <= 4) {
      return 'A';
    } else if (Player.Rankbypos > 4 && Player.Rankbypos <= 7) {
      return 'A-';
    } else if (Player.Rankbypos > 7 && Player.Rankbypos <= 10) {
      return 'A-';
    }else if (Player.Rankbypos > 10 && Player.Rankbypos <= 13) {
      return 'B+';
    }else if (Player.Rankbypos > 13 && Player.Rankbypos <= 16) {
      return 'B';
    } else if (Player.Rankbypos > 16 && Player.Rankbypos <= 19) {
      return 'B-';
    } 
    else if (Player.Rankbypos > 19 && Player.Rankbypos <= 22) {
      return 'C+';
    } 
    else if (Player.Rankbypos > 22 && Player.Rankbypos <= 24) {
      return 'C';
    } 
    else if (Player.Rankbypos > 24 && Player.Rankbypos <= 26) {
      return 'C-';
    } 
    else if (Player.Rankbypos > 26 && Player.Rankbypos <= 28) {
      return 'D';
    } else {
      return 'F';
    }
  } else if (Player.Pos === 'WR' || Player.Pos === 'RB') {
    if (Player.Rankbypos === 1) {
      return 'A+';
    } else if (Player.Rankbypos > 2 && Player.Rankbypos <= 6) {
      return 'A';
    } else if (Player.Rankbypos > 6 && Player.Rankbypos <= 10) {
      return 'A-';
    } else if (Player.Rankbypos > 10 && Player.Rankbypos <= 15) {
      return 'B+';
    } else if (Player.Rankbypos > 15 && Player.Rankbypos <= 20) {
      return 'B';
    } 
    else if (Player.Rankbypos > 20 && Player.Rankbypos <= 25) {
      return 'B-';
    } else if (Player.Rankbypos > 25 && Player.Rankbypos <= 30) {
      return 'C+';
    } else if (Player.Rankbypos > 30 && Player.Rankbypos <= 35) {
      return 'C';
    } else if (Player.Rankbypos > 35 && Player.Rankbypos <= 40) {
      return 'C-';
    } else if (Player.Rankbypos > 40 && Player.Rankbypos <= 50) {
      return 'D';
    }else {
      return 'F';
    }
  }
  return 'N/A';
};

const calculateConsistency = (Player: Player): [string, number | null] => {
  const weeklyPoints = [
    Player.WK1Pts,
    Player.WK2Pts,
    Player.WK3Pts,
    Player.WK4Pts,
    Player.WK5Pts,
    Player.WK6Pts,
  ];

  const totalPoints = weeklyPoints.reduce((acc, points) => acc + points, 0);
  
  // Calculate standard deviation for consistency
  const mean = totalPoints / weeklyPoints.length;
  const variance =
    weeklyPoints.reduce((acc, points) => acc + Math.pow(points - mean, 2), 0) /
    weeklyPoints.length;

  const stdDev = Math.sqrt(variance);
  return [totalPoints.toString(), stdDev]; // Return stdDev as number
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
        
        const filteredPlayers = data.filter((Player: Player) => {
          const totalPoints = Player.WK1Pts + Player.WK2Pts + Player.WK3Pts + Player.WK4Pts + Player.WK5Pts + Player.WK6Pts;
          return totalPoints >= 50;
        });
  
        // Sort filtered players
        filteredPlayers.sort((a: Player, b: Player) => {
          if (a.Pos < b.Pos) return -1;
          if (a.Pos > b.Pos) return 1;
          if (a.Player < b.Player) return -1;
          if (a.Player > b.Player) return 1;
          return a.Rankbypos - b.Rankbypos;
        });

        setPlayers(filteredPlayers); // Update state with fetched Players
        console.log(filteredPlayers); // Log the fetched data for debugging
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
        <th>Overall Grade</th> {/* New column for Rankbypos */}
        <th>Total Points</th>
        <th>Consistency Rating</th> {/* New column for Rankbypos */}
      </tr>
    </thead>
    <tbody>
            {Players.map((Player, index) => {
              const [totalPoints, stdDev] = calculateConsistency(Player); // Destructure the returned values
              const grade = getConsistencyGrade(stdDev); // Get the consistency grade
              const week6Performance = calculateWeek6Performance(Player); // Calculate Week 6 performance

              return (
                <tr key={index}>
                  <td className={styles.td}>{Player.Player}</td>
                  <td className={styles.td}>{Player.Pos}</td>
                  <td className={styles.td}>{analyzePlayer(Player)}</td>
                  <td className={styles.td}>{totalPoints}</td>
                  <td className={styles.td}>{grade}</td>
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

