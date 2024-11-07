import psycopg2
from psycopg2 import pool, extras
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(override=True)

# Define your connection pool globally
try:
    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(
        1,
        20,
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port="5432",
        database="fantasy_football_db",
    )
    if postgreSQL_pool:
        print("Connection pool created successfully")

except (Exception, psycopg2.DatabaseError) as error:
    print("Error while connecting to PostgreSQL", error)


def get_connection():
    """
    Get a connection from the PostgreSQL connection pool.

    Returns:
        connection: A connection object from the connection pool.
    """
    return postgreSQL_pool.getconn()


def release_connection(connection):
    """
    Release a connection back to the PostgreSQL connection pool.

    Args:
        connection: The connection object to be released.
    """
    postgreSQL_pool.putconn(connection)


def table_exists(table_name):
    """
    Check if a table exists in the database.

    Args:
        table_name: The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
                """,
                (table_name,),
            )
            return cursor.fetchone()[0]
    except Exception as e:
        raise e
    finally:
        release_connection(conn)


def create_access_tokens_table():
    """
    Create the access_tokens table in the database if it does not already exist.
    The table stores access tokens and related information for users.

    Columns:
        id: SERIAL PRIMARY KEY
        user_id: INTEGER NOT NULL
        access_token: TEXT NOT NULL
        consumer_key: TEXT NOT NULL
        consumer_secret: TEXT NOT NULL
        guid: TEXT NOT NULL UNIQUE
        refresh_token: TEXT NOT NULL
        token_time: DOUBLE PRECISION NOT NULL
        token_type: TEXT NOT NULL
        created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS access_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    access_token TEXT NOT NULL,
                    consumer_key TEXT NOT NULL,
                    consumer_secret TEXT NOT NULL,
                    guid TEXT NOT NULL UNIQUE,
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


def create_users_table():
    """
    Create the users table in the database if it does not already exist.
    The table stores user information including email, password, and GUID.

    Columns:
        id: SERIAL PRIMARY KEY
        email: TEXT NOT NULL UNIQUE
        password: TEXT NOT NULL
        guid: TEXT
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    guid TEXT
                );
                """
            )
        conn.commit()
        print("Table users created successfully")
    except Exception as e:
        conn.rollback()
        print("Error creating table users", e)
    finally:
        release_connection(conn)


def create_user(email, password):
    """
    Create a new user in the users table with the provided email and password.
    The password is hashed before storing it in the database.

    Args:
        email: The email address of the user.
        password: The plaintext password of the user.
    """
    if not table_exists('users'):
        create_users_table()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                """
                INSERT INTO users (email, password)
                VALUES (%s, %s)
                """,
                (email, hashed_password),
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)


def get_user_by_email(email):
    """
    Retrieve a user from the users table by their email address.

    Args:
        email: The email address of the user.

    Returns:
        dict: A dictionary containing the user's information, or None if the user is not found.
    """
    if not table_exists('users'):
        create_users_table()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM users WHERE email = %s
                """,
                (email,),
            )
            return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        release_connection(conn)


def get_user_by_id(user_id):
    """
    Retrieve a user from the users table by their user ID.

    Args:
        user_id: The ID of the user.

    Returns:
        dict: A dictionary containing the user's information, or None if the user is not found.
    """
    if not table_exists('users'):
        create_users_table()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM users WHERE id = %s
                """,
                (user_id,),
            )
            user = cursor.fetchone()
            if user is None:
                print(f"No user found with id {user_id}")
            return user
    except Exception as e:
        raise e
    finally:
        release_connection(conn)


def verify_password(stored_password, provided_password):
    """
    Verify that the provided password matches the stored hashed password.

    Args:
        stored_password: The hashed password stored in the database.
        provided_password: The plaintext password provided by the user.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return check_password_hash(stored_password, provided_password)


def save_access_token(user_id, token_dict):
    """
    Save an access token and related information to the access_tokens table.
    If an entry with the same GUID already exists, it is updated.

    Args:
        user_id: The ID of the user.
        token_dict: A dictionary containing the access token information.
    """
    if not table_exists('access_tokens'):
        create_access_tokens_table()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO access_tokens (
                    user_id, access_token, consumer_key, consumer_secret, guid, refresh_token, token_time, token_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (guid) DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    consumer_key = EXCLUDED.consumer_key,
                    consumer_secret = EXCLUDED.consumer_secret,
                    refresh_token = EXCLUDED.refresh_token,
                    token_time = EXCLUDED.token_time,
                    token_type = EXCLUDED.token_type,
                    created_at = CURRENT_TIMESTAMP
                """,
                (
                    user_id,
                    token_dict["access_token"],
                    token_dict["consumer_key"],
                    token_dict["consumer_secret"],
                    token_dict["guid"],
                    token_dict["refresh_token"],
                    token_dict["token_time"],
                    token_dict["token_type"],
                ),
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)

def get_access_token_by_user_id(user_id):
    """
    Retrieve an access token from the access_tokens table by the user's user_id.

    Args:
        user_id: The ID of the user.

    Returns:
        dict: A dictionary containing the access token information, or None if the token is not found.
    """
    if not table_exists('access_tokens'):
        create_access_tokens_table()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT access_token, consumer_key, consumer_secret, guid, refresh_token, token_time, token_type
                FROM access_tokens
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        raise e
    finally:
        release_connection(conn)


def get_access_token_by_guid(guid):
    """
    Retrieve an access token from the access_tokens table by the user's GUID.

    Args:
        guid: The GUID of the user.

    Returns:
        dict: A dictionary containing the access token information, or None if the token is not found.
    """
    if not table_exists('access_tokens'):
        create_access_tokens_table()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT access_token, consumer_key, consumer_secret, guid, refresh_token, token_time, token_type
                FROM access_tokens
                WHERE guid = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (guid,),
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        raise e
    finally:
        release_connection(conn)


def update_user_guid(user_id, new_guid):
    """
    Update the user's GUID in the users table if it is currently null or different.

    Args:
        user_id: The ID of the user.
        new_guid: The new GUID to be set for the user.
    """
    if not table_exists('users'):
        create_users_table()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET guid = %s
                WHERE id = %s AND (guid IS NULL OR guid != %s)
                """,
                (new_guid, user_id, new_guid),
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)
