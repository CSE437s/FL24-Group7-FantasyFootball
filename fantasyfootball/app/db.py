import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from psycopg2 import extras
from flask import g

load_dotenv(override=True)

# Define your connection pool globally
try:
    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port="5432",
        database="fantasy_football_db"
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

def save_access_token(token_dict):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO access_tokens (
                    access_token, consumer_key, consumer_secret, guid, refresh_token, token_time, token_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    token_dict['access_token'],
                    token_dict['consumer_key'],
                    token_dict['consumer_secret'],
                    token_dict['guid'],
                    token_dict['refresh_token'],
                    token_dict['token_time'],
                    token_dict['token_type']
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def get_access_token():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT access_token, consumer_key, consumer_secret, guid, refresh_token, token_time, token_type
                FROM access_tokens
                ORDER BY id DESC
                LIMIT 1
                """
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        raise e
    finally:
        release_connection(conn)

def create_access_tokens_table():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS access_tokens (
                    id SERIAL PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    consumer_key TEXT NOT NULL,
                    consumer_secret TEXT NOT NULL,
                    guid TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    token_time DOUBLE PRECISION NOT NULL,
                    token_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        conn.commit()
        print("Table access_tokens created successfully")
    except Exception as e:
        conn.rollback()
        print("Error creating table access_tokens", e)
    finally:
        release_connection(conn)

