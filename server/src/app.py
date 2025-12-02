from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from src.routers import query, upload, user
from .database.connection import lifespan_db
load_dotenv(".env")

app = FastAPI(lifespan=lifespan_db)


bearer_scheme = HTTPBearer()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "server is running"}
