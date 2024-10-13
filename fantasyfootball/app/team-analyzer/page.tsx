import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/teamAnalyzer.module.css';

interface Player {
  position: string;
  name: string;
  team: string;
  analysis: string;
}

const players: Player[] = [
  { position: "QB", name: "Kirk Cousins", team: "ATL", analysis: "Solid starter, good matchup upcoming." },
  { position: "QB", name: "Jalen Hurts", team: "PHI", analysis: "Dual-threat quarterback with high fantasy upside." },
  { position: "RB", name: "Jonathan Taylor", team: "IND", analysis: "High potential for breakout games." },
  { position: "RB", name: "James Conner", team: "ARI", analysis: "Heavy workload expected, risk of injury." },
  { position: "WR", name: "A.J. Brown", team: "PHI", analysis: "Consistent performer, strong target share." },
  { position: "WR", name: "Tee Higgins", team: "CIN", analysis: "Strong WR2 option with big-play ability." },
  { position: "TE", name: "Darren Waller", team: "NYG", analysis: "Great option in red zone." }
];

const TeamAnalyzerPage: NextPage = () => {
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
              <th>Position</th>
              <th>Name</th>
              <th>Team</th>
              <th>Analysis</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => (
              <tr key={index}>
                <td>{player.position}</td>
                <td>{player.name}</td>
                <td>{player.team}</td>
                <td>{player.analysis}</td>
              </tr>
            ))}
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

