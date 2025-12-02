
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from ..core.security import get_current_user
from ..database.connection import get_chroma_client_instance
from ..services.rag_service import RAG_PIPLINE


router = APIRouter(prefix="/upload", tags=["upload"])

MAX_MB = 20


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...), 
    current_user=Depends(get_current_user),
    chroma_client = Depends(get_chroma_client_instance)
    ):
    try:

        file_bytes = await file.read()

        print("Starting RAG pipeline processing...")
        result = await RAG_PIPLINE(user_id=str(current_user.id), chroma_client=chroma_client).process_pdf(
            file_bytes=file_bytes,
            filename=file.filename
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")
