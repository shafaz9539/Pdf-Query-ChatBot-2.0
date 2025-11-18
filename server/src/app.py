from fastapi import FastAPI
from src.routers import query, upload
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv(".env")

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)

@app.get("/")
async def root():
    return {"status": "server is running"}
