# /app/routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, session
import os
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
    get_access_token_by_user_id
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


@main.route("/register", methods=["GET", "POST"])
def register():
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
        return redirect(url_for("api.oauth"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        user = get_user_by_email(email)
        if not user or not verify_password(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 400

        session["user_id"] = user["id"]
        return redirect(url_for("main.home"))

    return render_template("login.html")


@main.route("/logout",methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        # Clear session and pop all keys from g
        session.clear()
        keys = g.__dict__.keys()
        
        for key in list(keys):
            g.pop(key)
        
            
        # Redirect to Yahoo's logout page
        return render_template("logout.html")
    # return redirect(f"https://login.yahoo.com/config/login?logout=1&.direct=1&.done={url_for('index', _external=True)}")
    return render_template("confirm_logout.html")


@api.route("/oauth", methods=["GET", "POST"])
def oauth():
    print("oauth")
    user_id = g.user_id
    if not user_id:
        print("no user_id in oauth whoops")
        return redirect(url_for("main.login"))
    print("user_id: ", user_id)
    access_token = g.access_token

    # TODO I think this needs to be more robust haha, what if access_token is expired or access_token = 42 or something like that
    if access_token is not None:
        return redirect(url_for("main.home"))
    else:
        print("\noauth else hits!\n")
        REDIRECT_URI = url_for("api.callback", _external=True)
        CLIENT_ID = os.getenv("YAHOO_CLIENT_ID")
        CLIENT_SECRET = os.getenv("YAHOO_CLIENT_SECRET")
        RESPONSE_TYPE = "code"
            
        auth_url = f"https://api.login.yahoo.com/oauth2/request_auth?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={REDIRECT_URI}&response_type={RESPONSE_TYPE}"
        webbrowser.open_new_tab(auth_url)
        return render_template("auth.html")


@api.route("/callback", methods=["GET", "POST"])
def callback():
   
    # print("callback")
    user = g.user
    if not user:
        return redirect(url_for("main.login"))
    # print("user: ", user)
    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        if not verification_code:
            return jsonify({"error": "Missing verification code"}), 400

        sys.stdin = StringIO(verification_code)

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
    save_access_token(user["id"],yahoo_access_token)
    gotten_token_after_save = get_access_token_by_user_id(user["id"])
    print("gotten_token_after_save: \n",gotten_token_after_save,"\n")
    # Update the user's GUID in the users table if it is currently null
    user_id = user["id"]
    return redirect(url_for("main.home"))


@main.route("/home", methods=["GET", "POST"])
def home():

    # TODO does not get access token here because it doesn't get right guid, and that's how we were accessing access token.
    if g.access_token:
        yahoo_access_token = g.access_token
        print("home", yahoo_access_token)
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

    leagues = query.get_user_leagues_by_game_key(449)

    for league in leagues:
        if isinstance(league.name, bytes):
            league.name = league.name.decode("utf-8")

    if request.method == "POST":
        selected_league_id = request.form.get("league_id")
        session["selected_league_id"] = selected_league_id
        query = YahooFantasySportsQuery(
            league_id=selected_league_id,
            game_code="nfl",
            game_id=449,
            yahoo_access_token_json=yahoo_access_token,
        )

        league_teams = query.get_league_teams()
        print([team.serialized() for team in league_teams])
        for team in league_teams:
            if isinstance(team.name, bytes):
                team.name = team.name.decode("utf-8")
            if team.is_owned_by_current_login == 1:
                curr_user_team = [team.team_id]

        team_info = query.get_team_info(curr_user_team[0])._extracted_data

        serializable_team_info = extract_serializable_data(team_info)
        team_name = team_info["name"]
        team_roster = team_info["roster"]

        session["user_team"] = {"team_name": team_name, "team_roster": team_roster}

        return jsonify(serializable_team_info)

    return render_template("home.html", leagues=leagues)


def update_ownership():
    # Load the CSV file into a DataFrame
    df = pd.read_csv("data/player_team_data.csv")

    try:
        # Get connection from the pool
        connection = get_connection()
        cursor = connection.cursor()

        # Iterate over the DataFrame and update the database
        for index, row in df.iterrows():
            player_name = row["player_name"]
            owner = row["team_name"]  # Assuming 'team_name' indicates ownership

            # Check if the player is in the database
            cursor.execute(
                'SELECT COUNT(*) FROM "seasonstats" WHERE "Player" = %s', (player_name,)
            )
            exists = cursor.fetchone()[0]

            if exists > 0:
                # Update the ownership status in the database
                cursor.execute(
                    'UPDATE "seasonstats" SET "fantasy_owner" = %s WHERE "Player" = %s',
                    (owner, player_name),
                )

        # Commit the transaction
        connection.commit()

        # Close cursor and release connection
        cursor.close()
        release_connection(connection)

        return jsonify({"message": "Ownership status updated successfully."}), 200

    except Exception as error:
        print("Error updating ownership status:", error)
        return jsonify({"error": "Error updating ownership status."}), 500


@main.route("/waiver-wire")
def waiver_wire():
    try:
        # Get the current page number and position filter from query parameters
        page = request.args.get("page", 1, type=int)
        position_filter = request.args.get("positionFilter", "", type=str)
        per_page = 25  # Number of players per page

        # Get connection from the pool
        connection = get_connection()
        cursor = connection.cursor()

        # Modify SQL query based on position filter
        if position_filter:
            cursor.execute(
                'SELECT "Player", "Pos", "Rankbypos" FROM "seasonstats" '
                'WHERE "fantasy_owner" IS NULL AND "Pos" = %s',
                (position_filter,),
            )
        else:
            cursor.execute(
                'SELECT "Player", "Pos", "Rankbypos" FROM "seasonstats" '
                'WHERE "fantasy_owner" IS NULL'
            )

        rows = cursor.fetchall()

        # Convert rows to dictionary format
        waiver_wire_players = [
            {
                "name": row[0],
                "position": row[1],
                "projection": f"{row[2]}",
            }
            for row in rows
        ]

        # Calculate pagination
        total = len(waiver_wire_players)
        total_pages = (total + per_page - 1) // per_page  # Calculate total pages
        start = (page - 1) * per_page
        end = start + per_page
        paginated_players = waiver_wire_players[start:end]

        # Close cursor and release connection
        cursor.close()
        release_connection(connection)

        # Render the waiver_wire template with paginated player data and filter info
        return render_template(
            "waiver_wire.html",
            waiver_wire_players=paginated_players,
            page=page,
            total_pages=total_pages,
            position_filter=position_filter,
        )

    except Exception as error:
        print("Error fetching waiver wire data:", error)
        return "Error loading waiver wire", 500


def analyze_player(player):
    if player["Pos"] in ["QB", "TE"]:
        if player["Rankbypos"] == 1:
            return "A+: best at Position!"
        elif 2 <= player["Rankbypos"] <= 5:
            return "A"
        elif 6 <= player["Rankbypos"] <= 10:
            return "B"
        elif 11 <= player["Rankbypos"] <= 15:
            return "C"
        elif 16 <= player["Rankbypos"] <= 20:
            return "D"
        else:
            return "F"
    elif player["Pos"] in ["WR", "RB"]:
        if player["Rankbypos"] == 1:
            return "A+"
        elif 2 <= player["Rankbypos"] <= 5:
            return "A"
        elif 6 <= player["Rankbypos"] <= 10:
            return "B"
        elif 11 <= player["Rankbypos"] <= 15:
            return "C"
        elif 16 <= player["Rankbypos"] <= 20:
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


@main.route("/team-analyzer", methods=["GET", "POST"])
def team_analyzer():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT "fantasy_owner" FROM "seasonstats"')
        all_teams = cursor.fetchall()
        cursor.close()
        release_connection(connection)

        teams = [team[0] for team in all_teams if team[0] is not None]
        selected_team = None
        players = []

        if request.method == "POST":
            selected_team = request.form.get("team")
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                'SELECT "Player", "Pos", "Rankbypos", "WK1Pts", "WK2Pts", "WK3Pts", "WK4Pts", "WK5Pts", "WK6Pts" FROM "seasonstats" WHERE "fantasy_owner" = %s',
                (selected_team,),
            )
            team_players = cursor.fetchall()
            cursor.close()
            release_connection(connection)

            for player in team_players:
                player_data = {
                    "Player": player[0],
                    "Pos": player[1],
                    "Rankbypos": player[2],
                    "WK1Pts": player[3],
                    "WK2Pts": player[4],
                    "WK3Pts": player[5],
                    "WK4Pts": player[6],
                    "WK5Pts": player[7],
                    "WK6Pts": player[8],
                }
                player_data["grade"] = analyze_player(player_data)
                total_points, std_dev = calculate_consistency(player_data)
                player_data["total_points"] = (
                    total_points if total_points is not None else "N/A"
                )
                player_data["std_dev"] = std_dev if std_dev is not None else "N/A"
                players.append(player_data)

        return render_template(
            "team_analyzer.html",
            teams=teams,
            selected_team=selected_team,
            players=players,
        )
    except Exception as e:
        print(f"Error fetching team analyzer data: {e}")
        return render_template("error.html", error_message=str(e))


@main.route("/trade-builder", methods=["GET", "POST"])
def trade_builder():
    connection = get_connection()
    cursor = connection.cursor()

    # Fetch all teams
    cursor.execute('SELECT DISTINCT "fantasy_owner" FROM "seasonstats"')
    all_teams = cursor.fetchall()
    cursor.close()
    release_connection(connection)

    teams = [team[0] for team in all_teams if team[0] is not None]

    team1_roster = []
    team2_roster = []
    trade_feedback = None

    if request.method == "POST":
        team1 = request.form.get("team1")
        team2 = request.form.get("team2")

        if team1 and team2 and team1 != team2:
            connection = get_connection()
            cursor = connection.cursor()

            # Fetch team 1 roster
            cursor.execute(
                'SELECT "Player", "Pos", "Rankbypos" FROM "seasonstats" WHERE "fantasy_owner" = %s',
                (team1,),
            )
            team1_roster = cursor.fetchall()

            # Fetch team 2 roster
            cursor.execute(
                'SELECT "Player", "Pos", "Rankbypos" FROM "seasonstats" WHERE "fantasy_owner" = %s',
                (team2,),
            )
            team2_roster = cursor.fetchall()

            cursor.close()
            release_connection(connection)

        if request.form.get("your_player") and request.form.get("target_player"):
            your_player = request.form.get("your_player")
            target_player = request.form.get("target_player")
            trade_feedback = f"You proposed trading {your_player} for {target_player}."

    return render_template(
        "trade_builder.html",
        teams=teams,
        team1_roster=team1_roster,
        team2_roster=team2_roster,
        trade_feedback=trade_feedback,
    )
