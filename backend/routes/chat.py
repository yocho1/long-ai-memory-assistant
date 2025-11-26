from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation
from schemas import ChatIn, ChatResponse
from auth import get_user_id_from_auth_header
from embeddings import embedding_service
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

def sanitize_sensitive_info(text: str) -> str:
    """
    Remove or mask sensitive information like TOTP secrets, API keys, etc.
    """
    # Mask TOTP secrets (the secret= parameter in otpauth URLs)
    text = re.sub(r'secret=[A-Za-z0-9]+', 'secret=***MASKED***', text)
    
    # Mask email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)
    
    # Mask phone numbers
    text = re.sub(r'\b\d{10,}\b', '***PHONE***', text)
    
    return text

def generate_ai_response(user_message: str, context: str, docs_count: int) -> str:
    """
    Generate an intelligent response based on the user message and retrieved context.
    This is a simplified version - you can integrate with OpenAI, Gemini, or other LLMs.
    """
    
    # Sanitize sensitive information from context
    safe_context = sanitize_sensitive_info(context)
    
    # Simple rule-based response generation
    # In a real implementation, you'd call an LLM API here
    
    if docs_count == 0:
        return "I couldn't find any relevant information in your stored documents about this topic. You might want to upload relevant documents first using the upload feature."
    
    # Analyze the context to generate a more intelligent response
    context_lower = safe_context.lower()
    
    # Check for specific topics in the context
    if any(word in context_lower for word in ['otpauth', 'totp', 'authenticator']):
        return "I found information about authentication codes in your documents. I've masked sensitive details for security. How can I help you with this information?"
    
    elif any(word in context_lower for word in ['mongodb', 'express', 'react', 'node', 'mern']):
        return f"I found {docs_count} relevant documents about web development with MERN stack. Based on your documents, it seems you have experience with full-stack JavaScript development. What specific aspect would you like to know more about?"
    
    elif any(word in context_lower for word in ['paypal', 'stripe', 'etsy', 'payment']):
        return f"I found {docs_count} documents related to payment services. I've secured any sensitive payment information. How would you like me to help with this?"
    
    else:
        # Generic intelligent response
        return f"Based on the {docs_count} relevant documents I found in your memory, I can help answer your question about '{user_message}'. The documents contain information that might be relevant to your query. What specific aspect would you like me to focus on?"

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
                    # Sanitize sensitive info in retrieved documents
                    safe_text = sanitize_sensitive_info(doc)
                    docs.append({
                        "text": safe_text, 
                        "meta": meta, 
                        "distance": res["distances"][0][i] if res.get("distances") else 0
                    })
        
        # Build context from retrieved docs
        context = "\n\n---\n\n".join([d["text"] for d in docs[:6]])
        
        # Generate intelligent AI response
        reply = generate_ai_response(message, context, len(docs))
        
        # Store assistant reply
        conv2 = Conversation(user_id=user_id, role="assistant", text=reply)
        db.add(conv2)
        db.commit()
        
        return {
            "reply": reply, 
            "retrieved": docs,  # These are now sanitized
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")