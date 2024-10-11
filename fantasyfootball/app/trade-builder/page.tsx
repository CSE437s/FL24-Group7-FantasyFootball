"use client";
import { NextPage } from "next";
import Link from "next/link";
import { useState } from "react";
import styles from '../../styles/tradeBuilder.module.css';

interface Player {
  position: string;
  name: string;
  team: string;
  analysis: string;
}

const userPlayers: Player[] = [
  { position: "QB", name: "Kirk Cousins", team: "ATL", analysis: "Solid starter, good matchup upcoming." },
  { position: "RB", name: "Jonathan Taylor", team: "IND", analysis: "High potential for breakout games." },
  { position: "WR", name: "A.J. Brown", team: "PHI", analysis: "Consistent performer, strong target share." },
];

const opposingPlayers: Player[] = [
  { position: "QB", name: "Jalen Hurts", team: "PHI", analysis: "Dual-threat quarterback with high fantasy upside." },
  { position: "RB", name: "James Conner", team: "ARI", analysis: "Heavy workload expected, risk of injury." },
  { position: "WR", name: "Tee Higgins", team: "CIN", analysis: "Strong WR2 option with big-play ability." },
  { position: "TE", name: "Darren Waller", team: "NYG", analysis: "Great option in red zone." }
];

const TradeBuilderPage: NextPage = () => {
  const [userSelections, setUserSelections] = useState<string[]>([]);
  const [opposingSelections, setOpposingSelections] = useState<string[]>([]);

  const toggleUserSelection = (name: string) => {
    setUserSelections(prev => 
      prev.includes(name) ? prev.filter(player => player !== name) : [...prev, name]
    );
  };

  const toggleOpposingSelection = (name: string) => {
    setOpposingSelections(prev => 
      prev.includes(name) ? prev.filter(player => player !== name) : [...prev, name]
    );
  };

  const calculateTradeScore = () => {
    // A basic example of how you could calculate a score based on selected players
    return (userSelections.length + opposingSelections.length) * 10; // Simple scoring for demo
  };

  return (
    <div className={styles.App}>
      <h1 className={styles.title}>Trade Builder</h1>
      <h2 className={styles.leagueteam}>**League Name**: **Team Name**</h2>
      <Link href="/" passHref>
        <button className={styles.homeButton}>Back to Homepage</button>
      </Link>
      <div className={styles.content}>
        <div className={styles.teamContainer}>
          <div className={styles.userTeam}>
            <h3>Your Team</h3>
            <table className={styles.playerTable}>
              <tbody>
                {userPlayers.map(player => (
                  <tr key={player.name}>
                    <td>
                      <input 
                        type="checkbox" 
                        checked={userSelections.includes(player.name)} 
                        onChange={() => toggleUserSelection(player.name)} 
                      />
                      {player.name} ({player.position}, {player.team})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className={styles.opposingTeam}>
            <h3>Opposing Team</h3>
            <table className={styles.playerTable}>
              <tbody>
                {opposingPlayers.map(player => (
                  <tr key={player.name}>
                    <td>
                      <input 
                        type="checkbox" 
                        checked={opposingSelections.includes(player.name)} 
                        onChange={() => toggleOpposingSelection(player.name)} 
                      />
                      {player.name} ({player.position}, {player.team})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className={styles.analysis}>
          <h3>Trade Analysis</h3>
          <p>Trade Score: {calculateTradeScore()}</p>
        </div>
      </div>
    </div>
  );
};

export default TradeBuilderPage;
