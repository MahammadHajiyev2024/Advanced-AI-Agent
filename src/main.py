import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from google import genai
import chromadb
from chromadb.utils import embedding_functions


# Local Import 
from database import run_postgres_query
from prompts import SYSTEM_PROMPT

# Path & Env Logic 
load_dotenv()
ROOT_DIR = Path (__file__).parent.parent
CHROMA_PATH = ROOT_DIR / "data" / "chroma_db"

# --- ADD THIS SECTION TO CONNECT TO CHROMA ---
# This connects to the folder you created in your ingest script
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
default_ef = embedding_functions.DefaultEmbeddingFunction()
# We use get_collection because it already exists
collection = chroma_client.get_or_create_collection(
    name="db_schema", 
    embedding_function=default_ef
)

def get_context(user_query):
    results = collection.query(query_texts=[user_query], n_results=1)
    return results['documents'][0]

# Init the client with your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the "Digital Employee"
def ask_agent(user_query):
    # Step 1: Ask Gemini to generate SQL
    schema_context = get_context(user_query)

    enriched_instruction = f"{SYSTEM_PROMPT}\n\nRELEVANT DATABASE SCHEMA:\n{schema_context}"

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        config={"tools": [run_postgres_query], "system_instruction": enriched_instruction},
        contents=user_query
    )

    # Step 2: Check if Gemini made a function call
    for part in response.candidates[0].content.parts:
        if part.function_call:
            fn_call = part.function_call
            sql = fn_call.args['sql_query']
            print(f"Gemini wants to run SQL: {sql}")

            # Step 3: Actually execute it
            result = run_postgres_query(sql)
            print(f"Real DB Result: {result}")
            print(f"Query used:  {sql}")
            return

    # Fallback: Gemini just responded with text (no function call)
    print(f"Agent Response: {response.text}")


if __name__ == "__main__":
    ask_agent("What is the average of the 'high_price' in the year 2022 and what query did you use to find the answer?")