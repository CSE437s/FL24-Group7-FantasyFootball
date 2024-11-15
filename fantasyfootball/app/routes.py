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

    query.save_access_token_data_to_env_file(
        env_file_location=Path(""), save_json_to_var_only=True
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
        
        for team in league_teams:
            team_info = query.get_team_info(team.team_id)._extracted_data
            team_roster = team_info["roster"]
            for player in team_roster.players:
                key = player.player_key
                player_stats = query.get_player_stats_by_week(key,chosen_week=10)
                season_totals = query.get_player_stats_for_season(key)
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

                    })

                player_team_data[-1]["season_totals"] = season_totals.player_points.total
    

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



def analyze_player(player_data):
    """
    Analyze player data and return a grade based on total points and position.

    Args:
        player_data (dict): A dictionary containing player information.

    Returns:
        str: A grade representing the player's performance.
    """
    total_points = player_data.get("season_totals", 0)
    position = player_data.get("Pos", "").upper()

    # Define grading thresholds based on position
    if position == "QB":
        if total_points >= 260:
            return "A+"
        elif total_points >= 240:
            return "A"
        elif total_points >= 220:
            return "A-"
        elif total_points >= 200:
            return "B+"
        elif total_points >= 180:
            return "B"
        elif total_points >= 160:
            return "B-"
        elif total_points >= 140:
            return "C+"
        elif total_points >= 120:
            return "C"
        elif total_points >= 100:
            return "C-"
        elif total_points >= 80:
            return "D+"
        elif total_points >= 60:
            return "D"
        elif total_points >= 40:
            return "D-"
        else:
            return "F"
    elif position in ["RB", "WR"]:
        if total_points >= 210:
            return "A+"
        elif total_points >= 190:
            return "A"
        elif total_points >= 170:
            return "A-"
        elif total_points >= 150:
            return "B+"
        elif total_points >= 130:
            return "B"
        elif total_points >= 110:
            return "B-"
        elif total_points >= 90:
            return "C+"
        elif total_points >= 70:
            return "C"
        elif total_points >= 50:
            return "C-"
        elif total_points >= 40:
            return "D+"
        elif total_points >= 30:
            return "D"
        elif total_points >= 20:
            return "D-"
        else:
            return "F"
    elif position == "TE":
        if total_points >= 118:
            return "A+"
        elif total_points >= 100:
            return "A"
        elif total_points >= 90:
            return "A-"
        elif total_points >= 80:
            return "B+"
        elif total_points >= 70:
            return "B"
        elif total_points >= 60:
            return "B-"
        elif total_points >= 50:
            return "C+"
        elif total_points >= 40:
            return "C"
        elif total_points >= 30:
            return "C-"
        elif total_points >= 20:
            return "D+"
        elif total_points >= 10:
            return "D"
        elif total_points >= 5:
            return "D-"
        else:
            return "F"
    elif position == "K":
        if total_points >= 117:
            return "A+"
        elif total_points >= 100:
            return "A"
        elif total_points >= 90:
            return "A-"
        elif total_points >= 80:
            return "B+"
        elif total_points >= 70:
            return "B"
        elif total_points >= 60:
            return "B-"
        elif total_points >= 50:
            return "C+"
        elif total_points >= 40:
            return "C"
        elif total_points >= 30:
            return "C-"
        elif total_points >= 20:
            return "D+"
        elif total_points >= 10:
            return "D"
        elif total_points >= 5:
            return "D-"
        else:
            return "F"
    elif position == "DEF":
        if total_points >= 108:
            return "A+"
        elif total_points >= 90:
            return "A"
        elif total_points >= 80:
            return "A-"
        elif total_points >= 70:
            return "B+"
        elif total_points >= 60:
            return "B"
        elif total_points >= 50:
            return "B-"
        elif total_points >= 40:
            return "C+"
        elif total_points >= 30:
            return "C"
        elif total_points >= 20:
            return "C-"
        elif total_points >= 15:
            return "D+"
        elif total_points >= 10:
            return "D"
        elif total_points >= 5:
            return "D-"
        else:
            return "F"
    else:
        return "F"



def topQB(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_qb = None
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "QB":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if player.get("season_totals", 0) > max_points:
                max_points = player.get("season_totals", 0)
                optimal_qb = player.get("Player", "")

    return optimal_qb
    


def topRBs(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_rbs = []
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "RB":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if len(optimal_rbs) < 2 or player.get("season_totals", 0) > max_points:
                if len(optimal_rbs) == 2:
                    optimal_rbs.pop(0)
                optimal_rbs.append(player.get("Player", ""))
                max_points = player.get("season_totals", 0)

    return tuple(optimal_rbs)

def topWRs(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_wrs = []
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "WR":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if len(optimal_wrs) < 2 or player.get("season_totals", 0) > max_points:
                if len(optimal_wrs) == 2:
                    optimal_wrs.pop(0)
                optimal_wrs.append(player.get("Player", ""))
                max_points = player.get("season_totals", 0)

    return tuple(optimal_wrs)

def topTE(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_te = None
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "TE":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if player.get("season_totals", 0) > max_points:
                max_points = player.get("season_totals", 0)
                optimal_te = player.get("Player", "")

    return optimal_te

def topFLEX(players, rbs, wrs, te):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_flex = None
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() not in ["RB", "WR", "TE"]:
            continue
        if player.get("Player", "") in rbs + wrs + (te,):
            continue
        if player.get("bye", 0) == current_week:
            continue
        if player.get("status", "") in ["IR", "D", "O"]:
            continue
        if player.get("season_totals", 0) > max_points:
            max_points = player.get("season_totals", 0)
            optimal_flex = player.get("Player", "")

    return optimal_flex

def topK(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_k = None
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "K":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if player.get("season_totals", 0) > max_points:
                max_points = player.get("season_totals", 0)
                optimal_k = player.get("Player", "")

    return optimal_k

def topDst(players):
    current_week = 1 + players[0].get("previous_week", 0) if players else 0
    optimal_dst = None
    max_points = -1

    for player in players:
        if player.get("Pos", "").upper() == "DEF":
            if player.get("bye", 0) == current_week:
                continue
            if player.get("status", "") in ["IR", "D", "O"]:
                continue
            if player.get("season_totals", 0) > max_points:
                max_points = player.get("season_totals", 0)
                optimal_dst = player.get("Player", "")

    return optimal_dst

def grade_to_numeric(grade):
    """Convert a grade to a numeric value for averaging."""
    grade_mapping = {
        "A+": 4.3, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0
    }
    return grade_mapping.get(grade, 0.0)

def numeric_to_grade(numeric):
    """Convert a numeric value back to a grade."""
    if numeric >= 4.3:
        return "A+"
    elif numeric >= 4.0:
        return "A"
    elif numeric >= 3.7:
        return "A-"
    elif numeric >= 3.3:
        return "B+"
    elif numeric >= 3.0:
        return "B"
    elif numeric >= 2.7:
        return "B-"
    elif numeric >= 2.3:
        return "C+"
    elif numeric >= 2.0:
        return "C"
    elif numeric >= 1.7:
        return "C-"
    elif numeric >= 1.3:
        return "D+"
    elif numeric >= 1.0:
        return "D"
    elif numeric >= 0.7:
        return "D-"
    else:
        return "F"

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
        ideal_lineup = {}
        position_grades = {}
        strengths = None
        strengths_grade = None
        weaknesses = None
        weaknesses_grade = None

        if request.method == 'POST':
            selected_team = request.form.get('team')
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" FROM "player_data" WHERE "team_name" = %s', (selected_team,))
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
                    'total_points': player[8],
                    'team_abb': player[9],
                    'season_totals': player[10]
                }
                player_data['grade'] = analyze_player(player_data)
                players.append(player_data)

                # Collect grades for each position
                pos = player_data['Pos']
                if pos not in position_grades:
                    position_grades[pos] = []
                position_grades[pos].append(grade_to_numeric(player_data['grade']))

            # Calculate top players for each position
            qb = topQB(players)
            rbs = topRBs(players)
            wrs = topWRs(players)
            te = topTE(players)
            flex = topFLEX(players, rbs, wrs, te)
            k = topK(players)
            dst = topDst(players)

            ideal_lineup = {
                "QB": qb,
                "RB1": rbs[0] if len(rbs) > 0 else None,
                "RB2": rbs[1] if len(rbs) > 1 else None,
                "WR1": wrs[0] if len(wrs) > 0 else None,
                "WR2": wrs[1] if len(wrs) > 1 else None,
                "TE": te,
                "FLEX": flex,
                "K": k,
                "DST": dst
            }

            min_depth = {
                "QB": 1,
                "RB": 2,
                "WR": 2,
                "TE": 1,
                "FLEX": 1
            }

            # Calculate average grades for each position
            filtered_position_grades = {pos: grades for pos, grades in position_grades.items() if pos not in ["K", "DEF"] and len(grades) >= min_depth.get(pos, 0)}
            if filtered_position_grades:
                avg_grades = {pos: (sum(grades) / len(grades)) + (0.2 * (len(grades) - min_depth.get(pos, 0))) for pos, grades in filtered_position_grades.items()}
                strengths = max(avg_grades, key=avg_grades.get)
                weaknesses = min(avg_grades, key=avg_grades.get)

                strengths_grade = numeric_to_grade(avg_grades[strengths])
                weaknesses_grade = numeric_to_grade(avg_grades[weaknesses])
            else:
                strengths = "N/A"
                strengths_grade = "N/A"
                weaknesses = "N/A"
                weaknesses_grade = "N/A"


        return render_template('team_analyzer.html', teams=teams, selected_team=selected_team, players=players, ideal_lineup=ideal_lineup, strengths=strengths, strengths_grade=strengths_grade, weaknesses=weaknesses, weaknesses_grade=weaknesses_grade)
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
