from typing import List, Dict, Any

def add_embeddings(
    chroma_client,
    chunks: List[str],               
    embeddings: List[List[float]],    
    ids: List[str],                  
    metadatas: List[Dict[str, Any]]   
):
    """
    Store chunk embeddings into Chroma.
    - ids:       unique UUID chunk IDs
    - chunks:    chunk text
    - embeddings: vector list
    - metadatas: list of metadata dicts (file_id, page_number, token_count)
    """

    collection = chroma_client.get_collection("pdf_embeddings")
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"✅ Added {len(ids)} embeddings to Chroma.")
    return len(ids)

def query_similar_chunks(
    chroma_client,
    file_id: str,
    user_id: str,
    query_embedding: List[float],
    top_k: int
):
    """
    Query Chroma by file_id filter + similarity search.
    Returns full Chroma result.
    """

    collection = chroma_client.get_collection("pdf_embeddings")

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"$and": [{"file_id": file_id}, {"user_id": user_id}]}
    )



def delete_file_chunks(file_id: str, chroma_client) -> int:
    """
    Delete all embeddings belonging to file_id.
    """

    collection = chroma_client.get_collection("pdf_embeddings")

    items = collection.get(where={"file_id": file_id})

    ids = items.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)
