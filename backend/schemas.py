from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class IngestResponse(BaseModel):
    success: bool
    ingested_chunks: int
    message: str = ""

class ChatIn(BaseModel):
    message: str
    top_k: Optional[int] = 4

class ChatResponse(BaseModel):
    reply: str
    retrieved: List[dict]
    success: bool = True

class HistoryResponse(BaseModel):
    history: List[dict]
    success: bool = True

class ConversationOut(BaseModel):
    role: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True