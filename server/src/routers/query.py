from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db.chroma_ops import query_similar_chunks
from src.services.embedder import embed_query
from src.services.rag import generate_answer  

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    file_id: str
    question: str
    top_k: int = 5  


@router.post("/")
async def query_pdf(payload: QueryRequest):

    file_id = payload.file_id
    question = payload.question
    top_k = payload.top_k

    try:
        # 1️⃣ Embed the query using Gemini embedding model
        query_vec = embed_query(question)

        # 2️⃣ Search Chroma using file filter
        res = query_similar_chunks(file_id=file_id, query_embedding=query_vec, top_k=top_k)

        if not res or not res.get("documents") or not res["documents"][0]:
            raise HTTPException(status_code=404, detail="No relevant content found for this file_id")

        # 3️⃣ Extract docs + metadata
        docs = res["documents"][0]
        metadatas = res.get("metadatas", [[]])[0]

        # 4️⃣ Sort chunks by page_number
        combined = list(zip(docs, metadatas))
        combined.sort(key=lambda x: x[1].get("page_number", 0))

        sorted_docs = [x[0] for x in combined]
        sorted_meta = [x[1] for x in combined]

        # 5️⃣ Limit context length for Gemini
        safe_context = "\n\n".join(sorted_docs[:top_k])

        # 6️⃣ Ask Gemini Flash using RAG
        answer = generate_answer(
            question=question,
            context=safe_context
        )

        return {
            "file_id": file_id,
            "question": question,
            "answer": answer,
            "chunks_used": sorted_docs[:top_k],
            "metadatas_used": sorted_meta[:top_k],
            "top_k": top_k
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
