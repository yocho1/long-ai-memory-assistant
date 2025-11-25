import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.ingest import router as ingest_router
from routes.history import router as history_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
create_tables()

app = FastAPI(title="LongTerm AI Memory Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - REMOVE the prefix parameter
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(history_router)

@app.get("/")
def root():
    return {"message": "LongTerm AI Memory Assistant API", "status": "running"}

@app.get("/health")
def health_check():
    from embeddings import embedding_service
    from config import settings
    from embeddings import GENAI_AVAILABLE
    
    status = {
        "status": "healthy",
        "chromadb_available": embedding_service.collection is not None,
        "gemini_available": GENAI_AVAILABLE and bool(settings.GEMINI_KEY),
    }
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5005, reload=True)