import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path


#0 Path Logic
ROOT_DIR = Path(__file__).parent.parent
SCHEMA_PATH = ROOT_DIR / "data" / "US_Stock_Market_DB_Schema.txt"
CHROMA_PATH = ROOT_DIR / "data" / "chroma_db"

# 1. Initialize local persistent storage
client = chromadb.PersistentClient(path="./data/chroma_db")

# 2. Use a local embedding function (or Ollama)
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="db_schema", embedding_function=default_ef)

# 3. Read your schema file and add to collection
with open(SCHEMA_PATH, "r") as f:
    schema_content = f.read()
    # In a real project, you'd split this by table name
    collection.add(
        documents=[schema_content],
        ids=["stock_market_schema"]
    )

print("Schema successfully ingested into ChromaDB!")