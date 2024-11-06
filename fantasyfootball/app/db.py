import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

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

