import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv(override=True)


# Define your connection pool globally
try:
    sleep(1)
    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "example_password"),
        host=os.getenv("POSTGRES_HOST", "db"),
        port="5432",
        database=os.getenv("POSTGRES_DB", "fantasy_football_db")
    )
    if postgreSQL_pool:
        print("Connection pool created successfully")

except (Exception, psycopg2.DatabaseError) as error:
    print("Error while connecting to PostgreSQL", error)

def get_connection():
    # Fetch a connection from the pool
    return postgreSQL_pool.getconn()

def release_connection(connection):
    # Return the connection to the pool
    postgreSQL_pool.putconn(connection)

def create_player_data_table():
    """Create player_data table if it does not exist."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS "player_data" (
            "id" SERIAL PRIMARY KEY,
            "player_name" VARCHAR(255) NOT NULL,
            "team_name" VARCHAR(255),
            "primary_position" VARCHAR(50),
            "bye" INTEGER,
            "team_abb" VARCHAR(10),
            "image" TEXT,
            "status" VARCHAR(50),
            "injury" TEXT,
            "player_key" VARCHAR(100) UNIQUE NOT NULL,
            "previous_week" INTEGER,
            "previous_performance" NUMERIC,
            "games_played" INTEGER,
            "total_points" NUMERIC,
            "ppg" NUMERIC
        );
        '''

        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'player_data' created successfully or already exists.")

    except Exception as error:
        print("Error creating table:", error)
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Call the function to create the table    


def player_exists(cursor, player_name):
    """Check if the player exists in the database by name."""
    cursor.execute(
        'SELECT COUNT(*) FROM "player_data" WHERE "player_name" = %s', (player_name,)
    )
    return cursor.fetchone()[0] > 0

def update_player_data(cursor, player):
    """Update player information in the database."""
    cursor.execute(
        '''UPDATE "player_data"
        SET "team_name" = %s, "primary_position" = %s, "bye" = %s, 
            "team_abb" = %s, "image" = %s, "status" = %s, "injury" = %s, 
            "player_key" = %s, "previous_week" = %s, 
            "previous_performance" = %s, "games_played" = %s, 
            "total_points" = %s, "ppg" = %s
        WHERE "player_name" = %s''',
        (player["team_name"], player["primary_position"], player["bye"], 
         player["team_abb"], player["image"], player["status"], 
         player["injury"], player["player_key"], player["previous_week"], 
         player["previous_performance"], player["games_played"], 
         player["total_points"], player["ppg"], player["player_name"])
    )

def insert_player_data(cursor, player):
    """Insert new player data into the database."""
    cursor.execute(
        '''INSERT INTO "player_data" 
        ("player_name", "team_name", "primary_position", "bye", 
         "team_abb", "image", "status", "injury", 
         "player_key", "previous_week", "previous_performance", 
         "games_played", "total_points", "ppg") 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (player["player_name"], player["team_name"], player["primary_position"], 
         player["bye"], player["team_abb"], player["image"], 
         player["status"], player["injury"], player["player_key"], 
         player["previous_week"], player["previous_performance"], 
         player["games_played"], player["total_points"], player["ppg"])
    )

def upsert_player_data(player_team_data):
    """Upsert player data: update existing or insert new player data."""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        for player in player_team_data:
            if player_exists(cursor, player["player_name"]):
                update_player_data(cursor, player)
            else:
                insert_player_data(cursor, player)

        connection.commit()
        print("Player data upserted successfully.")

    except Exception as error:
        print("Error during upsert operation:", error)
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
