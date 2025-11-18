from chromadb import PersistentClient

client = PersistentClient(path="./vector_store")


def get_collection():
    """
    Returns (or creates) the main ChromaDB collection.
    Cosine similarity works best for embeddings.
    """
    return client.get_or_create_collection(
        name="pdf_embeddings",
        metadata={"hnsw:space": "cosine"} 
    )
