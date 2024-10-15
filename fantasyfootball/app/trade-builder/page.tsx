'use client';
import { useState, useEffect } from 'react';
import Link from "next/link";
import styles from '../../styles/tradeBuilder.module.css'; // Adjust path as necessary

interface Player {
  name: string;
  team: string;
  position: string;
}

const TradeBuilder = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [searchTermTeam1, setSearchTermTeam1] = useState<string>("");
  const [searchTermTeam2, setSearchTermTeam2] = useState<string>("");
  const [team1Players, setTeam1Players] = useState<Player[]>([]);
  const [team2Players, setTeam2Players] = useState<Player[]>([]);
  const [filteredPlayersTeam1, setFilteredPlayersTeam1] = useState<Player[]>([]);
  const [filteredPlayersTeam2, setFilteredPlayersTeam2] = useState<Player[]>([]);

  // State to hold displayed player names after search
  const [displayedPlayerNamesTeam1, setDisplayedPlayerNamesTeam1] = useState<string[]>([]);
  const [displayedPlayerNamesTeam2, setDisplayedPlayerNamesTeam2] = useState<string[]>([]);

  // Fetch players when component mounts
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await fetch('/api/players');
        const data = await response.json();
        setPlayers(data);
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    };

    fetchPlayers();
  }, []);

  // Handle adding a player to Team 1
  const addPlayerToTeam1 = (player: Player) => {
    if (!team1Players.find(p => p.name === player.name)) {
      setTeam1Players(prev => [...prev, player]);
    }
  };

  // Handle adding a player to Team 2
  const addPlayerToTeam2 = (player: Player) => {
    if (!team2Players.find(p => p.name === player.name)) {
      setTeam2Players(prev => [...prev, player]);
    }
  };

  // Search for players in Team 1
  const searchPlayersTeam1 = () => {
    if (!searchTermTeam1) {
      setFilteredPlayersTeam1([]); // Clear if search term is empty
      return;
    }

    const filtered = players.filter(player =>
      player?.name?.toLowerCase().includes(searchTermTeam1.toLowerCase())
    );

    setFilteredPlayersTeam1(filtered);

    // Add displayed name based on the search result
    if (filtered.length > 0) {
      setDisplayedPlayerNamesTeam1(prev => [...prev, filtered[0].name]); // Show the first match
    } else {
      setDisplayedPlayerNamesTeam1(prev => [...prev, searchTermTeam1]); // Show search term if no match
    }

    // Clear the search term after search
    setSearchTermTeam1("");
  };

  // Search for players in Team 2
  const searchPlayersTeam2 = () => {
    if (!searchTermTeam2) {
      setFilteredPlayersTeam2([]); // Clear if search term is empty
      return;
    }

    const filtered = players.filter(player =>
      player?.name?.toLowerCase().includes(searchTermTeam2.toLowerCase())
    );

    setFilteredPlayersTeam2(filtered);

    // Add displayed name based on the search result
    if (filtered.length > 0) {
      setDisplayedPlayerNamesTeam2(prev => [...prev, filtered[0].name]); // Show the first match
    } else {
      setDisplayedPlayerNamesTeam2(prev => [...prev, searchTermTeam2]); // Show search term if no match
    }

    // Clear the search term after search
    setSearchTermTeam2("");
  };

  // Remove a player name from Team 1's displayed list
  const removePlayerFromTeam1 = (name: string) => {
    setDisplayedPlayerNamesTeam1(prev => prev.filter(playerName => playerName !== name));
  };

  // Remove a player name from Team 2's displayed list
  const removePlayerFromTeam2 = (name: string) => {
    setDisplayedPlayerNamesTeam2(prev => prev.filter(playerName => playerName !== name));
  };

  return (
    <div className={styles.App}>
      <div className={styles.title}>Trade Builder</div>
      <Link href="/" passHref>
        <button className={styles.homeButton}>Back to Homepage</button>
      </Link>
      <div className={styles.teamContainer}>
        <div className={styles.userTeam}>
          <h2>Team 1</h2>
          <input
            type="text"
            value={searchTermTeam1}
            onChange={(e) => setSearchTermTeam1(e.target.value)}
            placeholder="Search for a player"
            className={styles.searchInput}
          />
          <button onClick={searchPlayersTeam1} className={styles.searchButton}>
            Search
          </button>
          <ul className={styles.playerList}>
            {filteredPlayersTeam1.map((player, index) => (
              <li key={index} onClick={() => addPlayerToTeam1(player)} className={styles.playerItem}>
                {player.name} - {player.team} - {player.position}
              </li>
            ))}
          </ul>
          <h3>Selected Players:</h3>
          <ul className={styles.selectedPlayers}>
            {team1Players.map((player, index) => (
              <li key={index} className={styles.selectedPlayer}>{player.name}</li>
            ))}
          </ul>
          {/* Print the player's names below the team after search is clicked */}
          {displayedPlayerNamesTeam1.length > 0 && (
            <div className={styles.displayedPlayerList}>
              {displayedPlayerNamesTeam1.map((name, index) => (
                <div key={index} className={styles.displayedPlayer}>
                  {name}
                  <button onClick={() => removePlayerFromTeam1(name)} className={styles.removeButton}>
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={styles.opposingTeam}>
          <h2>Team 2</h2>
          <input
            type="text"
            value={searchTermTeam2}
            onChange={(e) => setSearchTermTeam2(e.target.value)}
            placeholder="Search for a player"
            className={styles.searchInput}
          />
          <button onClick={searchPlayersTeam2} className={styles.searchButton}>
            Search
          </button>
          <ul className={styles.playerList}>
            {filteredPlayersTeam2.map((player, index) => (
              <li key={index} onClick={() => addPlayerToTeam2(player)} className={styles.playerItem}>
                {player.name} - {player.team} - {player.position}
              </li>
            ))}
          </ul>
          <h3>Selected Players:</h3>
          <ul className={styles.selectedPlayers}>
            {team2Players.map((player, index) => (
              <li key={index} className={styles.selectedPlayer}>{player.name}</li>
            ))}
          </ul>
          {/* Print the player's names below the team after search is clicked */}
          {displayedPlayerNamesTeam2.length > 0 && (
            <div className={styles.displayedPlayerList}>
              {displayedPlayerNamesTeam2.map((name, index) => (
                <div key={index} className={styles.displayedPlayer}>
                  {name}
                  <button onClick={() => removePlayerFromTeam2(name)} className={styles.removeButton}>
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TradeBuilder;










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
