import logging
from typing import List
import chromadb
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Gemini AI not available: {e}")
    GENAI_AVAILABLE = False

from config import settings

class EmbeddingService:
    def __init__(self):
        logger.info("Initializing EmbeddingService...")
        self.use_gemini_embeddings = bool(settings.GEMINI_KEY and GENAI_AVAILABLE)
        
        # Initialize Gemini if available
        if settings.GEMINI_KEY and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=settings.GEMINI_KEY)
                logger.info("Gemini AI configured successfully")
            except Exception as e:
                logger.error(f"Gemini configuration failed: {e}")
                self.use_gemini_embeddings = False
        
        # Initialize local embedding model as fallback
        if not self.use_gemini_embeddings:
            try:
                self.embed_model = SentenceTransformer(settings.EMBED_MODEL)
                logger.info(f"Local embedding model {settings.EMBED_MODEL} loaded")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embed_model = None
        else:
            self.embed_model = None
            logger.info("Using Gemini embeddings")
        
        # Initialize ChromaDB
        try:
            self.chroma_client = PersistentClient(path=settings.CHROMA_DIR)
            self.collection = self.chroma_client.get_or_create_collection(name="user_memories")
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            self.chroma_client = None
            self.collection = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        if self.use_gemini_embeddings and GENAI_AVAILABLE:
            try:
                embeddings = []
                for text in texts:
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(result['embedding'])
                return embeddings
            except Exception as e:
                logger.error(f"Gemini embedding error: {e}, falling back to local model")
                return self._fallback_embed(texts)
        else:
            return self._fallback_embed(texts)

    def _fallback_embed(self, texts: List[str]) -> List[List[float]]:
        if self.embed_model:
            arr = self.embed_model.encode(texts, show_progress_bar=False)
            return [a.tolist() if hasattr(a, "tolist") else list(a) for a in arr]
        else:
            logger.error("No embedding model available")
            return [[0.0] * 384 for _ in texts]  # Default fallback

embedding_service = EmbeddingService()