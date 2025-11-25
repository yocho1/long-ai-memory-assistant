from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation
from schemas import HistoryResponse
from auth import get_user_id_from_auth_header

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/", response_model=HistoryResponse)
def history(
    authorization: str = Header(None), 
    db: Session = Depends(get_db)
):
    try:
        user_id = get_user_id_from_auth_header(authorization)
        rows = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.asc()).all()
        
        history_data = [{
            "role": r.role, 
            "text": r.text, 
            "created_at": r.created_at.isoformat()
        } for r in rows]
        
        return {
            "history": history_data,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")