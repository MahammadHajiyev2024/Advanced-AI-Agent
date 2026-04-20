import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_postgres_query(sql_query: str):
    """Encapsulated DB logic: Open connection, execute, return results, close."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        with conn.cursor() as cur:
            cur.execute(sql_query)
            return cur.fetchall()
    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()