from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import RegisterIn, LoginIn
from auth import get_password_hash, verify_password, create_access_token  # Import from your auth utility file

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user = User(
            email=payload.email, 
            hashed_password=get_password_hash(payload.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create access token
        token = create_access_token({"sub": str(user.id)})
        return {
            "access_token": token, 
            "token_type": "bearer", 
            "user_id": user.id,
            "message": "Registration successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"sub": str(user.id)})
        return {
            "access_token": token, 
            "token_type": "bearer", 
            "user_id": user.id,
            "message": "Login successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")