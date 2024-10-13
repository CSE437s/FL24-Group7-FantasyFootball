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

/*
Notes for trade builder:
Thinking maybe offer three insights per waiver wire player
--> (1): boom/bust --> will the trade make your team more consistent, or volatile?
--> (2): future defenses --> how are players future matchups after trading for them?
--> (3): depth analysis --> will the trade help/harm overall team depth

Boom/Bust Analysis:

Add a boom/bust score for both outgoing and incoming players. Calculate this using standard deviation of fantasy points over recent games.
Provide an overall volatility score for the trade, showing whether the trade increases or decreases the likelihood of consistent performance.
Future Matchup Analysis:

Fetch the upcoming opponents for the players involved in the trade and provide a projected difficulty rating. You can compare how the players are expected to perform based on their opponent's defensive rankings (e.g., how many fantasy points the defense typically allows to certain positions).
Display a list of the next 3-5 matchups and highlight favorable or unfavorable matchups in green/red.
Depth Analysis:

Analyze the depth of the user’s team both before and after the trade. Check if the trade leaves the user too stacked in one position but thin in others.
Offer recommendations based on roster needs (e.g., "Your team is deep in WRs but lacks RB depth. This trade improves RB depth but weakens WR depth.").
Additionally, to enhance the Trade Score:

Incorporate player rankings and projections into the score. A higher-ranked player or a player with better future matchups should increase the trade score.
Factor in positional needs. Trades that better balance the user’s roster should result in a higher score.



*/
