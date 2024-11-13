from flask import Blueprint, jsonify, request, redirect, url_for
import os
from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
from flask import render_template
import json
import pandas as pd
import psycopg2
from psycopg2 import pool
from app.db import get_connection, release_connection, upsert_player_data
import numpy as np
from dotenv import load_dotenv

load_dotenv(override=True)


# Define a Blueprint for the API routes
api = Blueprint("api", __name__)
main = Blueprint("main", __name__)

def extract_serializable_data(obj):
    # If the object has '_extracted_data', use it
    if hasattr(obj, "_extracted_data"):
        obj = obj._extracted_data

    # If it's a dictionary, recursively process its values
    if isinstance(obj, dict):
        return {key: extract_serializable_data(value) for key, value in obj.items()}

    # If it's a list or tuple, recursively process its elements
    elif isinstance(obj, (list, tuple)):
        return [extract_serializable_data(item) for item in obj]

    # If it's a serializable primitive (str, int, float, bool, None), return it directly
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # If it's another object type, check for '_extracted_data' or convert to string as fallback
    else:
        return str(obj)  # Convert to string as a last resort

@api.route("/auth", methods=["GET"])
def auth():

    redirect_uri = os.getenv("REDIRECT_URI")
    client_id = os.getenv("YAHOO_CLIENT_ID")
    client_secret = os.getenv("YAHOO_CLIENT_SECRET")
    response_type = "code"
    print('hellothere')
    return redirect(
        f"https://api.login.yahoo.com/oauth2/request_auth?client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&response_type={response_type}"
    )

@api.route("/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    query = YahooFantasySportsQuery(
        league_id="<YAHOO_LEAGUE_ID>",
        game_code="nfl",
        game_id=449,
        yahoo_consumer_key=os.getenv("YAHOO_CLIENT_ID"),
        yahoo_consumer_secret=os.getenv("YAHOO_CLIENT_SECRET"),
        env_file_location=Path(""),
    )

    

    return redirect(url_for("main.home"))


@main.route("/home", methods=["GET", "POST"])
def home():
    query = YahooFantasySportsQuery(
        league_id="<YAHOO_LEAGUE_ID>",
        game_code="nfl",
        game_id=449,
        yahoo_consumer_key=os.getenv("YAHOO_CLIENT_ID"),
        yahoo_consumer_secret=os.getenv("YAHOO_CLIENT_SECRET"),
        env_file_location=Path(""),
    )
    # curr_user_team = query.get_current_user()._extracted_data["guid"]
    leagues = query.get_user_leagues_by_game_key(449)

    for league in leagues:
        if isinstance(league.name, bytes):
            league.name = league.name.decode("utf-8")


    if request.method == "POST":
        selected_league_id = request.form.get("league_id")
        query = YahooFantasySportsQuery(
            league_id=selected_league_id,
            game_code="nfl",
            game_id=449,
            yahoo_consumer_key=os.getenv("YAHOO_CLIENT_ID"),
            yahoo_consumer_secret=os.getenv("YAHOO_CLIENT_SECRET"),
            env_file_location=Path(""),
        )

        player_team_data = []
        league_teams = query.get_league_teams()
        player_names = set()
        for team in league_teams:
            team_info = query.get_team_info(team.team_id)._extracted_data
            team_roster = team_info["roster"]
            for player in team_roster.players:
                key = player.player_key
                player_stats = query.get_player_stats_by_week(key,chosen_week=9)
                # hard coded week for now
                player_team_data.append(
                    {
                        "player_name": player.name.full,
                        "team_name": team_info["name"],
                        "primary_position": player.primary_position,
                        "bye": player.bye,
                        "team_abb": player.editorial_team_abbr,
                        "image": player.image_url,
                        "status": player.status,
                        "injury": player.injury_note,
                        "player_key": player.player_key,
                        "previous_week": player_stats.player_points.week,
                        "previous_performance": player_stats.player_points.total,
                        "games_played": player_stats.player_stats.stats[0].value,
                        "total_points": player_stats.player_points.total,
                        "ppg": (player_stats.player_points.total / player_stats.player_stats.stats[0].value
                                if player_stats.player_stats.stats[0].value != 0 else 0)

                    }
                )

        # all_players = query.get_league_players()
        # waiver_data = []
        # for player in all_players:
        #     waiver_data.append({
        #                 "player_name": player.name.full,
        #                 "primary_position": player.primary_position,
        #                 "bye": player.bye,
        #                 "team_abb": player.editorial_team_abbr,
        #                 "image": player.image_url,
        #                 "status": player.status,
        #                 "injury": player.injury_note,
        #                 "player_key": player.player_key,
        #     })


                # player_names.add(player.name.full)

        # for player in all_players:
        #     if player.name.full not in player_names:
        #         player_team_data.append(
        #             {
        #             "player_name": player.name.full,
        #             "team_name": "N/A",
        #             "primary_position": player.primary_position,
        #             "bye": player.bye,
        #             "team_abb": player.editorial_team_abbr,
        #             "image": player.image_url,
        #             "status": player.status,
        #             "injury": player.injury_note,
        #             "player_key": player.player_key,
        #             "previous_week": "N/A",
        #             "previous_performance": "N/A",
        #             "games_played": "N/A",
        #             "total_points": "N/A",
        #             "ppg": "N/A"

        #         }
        #     )



        # Mahomes
        # stat ID 4 - passing yds
        # stat ID 5 - passing TDs
        # stat ID 6 - passing INTs
        # stat ID 8 - RUSH ATTs
        # stat ID 9 - rush YDS
        # stat ID 10 - rush TDs
        # stat ID 11 - receptions
        # stat ID 12 - receiving yards
        # stat ID 13 - receiving TDs
        # stat ID 15 - return TDs
        # stat ID 16 - 2pt
        # stat ID 18 - fumble lost
        # stat ID 78 - targets


#         ALTER TABLE player_data
# ADD COLUMN games_played INT DEFAULT NULL,
# ADD COLUMN total_points DECIMAL(5, 2) DEFAULT NULL,
# ADD COLUMN ppg DECIMAL(5, 2) DEFAULT NULL;



        # print(players)


        # for player in players:
        #     owner_hopefully = player.ownership._extracted_data
        #     player_info = {
        #         "player_name": player.name.full,
        #         "primary_position": player.primary_position,
        #         "bye": player.bye,
        #         "team_abb": player.editorial_team_abbr,
        #         "image": player.image_url,
        #         "status": player.status,
        #         "injury": player.injury_note,
        #     }

        #     stat_list = player.player_stats.stats
        #     if stat_list:
        #         for stat in stat_list:

        #             stat = stat._extracted_data

        #             stat_name = stat.name
        #             stat_value = stat.value

        #             if stat_name and stat_value is not None:

        #                 player_info[stat_name] = stat_value
        #             else:
        #                 print(f"Stat data missing for player: {player.name.full}, stat: {stat_name}")


            # player_team_data.append(player_info)

        # # Create the DataFrame
        # df = pd.DataFrame(player_team_data)
        # # df2 = pd.DataFrame(waiver_data)

        # if not os.path.exists("data"):
        #     os.makedirs("data")

        # Save the DataFrame to CSV
        # df.to_csv("data/player_team_data.csv", index=False)
        # df2.to_csv("data/waiver_data.csv", index=False)
    

        upsert_player_data(player_team_data)

        # Pass team name and players to the template
        return render_template(
            "home.html",
            leagues=leagues,
            player_and_teams_loaded=True,
        )

    return render_template(
        "home.html",
        leagues=leagues,
    )


@main.route("/waiver-wire")
def waiver_wire():
    try:
        # Get the current page number and position filter from query parameters
        page = request.args.get('page', 1, type=int)
        position_filter = request.args.get('positionFilter', '', type=str)
        per_page = 25  # Number of players per page

        # Get connection from the pool
        connection = get_connection()
        cursor = connection.cursor()

        # Modify SQL query based on position filter
        if position_filter:
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "ppg", "total_points","team_abb" '
                'FROM "player_data" '
                'WHERE "primary_position" = %s '
                'LIMIT %s OFFSET %s',
                (position_filter, per_page, (page - 1) * per_page)
            )
        else:
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "ppg", "total_points","team_abb" '
                'FROM player_data '
                'LIMIT %s OFFSET %s',
                (per_page, (page - 1) * per_page)
            )

        rows = cursor.fetchall()

        # Convert rows to dictionary format
        waiver_wire_players = [
            {
                "player_name": row[0],
                "primary_position": row[1],
                "bye": row[2],
                "team_abb": row[3],
                "image_url": row[4],
                "status": row[5],
                "injury": row[6],
                "player_key": row[7]
            }
            for row in rows
        ]

        # Calculate pagination
        total = len(waiver_wire_players)
        total_pages = (total + per_page - 1) // per_page  # Calculate total pages

        # Close cursor and release connection
        cursor.close()
        release_connection(connection)

        # Render the waiver_wire template with paginated player data and filter info
        return render_template(
            "waiver_wire.html",
            waiver_wire_players=waiver_wire_players,
            page=page,
            total_pages=total_pages,
            position_filter=position_filter
        )

    except Exception as error:
        print("Error fetching waiver wire data:", error)
        return "Error loading waiver wire", 500



def analyze_player(player):
    if player["Pos"] in ["QB", "TE"]:
        if player["ppg"] >= 20:
            return "A+: best at Position!"
        elif 15 <= player["ppg"] < 20:
            return "A"
        elif 10 <= player["ppg"] < 15:
            return "B"
        elif 5 <= player["ppg"] < 10:
            return "C"
        elif 2 <= player["ppg"] < 5:
            return "D"
        else:
            return "F"
    elif player["Pos"] in ["WR", "RB"]:
        if player["ppg"] >= 20:
            return "A+"
        elif 15 <= player["ppg"] < 20:
            return "A"
        elif 10 <= player["ppg"] < 15:
            return "B"
        elif 5 <= player["ppg"] < 10:
            return "C"
        elif 2 <= player["ppg"] < 5:
            return "D"
        else:
            return "F"
    return "N/A"



def calculate_consistency(player):
    weekly_points = [
        player["WK1Pts"],
        player["WK2Pts"],
        player["WK3Pts"],
        player["WK4Pts"],
        player["WK5Pts"],
        player["WK6Pts"],
    ]

    total_points = sum(weekly_points)

    # If total points are less than 40, return None for both total and std_dev
    # if total_points < 40:
    # return None, None

    # Calculate standard deviation for consistency
    mean = total_points / len(weekly_points)
    variance = np.var(weekly_points)
    std_dev = np.sqrt(variance)

    grade = ""

    if std_dev <= 6:
        grade = "A"
    elif std_dev <= 8:
        grade = "B"
    elif std_dev <= 10:
        grade = "C"
    elif std_dev <= 12:
        grade = "D"
    else:
        grade = "F"

    return total_points, grade


def topQB(player_data):
    return "Drake Maye"

def topRBs(player_data):
    return "Derrick Henry","Saquon Barkley"

def topWRs(player_data):
    return "Justin Jefferson", "AJ Brown"

def topTE(player_data):
    return "Brock Bowers"

def topFLEX(player_data, rbs, wrs, tes):
    return "Demario Douglas"

def topK(player_data):
    return "Brandon Aubrey"

def topDst(player_data):
    return "Jets"

@main.route('/team-analyzer', methods=['GET', 'POST'])
def team_analyzer():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT "team_name" FROM "player_data"')
        all_teams = cursor.fetchall()
        cursor.close()
        release_connection(connection)

        teams = [team[0] for team in all_teams if team[0] is not None]
        selected_team = None
        players = []

        if request.method == 'POST':
            selected_team = request.form.get('team')
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "ppg", "total_points","team_abb" FROM "player_data" WHERE "team_name" = %s', (selected_team,))
            team_players = cursor.fetchall()
            cursor.close()
            release_connection(connection)

            for player in team_players:
                player_data = {
                    'Player': player[0],
                    'Pos': player[1],
                    'img': player[2],
                    'previous_performance': player[3],
                    'bye': player[4],
                    'status': player[5],
                    'injury': player[6],
                    'previous_week': player[7],
                    'ppg': player[8],
                    'total_points': player[9],
                    'team_abb': player[10]
                }
                player_data['grade'] = analyze_player(player_data)
                total_points, std_dev = None,None
                # calculate_consistency(player_data)
                qb = topQB(player_data)
                rbs = topRBs(player_data)
                wrs = topWRs(player_data)
                te = topTE(player_data)
                flex = topFLEX(player_data, rbs, wrs, te)
                k = topK(player_data)
                dst = topDst(player_data)

                player_data['total_points'] = total_points if total_points is not None else "N/A"
                player_data['std_dev'] = std_dev if std_dev is not None else "N/A"
                players.append(player_data)

        return render_template('team_analyzer.html', teams=teams, selected_team=selected_team, players=players)
    except Exception as e:
        print(f"Error fetching team analyzer data: {e}")
        return render_template('error.html', error_message=str(e))


@main.route("/trade-builder", methods=["GET", "POST"])
def trade_builder():
    connection = get_connection()
    cursor = connection.cursor()

    # Fetch all teams
    cursor.execute('SELECT DISTINCT "team_name" FROM "player_data"')
    all_teams = cursor.fetchall()
    cursor.close()
    release_connection(connection)

    teams = [team[0] for team in all_teams if team[0] is not None]

    team1_roster = []
    team2_roster = []
    team1_roster_info = []
    team2_roster_info = []
    trade_feedback = None

    if request.method == "POST":
        team1 = request.form.get("team1")
        team2 = request.form.get("team2")

        if team1 and team2 and team1 != team2:
            connection = get_connection()
            cursor = connection.cursor()

            # Fetch team 1 roster
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "team_name", "bye", "status", "injury", "player_key", "previous_week", "ppg", "total_points", "team_abb" FROM "player_data" WHERE "team_name" = %s',
                (team1,),
            )
            team1_roster = cursor.fetchall()

            # Fetch team 2 roster
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "team_name", "bye", "status", "injury", "player_key", "previous_week", "ppg", "total_points","team_abb" FROM "player_data" WHERE "team_name" = %s',
                (team2,),
            )
            team2_roster = cursor.fetchall()

            cursor.close()
            release_connection(connection)

            for player in team1_roster:
                team1_info = {
                    'Player': player[0],
                    'Pos': player[1],
                    'img': player[2],
                    'previous_performance': player[3],
                    'team_name': player[4],
                    'bye': player[5],
                    'status': player[6],
                    'injury': player[7],
                    'player_key': player[8],
                    'previous_week': player[9],
                    'ppg': player[10],
                    'total_points': player[11],
                    'team_abb': player[12]
                }
                team1_roster_info.append(team1_info)

            # Process team 2 roster
            for player in team2_roster:
                team2_info = {
                    'Player': player[0],
                    'Pos': player[1],
                    'img': player[2],
                    'previous_performance': player[3],
                    'team_name': player[4],
                    'bye': player[5],
                    'status': player[6],
                    'injury': player[7],
                    'player_key': player[8],
                    'previous_week': player[9],
                    'ppg': player[10],
                    'total_points': player[11],
                    'team_abb': player[12]
                }
                team2_roster_info.append(team2_info)

            # Now set the rosters for rendering
            team1_roster = team1_roster_info
            team2_roster = team2_roster_info

        if request.form.get("your_player") and request.form.get("target_player"):
            your_player = request.form.get("your_player")
            target_player = request.form.get("target_player")
            trade_feedback = f'You proposed trading {your_player} for {target_player}.'



    return render_template(
        "trade_builder.html",
        teams=teams,
        team1_roster=team1_roster,
        team2_roster=team2_roster,
        trade_feedback=trade_feedback,
    )
