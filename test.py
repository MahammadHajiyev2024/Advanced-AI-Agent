import os
import psycopg2
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCHEMA = """
TABLE tickers (
    ticker TEXT,
    company_name TEXT
)
"""

# Agent 1: Generates SQL from natural language
def sql_agent(user_query: str) -> str:
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        config={"system_instruction": f"""You are a PostgreSQL expert.
Here is the database schema:
{SCHEMA}
Return ONLY the raw SQL query, no explanation, no markdown, no backticks."""},
        contents=user_query
    )
    sql = response.text.strip().removeprefix("```sql").removesuffix("```").strip()
    print(f"Generated SQL: {sql}")
    return sql

# Agent 2: Executes SQL against the database
def db_agent(sql_query: str):
    conn = psycopg2.connect(
        dbname="US_Stock_Market",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )
    try:
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Orchestrator: connects the two agents
def ask(user_query: str):
    sql = sql_agent(user_query)
    result = db_agent(sql)
    print(f"Result: {result}")

if __name__ == "__main__":
    ask("How many distinct ticker values are there in the tickers table?")