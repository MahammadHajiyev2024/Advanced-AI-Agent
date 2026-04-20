import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_collection(name="db_schema", embedding_function=embedding_functions.DefaultEmbeddingFunction())

# Test it!
results = collection.query(query_texts=["dividend data"], n_results=1)
print(results['documents'])