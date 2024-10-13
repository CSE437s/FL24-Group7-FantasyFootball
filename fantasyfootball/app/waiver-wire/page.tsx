import { NextPage } from "next";
import Link from "next/link";
import styles from '../../styles/waiverWire.module.css';

interface Player {
  position: string;
  name: string;
  team: string;
  analysis: string;
}

const players: Player[] = [
  { position: "RB", name: "Jonathan Taylor", team: "IND", analysis: "High potential for breakout games." },
  { position: "WR", name: "A.J. Brown", team: "PHI", analysis: "Consistent performer, strong target share." },
  { position: "QB", name: "Jalen Hurts", team: "PHI", analysis: "Dual-threat quarterback with high fantasy upside." },
  { position: "TE", name: "Darren Waller", team: "NYG", analysis: "Great option in red zone." },
  { position: "RB", name: "James Conner", team: "ARI", analysis: "Heavy workload expected, risk of injury." },
  { position: "WR", name: "Tee Higgins", team: "CIN", analysis: "Strong WR2 option with big-play ability." },
  { position: "QB", name: "Kirk Cousins", team: "ATL", analysis: "Solid starter, good matchup upcoming." },
];

const WaiverWirePage: NextPage = () => {
  return (
    <div className={styles.App}>
      <h1 className={styles.title}>Waiver Wire Suggestions Page</h1>
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

