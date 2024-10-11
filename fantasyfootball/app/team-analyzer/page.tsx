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

const WaiverWirePage: NextPage = () => {
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

export default WaiverWirePage;

