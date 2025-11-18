from typing import List, Dict, Any
from src.db.chroma_client import get_collection


def add_embeddings(
    chunks: List[str],                # chunk texts
    embeddings: List[List[float]],    # vectors
    ids: List[str],                   # chunk_ids (UUIDs)
    metadatas: List[Dict[str, Any]]   # metadata for each chunk
):
    """
    Store chunk embeddings into Chroma.
    - ids:       unique UUID chunk IDs
    - chunks:    chunk text
    - embeddings: vector list
    - metadatas: list of metadata dicts (file_id, page_number, token_count)
    """

    collection = get_collection()

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"✅ Added {len(ids)} embeddings to Chroma.")
    return len(ids)



def query_similar_chunks(
    file_id: str,
    query_embedding: List[float],
    top_k: int
):
    """
    Query Chroma by file_id filter + similarity search.
    Returns full Chroma result.
    """

    collection = get_collection()

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"file_id": file_id}
    )



def delete_file_chunks(file_id: str):
    """
    Delete all embeddings belonging to file_id.
    """

    collection = get_collection()

    items = collection.get(where={"file_id": file_id})

    ids = items.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)
