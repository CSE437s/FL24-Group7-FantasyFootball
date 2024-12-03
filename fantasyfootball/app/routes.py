# /app/routes.py
from flask import (
    Blueprint,
    jsonify,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import os
import requests
import json
from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
from flask import render_template
import json
import pandas as pd
import psycopg2
from psycopg2 import pool
from app.db import (
    get_connection,
    release_connection,
    save_access_token,
    get_access_token_by_guid,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
    update_user_guid,  # Import the new function
    get_access_token_by_user_id,
    upsert_player_data,
)
import numpy as np
from dotenv import load_dotenv
import webbrowser
import sys
from io import StringIO
from flask import g


load_dotenv(override=True)


# Define a Blueprint for the API routes
api = Blueprint("api", __name__)
main = Blueprint("main", __name__)

# Endpoint for fethcing from `Football News API`
FOOTBALL_NEWS_API_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
)


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


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/terms_of_service")
def terms_of_service():
    return render_template("terms_of_service.html")


@main.route("/about_us")
def about_us():
    return render_template("about_us.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    print("register")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        user = get_user_by_email(email)
        if user:
            # If the email exists, check if the password matches
            if verify_password(user["password"], password):
                # If the password matches, treat it as a login
                session["user_id"] = user["id"]
                return redirect(url_for("main.home"))
            else:
                return (
                    jsonify({"error": "User already exists with a different password"}),
                    400,
                )

        create_user(email, password)
        user = get_user_by_email(email)  # Retrieve the newly created user
        session["user_id"] = user["id"]
        print(email)
        print(password)
        return redirect(url_for("api.oauth"))
    return render_template("register.html")


from flask import flash


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            flash("Missing email or password", "error")
            return redirect(url_for("main.login"))

        user = get_user_by_email(email)
        if not user or not verify_password(user["password"], password):
            flash("Invalid email or password", "error")
            return redirect(url_for("main.login"))

        session["user_id"] = user["id"]
        return redirect(url_for("main.home"))

    return render_template("login.html")


@main.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        # Clear session and pop all keys from g
        session.clear()
        keys = g.__dict__.keys()

        for key in list(keys):
            g.pop(key)

        # Redirect to Yahoo's logout page
        return render_template("index.html")
    return render_template("confirm_logout.html")


@api.route("/oauth", methods=["GET", "POST"])
def oauth():
    print("oauth")
    try:
        user_id = g.user_id
        print("user_id in oauth:", user_id)
        if not user_id:
            return redirect(url_for("main.login"))
        access_token = g.access_token
        print("access_token:", access_token)
        # TODO I think this needs to be more robust haha, what if access_token is expired or access_token = 42 or something like that
        if access_token is not None:
            print("access_token in if statement that hits:", access_token)

            return redirect(url_for("main.home"))
        else:
            print("else hits")
            REDIRECT_URI = url_for("api.callback", _external=True)
            CLIENT_ID = os.getenv("YAHOO_CLIENT_ID")
            CLIENT_SECRET = os.getenv("YAHOO_CLIENT_SECRET")
            RESPONSE_TYPE = "code"

            auth_url = f"https://api.login.yahoo.com/oauth2/request_auth?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={REDIRECT_URI}&response_type={RESPONSE_TYPE}"
            webbrowser.open_new_tab(auth_url)
            return render_template(
                "auth.html",
                # auth_url=auth_url,
            )
    except Exception as e:
        print("Error in oauth:", e)
        return jsonify({"error": "Error in oauth"}), 400


@api.route("/callback", methods=["GET", "POST"])
def callback():
    user = g.user
    if not user:
        return redirect(url_for("main.login"))
    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        if not verification_code:
            return jsonify({"error": "Missing verification code"}), 400

        # # good for localhost
        sys.stdin = StringIO(verification_code)

        ## for docker

    query = YahooFantasySportsQuery(
        league_id="<YAHOO_LEAGUE_ID>",
        game_code="nfl",
        game_id=449,
        yahoo_consumer_key=os.getenv("YAHOO_CLIENT_ID"),
        yahoo_consumer_secret=os.getenv("YAHOO_CLIENT_SECRET"),
    )

    curr_user_guid = query.get_current_user()._extracted_data["guid"]
    yahoo_access_token = query._yahoo_access_token_dict
    yahoo_access_token["guid"] = curr_user_guid
    update_user_guid(user["id"], curr_user_guid)
    try:
        save_access_token(g.user_id, yahoo_access_token)

    except ValueError as e:
        flash(str(e))
        return redirect(url_for("api.oauth"))
    return redirect(url_for("main.home"))


@main.route("/home", methods=["GET", "POST"])
def home():

    if g.access_token:
        yahoo_access_token = g.access_token
    else:
        return redirect(url_for("api.oauth"))

    user_id = g.user_id
    user = get_user_by_id(user_id)
    user_guid = user["guid"]

    query = YahooFantasySportsQuery(
        league_id="<YAHOO_LEAGUE_ID>",
        game_code="nfl",
        game_id=449,
        yahoo_access_token_json=yahoo_access_token,
    )
    # curr_user_team = query.get_current_user()._extracted_data["guid"]
    leagues = query.get_user_leagues_by_game_key(449)

    for league in leagues:
        if isinstance(league.name, bytes):
            league.name = league.name.decode("utf-8")

    # Set the league name in the session
    if request.method == "POST":
        selected_league_id = request.form.get("league_id")
        selected_league = next(
            (league for league in leagues if league.league_id == selected_league_id),
            None,
        )
        if selected_league:
            session["league_name"] = selected_league.name

    # Get connection from the pool
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT "id", "name", "logo_url", "espn_link" ' 'FROM "nfl_teams"')

    rows = cursor.fetchall()

    # Convert rows to dictionary format
    teams_data = [
        {
            "id": row[0],
            "name": row[1],
            "logo_url": row[2],
            "espn_link": row[3],
        }
        for row in rows
    ]

    # Close cursor and release connection
    cursor.close()
    release_connection(connection)

    if request.method == "POST":
        selected_league_id = request.form.get("league_id")
        session["selected_league_id"] = selected_league_id
        query = YahooFantasySportsQuery(
            league_id=selected_league_id,
            game_code="nfl",
            game_id=449,
            yahoo_access_token_json=yahoo_access_token,
        )

        player_team_data = []
        league_teams = query.get_league_teams()

        for team in league_teams:
            team_info = query.get_team_info(team.team_id)._extracted_data
            team_roster = team_info["roster"]
            for player in team_roster.players:
                key = player.player_key
                player_stats = query.get_player_stats_by_week(key, chosen_week=13)
                season_totals = query.get_player_stats_for_season(key)
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
                        "ppg": (
                            player_stats.player_points.total
                            / player_stats.player_stats.stats[0].value
                            if player_stats.player_stats.stats[0].value != 0
                            else 0
                        ),
                        "fantasy_league": session["league_name"],
                    }
                )

                player_team_data[-1][
                    "season_totals"
                ] = season_totals.player_points.total

        upsert_player_data(player_team_data, league=session.get("league_name"))

        # Pass team name and players to the template
        return render_template(
            "home.html",
            leagues=leagues,
            player_and_teams_loaded=True,
        )

    return render_template(
        "home.html",
        leagues=leagues,
        teams_data=teams_data,
    )


@main.route("/league_players")
def league_players():
    try:
        # Get the position filter from query parameters
        position_filter = request.args.get("positionFilter", "", type=str)

        # Get connection from the pool
        connection = get_connection()
        cursor = connection.cursor()

        # Modify SQL query based on position filter
        if position_filter:
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" FROM "player_data" '
                'WHERE "primary_position" = %s AND "league" = %s',
                (position_filter,
                session["league_name"],),
            )
        else:
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" '
                'FROM "player_data" WHERE "league" = %s',
                (session["league_name"],),
            )

        rows = cursor.fetchall()

        # Convert rows to dictionary format
        waiver_wire_players = [
            {
                "Player": row[0],
                "Pos": row[1],
                "img": row[2],
                "previous_performance": row[3],
                "bye": row[4],
                "status": row[5],
                "injury": row[6],
                "previous_week": row[7],
                "total_points": row[8],
                "team_abb": row[9],
                "season_totals": row[10],
            }
            for row in rows
        ]

        # Close cursor and release connection
        cursor.close()
        release_connection(connection)

        # Render the waiver_wire template with player data and filter info
        return render_template(
            "league_players.html",
            waiver_wire_players=waiver_wire_players,
            position_filter=position_filter,
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
        if total_points >= 280:
            return "A+"
        elif total_points >= 260:
            return "A"
        elif total_points >= 240:
            return "A-"
        elif total_points >= 220:
            return "B+"
        elif total_points >= 200:
            return "B"
        elif total_points >= 180:
            return "B-"
        elif total_points >= 160:
            return "C+"
        elif total_points >= 140:
            return "C"
        elif total_points >= 120:
            return "C-"
        elif total_points >= 100:
            return "D+"
        elif total_points >= 80:
            return "D"
        elif total_points >= 60:
            return "D-"
        else:
            return "F"
    elif position in ["RB", "WR"]:
        if total_points >= 230:
            return "A+"
        elif total_points >= 210:
            return "A"
        elif total_points >= 190:
            return "A-"
        elif total_points >= 170:
            return "B+"
        elif total_points >= 150:
            return "B"
        elif total_points >= 130:
            return "B-"
        elif total_points >= 110:
            return "C+"
        elif total_points >= 90:
            return "C"
        elif total_points >= 70:
            return "C-"
        elif total_points >= 50:
            return "D+"
        elif total_points >= 30:
            return "D"
        elif total_points >= 20:
            return "D-"
        else:
            return "F"
    elif position == "TE":
        if total_points >= 130:
            return "A+"
        elif total_points >= 110:
            return "A"
        elif total_points >= 90:
            return "A-"
        elif total_points >= 70:
            return "B+"
        elif total_points >= 50:
            return "B"
        elif total_points >= 40:
            return "B-"
        elif total_points >= 30:
            return "C+"
        elif total_points >= 20:
            return "C"
        elif total_points >= 10:
            return "C-"
        elif total_points >= 5:
            return "D+"
        elif total_points >= 2:
            return "D"
        elif total_points >= 1:
            return "D-"
        else:
            return "F"
    elif position == "K":
        if total_points >= 130:
            return "A+"
        elif total_points >= 124:
            return "A"
        elif total_points >= 118:
            return "A-"
        elif total_points >= 112:
            return "B+"
        elif total_points >= 106:
            return "B"
        elif total_points >= 100:
            return "B-"
        elif total_points >= 94:
            return "C+"
        elif total_points >= 88:
            return "C"
        elif total_points >= 82:
            return "C-"
        elif total_points >= 76:
            return "D+"
        elif total_points >= 70:
            return "D"
        else:
            return "F"
    elif position == "DEF":
        if total_points >= 130:
            return "A+"
        elif total_points >= 110:
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

    if optimal_qb is None:    
        return "No valid QB on roster - pick someone up off waiver wire!"
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

    if optimal_te is None:    
        return "No valid TE on roster - pick someone up off waiver wire!"
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

    if optimal_flex is None:    
        return "No valid FLEX on roster - pick someone up off waiver wire!"
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

    if optimal_k is None:    
        return "No valid K on roster - pick someone up off waiver wire!"
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

    if optimal_dst is None:    
        return "No valid DST on roster - pick someone up off waiver wire!"
    return optimal_dst


def grade_to_numeric(grade):
    """Convert a grade to a numeric value for averaging."""
    grade_mapping = {
        "A+": 4.3,
        "A": 4.0,
        "A-": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "B-": 2.7,
        "C+": 2.3,
        "C": 2.0,
        "C-": 1.7,
        "D+": 1.3,
        "D": 1.0,
        "D-": 0.7,
        "F": 0.0,
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


@main.route("/team-analyzer", methods=["GET", "POST"])
def team_analyzer():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT DISTINCT "team_name" FROM "player_data" WHERE "league" = %s',
            (session["league_name"],),
        )
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

        if request.method == "POST":
            selected_team = request.form.get("team")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" FROM "player_data" WHERE "team_name" = %s AND "league" = %s',
                (
                    selected_team,
                    session["league_name"],
                ),
            )
            team_players = cursor.fetchall()
            cursor.close()
            release_connection(connection)

            for player in team_players:
                player_data = {
                    "Player": player[0],
                    "Pos": player[1],
                    "img": player[2],
                    "previous_performance": player[3],
                    "bye": player[4],
                    "status": player[5],
                    "injury": player[6],
                    "previous_week": player[7],
                    "total_points": player[8],
                    "team_abb": player[9],
                    "season_totals": player[10],
                }
                player_data["grade"] = analyze_player(player_data)
                players.append(player_data)

                # Collect grades for each position
                pos = player_data["Pos"]
                if pos not in position_grades:
                    position_grades[pos] = []
                position_grades[pos].append(grade_to_numeric(player_data["grade"]))

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
                "DST": dst,
            }

            min_depth = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}

            # Calculate average grades for each position
            filtered_position_grades = {
                pos: grades
                for pos, grades in position_grades.items()
                if pos not in ["K", "DEF"] and len(grades) >= min_depth.get(pos, 0)
            }
            if filtered_position_grades:
                avg_grades = {
                    pos: (sum(grades) / len(grades))
                    + (0.2 * (len(grades) - min_depth.get(pos, 0)))
                    for pos, grades in filtered_position_grades.items()
                }
                strengths = max(avg_grades, key=avg_grades.get)
                weaknesses = min(avg_grades, key=avg_grades.get)

                strengths_grade = numeric_to_grade(avg_grades[strengths])
                weaknesses_grade = numeric_to_grade(avg_grades[weaknesses])
            else:
                strengths = "N/A"
                strengths_grade = "N/A"
                weaknesses = "N/A"
                weaknesses_grade = "N/A"

        return render_template(
            "team_analyzer.html",
            teams=teams,
            selected_team=selected_team,
            players=players,
            ideal_lineup=ideal_lineup,
            strengths=strengths,
            strengths_grade=strengths_grade,
            weaknesses=weaknesses,
            weaknesses_grade=weaknesses_grade,
        )
    except Exception as e:
        print(f"Error fetching team analyzer data: {e}")
        return render_template("error.html", error_message=str(e))


@main.route("/trade-builder", methods=["GET", "POST"])
def trade_builder():
    curr_user = g.user_id

    connection = get_connection()
    cursor = connection.cursor()

    # Fetch all teams
    cursor.execute(
        'SELECT DISTINCT "team_name" FROM "player_data" WHERE "league" = %s',
        (session["league_name"],),
    )
    all_teams = cursor.fetchall()
    cursor.close()
    release_connection(connection)

    teams = [team[0] for team in all_teams if team[0] is not None]

    team1_roster = []
    team2_roster = []
    team1_roster_info = []
    team2_roster_info = []

    if request.method == "POST":
        team1 = request.form.get("team1")
        team2 = request.form.get("team2")

        if team1 and team2 and team1 != team2:
            connection = get_connection()
            cursor = connection.cursor()

            # Fetch team 1 roster
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" FROM "player_data" WHERE "team_name" = %s',
                (team1,),
            )
            team1_roster = cursor.fetchall()

            # Fetch team 2 roster
            cursor.execute(
                'SELECT "player_name", "primary_position", "image", "previous_performance", "bye", "status", "injury", "previous_week", "total_points", "team_abb", "season_totals" FROM "player_data" WHERE "team_name" = %s',
                (team2,),
            )
            team2_roster = cursor.fetchall()

            cursor.close()
            release_connection(connection)

            for player in team1_roster:
                team1_info = {
                    "Player": player[0],
                    "Pos": player[1],
                    "img": player[2],
                    "previous_performance": player[3],
                    "bye": player[4],
                    "status": player[5],
                    "injury": player[6],
                    "previous_week": player[7],
                    "total_points": player[8],
                    "team_abb": player[9],
                    "season_totals": player[10],
                }
                team1_roster_info.append(team1_info)

            for player in team2_roster:
                team2_info = {
                    "Player": player[0],
                    "Pos": player[1],
                    "img": player[2],
                    "previous_performance": player[3],
                    "bye": player[4],
                    "status": player[5],
                    "injury": player[6],
                    "previous_week": player[7],
                    "total_points": player[8],
                    "team_abb": player[9],
                    "season_totals": player[10],
                }
                team2_roster_info.append(team2_info)
            print(team1_roster_info)

    return render_template(
        "trade_builder.html",
        teams=teams,
        team1_roster=team1_roster_info,
        team2_roster=team2_roster_info,
    )
