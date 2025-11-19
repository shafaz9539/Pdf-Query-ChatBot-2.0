import uuid
import tempfile
import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from src.services.pdf_reader import extract_clean_markdown
from src.services.chunker import chunk_with_token_safety
from src.services.embedder import embed_chunks
from src.db.chroma_ops import add_embeddings  

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_MB = 20


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Validate extension
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        file_bytes = await file.read()

        # Validate size
        if len(file_bytes) > MAX_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Max {MAX_MB}MB allowed")

        file_id = str(uuid.uuid4())

        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file_bytes)
            temp_pdf_path = temp_pdf.name

        # Extract cleaned pages
        cleaned_pages = extract_clean_markdown(temp_pdf_path)

        # Chunk with token safety
        chunks = chunk_with_token_safety(
            cleaned_pages,
            model="gemini-embedding-001",
            max_tokens=800,
            chunk_size=1200,
            chunk_overlap=200
        )

        # Extract text only
        chunk_texts = [c["text"] for c in chunks]

        # Embed chunks
        embeddings = embed_chunks(chunk_texts)

        # Prepare metadata
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [
            {
                "file_id": file_id,
                "chunk_id": c["chunk_id"],
                "page_number": c["page_number"],
                "token_count": c["token_count"]
            }
            for c in chunks
        ]

        # Store embeddings
        stored_count = add_embeddings(
            chunks=chunk_texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        # Cleanup temp file
        os.remove(temp_pdf_path)

        return {
            "filename": file.filename,
            "fileId": file_id,
            "total_cleaned_pages": len(cleaned_pages),
            "total_chunks": len(chunks),
            "stored_chunks": stored_count,
            "message": "PDF uploaded, processed, chunked, embedded & stored successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")
