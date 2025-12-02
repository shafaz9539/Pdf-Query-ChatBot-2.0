from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from ..database.connection import get_chroma_client_instance
from ..services.rag_service import RAG_PIPLINE 
from ..core.security import get_current_user
from ..models.document import User 

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    file_id: str
    question: str
    top_k: int = 5 
    
@router.post("/", status_code=status.HTTP_200_OK)
async def query_pdf(
    request: Request,
    payload: QueryRequest,
    # 🚨 FIX 1: Add authentication dependency
    current_user: User = Depends(get_current_user),
    # 🚨 FIX 2: Inject the initialized Chroma client instance
    chroma_client = Depends(get_chroma_client_instance)
):
    try:
        # 🚨 FIX 3: Instantiate the service correctly (Binding 'self' and dependencies)
        service = RAG_PIPLINE(
            user_id=str(current_user.id),
            chroma_client=chroma_client
        )
        
        # 🚨 FIX 4: Call the method from the service instance
        answer_data = await service.query_and_answer_pdf(
            file_id=payload.file_id,
            question=payload.question,
            top_k=payload.top_k
        )

        return answer_data

    except ValueError as e:
        # Catch custom exception raised by the service (e.g., "No content found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except Exception as e:
        # Avoid generic 500 block; FastAPI handles uncaught errors better
        # This remains for debugging external failures:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Query Error: {e}")