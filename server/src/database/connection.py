from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from beanie import init_beanie 
from chromadb import PersistentClient
from fastapi import Request, HTTPException, status
from chromadb.api import ClientAPI 

from ..core.config import settings
from ..models.document import User, RefreshToken

mongo_client: AsyncMongoClient = None
chroma_client = None

@asynccontextmanager
async def lifespan_db(app: FastAPI):
    
    global mongo_client
    mongo_client = AsyncMongoClient(settings.MONGO_URI)

    await init_beanie(
        database=mongo_client[settings.DB_NAME],
        document_models=[User, RefreshToken]
    )
    
    app.mongodb_db = mongo_client[settings.DB_NAME]
    print("🚀 MongoDB connection and Beanie initialization established.")

    global chroma_client

    chroma_client = PersistentClient(path="./vector_store")

    app.chroma_client = chroma_client
    print("🚀 ChromaDB client initialized.")
 
    
    yield 
    
    if mongo_client:
        mongo_client.close()
        print("👋 MongoDB connection closed.")

    del app.chroma_client
    print("👋 ChromaDB connection closed.")


def get_chroma_client_instance(request: Request) -> ClientAPI:
    """
    Retrieves the initialized ChromaDB client from the FastAPI app state.
    """
    if not hasattr(request.app, "chroma_client") or request.app.chroma_client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail="Vector database is not initialized.")
                            
    return request.app.chroma_client