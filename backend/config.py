import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    JWT_SECRET = os.getenv("JWT_SECRET_KEY", "please_change_this_to_secure_secret_key")
    JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_store")
    EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

settings = Settings()