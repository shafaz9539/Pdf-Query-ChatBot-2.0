import os
import tempfile
import uuid

from .chroma_ops import add_embeddings, query_similar_chunks
from ..utils.chunker import chunk_with_token_safety
from ..utils.embedder import embed_chunks, embed_query
from ..utils.pdf_reader import extract_clean_markdown
from ..utils.generate_answer import generate_answer


class RAG_PIPLINE:
    def __init__(self, user_id: str, chroma_client):
        self.user_id = user_id
        self.chroma = chroma_client
        self.collection = self.chroma.get_or_create_collection(
            name="pdf_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    async def process_pdf(self, file_bytes: bytes, filename: str) -> dict:

        file_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file_bytes)
            temp_pdf_path = temp_pdf.name

        try:
            # 1. Extract and Chunk Text
            print("Extracting and chunking PDF...")
            cleaned_pages = extract_clean_markdown(temp_pdf_path)
            
            print(f"Extracted {len(cleaned_pages)} pages from PDF.")

            chunks = chunk_with_token_safety(
                cleaned_pages, model="gemini-embedding-001", max_tokens=800, 
                chunk_size=1200, chunk_overlap=200
            )
            chunk_texts = [c["text"] for c in chunks]
            
            print(f"Chunked into {len(chunk_texts)} pieces.")
            # 2. Embed and Prepare Metadata
            embeddings = embed_chunks(chunk_texts) 
            ids = [c["chunk_id"] for c in chunks]
            
            metadatas = [
                {
                    "file_id": file_id,
                    "user_id": self.user_id,
                    "chunk_id": c["chunk_id"],
                    "page_number": c["page_number"],
                }
                for c in chunks
            ]

            print("Embeddings generated.")
            stored_count = add_embeddings(
                chroma_client=self.chroma,
                chunks=chunk_texts, 
                embeddings=embeddings, 
                ids=ids, 
                metadatas=metadatas
            )

            print(f"Stored {stored_count} embeddings in Chroma.")
            # 4. Return results for the Controller to format
            return {
                "file_id": file_id,
                "stored_count": stored_count,
                "total_chunks": len(chunks)
            }
        finally:
            os.remove(temp_pdf_path)


    async def query_and_answer_pdf(self, file_id: str, question: str, top_k: int = 5) -> dict:
        # 1️⃣ Embed the query
        query_vec = embed_query(question)

        # 2️⃣ Search Chroma using BOTH filters
        # We must pass self.user_id for security and file_id for file context
        res = query_similar_chunks(
            chroma_client=self.chroma,
            user_id=self.user_id, 
            file_id=file_id, 
            query_embedding=query_vec, 
            top_k=top_k
        )

        if not res or not res.get("documents") or not res["documents"][0]:
            # Raise a standard Python exception (Service should not raise HTTPException)
            raise ValueError("No relevant content found for this file and user.")

        # 3️⃣ Extract and Sort Context
        docs = res["documents"][0]
        metadatas = res.get("metadatas", [[]])[0]

        # Sort chunks by page_number 
        combined = list(zip(docs, metadatas))
        combined.sort(key=lambda x: x[1].get("page_number", 0))

        sorted_docs = [x[0] for x in combined]
        sorted_meta = [x[1] for x in combined]

        # 4️⃣ Limit Context & Ask LLM
        safe_context = "\n\n".join(sorted_docs[:top_k])

        answer = generate_answer(
            question=question,
            context=safe_context
        )

        # 5️⃣ Return structured data (Service's output)
        return {
            "file_id": file_id,
            "question": question,
            "answer": answer,
            "chunks_used": sorted_docs[:top_k],
            "metadatas_used": sorted_meta[:top_k],
            "top_k": top_k
        }