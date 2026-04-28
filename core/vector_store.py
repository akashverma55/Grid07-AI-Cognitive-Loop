import chromadb
from chromadb.config import Settings

def get_vector_store(collections_name:str = "bot_personas")->chromadb.Collection:
    client = chromadb.EphemeralClient(
        settings = Settings(anonymized_telemetry = False)
    )

    collection = client.get_or_create_collection(
        name = collections_name,
        metadata = {"hnsw:space":"cosine"}
    )

    return collection 