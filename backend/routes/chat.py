from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation
from schemas import ChatIn, ChatResponse
from auth import get_user_id_from_auth_header
from embeddings import embedding_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatIn, 
    authorization: str = Header(None), 
    db: Session = Depends(get_db)
):
    try:
        user_id = get_user_id_from_auth_header(authorization)
        message = payload.message.strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Message empty")
        
        # Store user message
        conv = Conversation(user_id=user_id, role="user", text=message)
        db.add(conv)
        db.commit()
        
        # Check if ChromaDB is available
        if not embedding_service.collection:
            reply = "Vector database not available. Please try again later."
            conv2 = Conversation(user_id=user_id, role="assistant", text=reply)
            db.add(conv2)
            db.commit()
            return {"reply": reply, "retrieved": []}
        
        # Embed query
        q_emb = embedding_service.embed_texts([message])[0]
        
        # Retrieve relevant documents for this user
        res = embedding_service.collection.query(
            query_embeddings=[q_emb], 
            n_results=payload.top_k,
            where={"user_id": user_id},
            include=["documents", "metadatas", "distances"]
        )
        
        docs = []
        if res and res.get("documents"):
            for i, doc in enumerate(res["documents"][0]):
                meta = res["metadatas"][0][i] if res.get("metadatas") else {}
                if meta.get("user_id") == user_id:
                    docs.append({
                        "text": doc, 
                        "meta": meta, 
                        "distance": res["distances"][0][i] if res.get("distances") else 0
                    })
        
        # Build context from retrieved docs
        context = "\n\n---\n\n".join([d["text"] for d in docs[:6]])
        
        # Generate response (simplified - you can integrate with your preferred LLM)
        if docs:
            reply = f"I found {len(docs)} relevant document chunks in your memory. Based on this information: {context[:500]}..."
        else:
            reply = "I couldn't find any relevant information in your stored documents. Please upload some documents first using the /ingest endpoint."
        
        # Store assistant reply
        conv2 = Conversation(user_id=user_id, role="assistant", text=reply)
        db.add(conv2)
        db.commit()
        
        return {
            "reply": reply, 
            "retrieved": docs,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")