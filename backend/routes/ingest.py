from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from schemas import IngestResponse
from auth import get_user_id_from_auth_header
from embeddings import embedding_service
from utils import extract_text_from_file, chunk_text, generate_uuid_list
from datetime import datetime

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...), 
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Upload doc; chunks are stored with metadata including user_id and source.
    Header: Authorization: Bearer <token>
    """
    try:
        user_id = get_user_id_from_auth_header(authorization)
        
        # Check if ChromaDB is available
        if not embedding_service.collection:
            raise HTTPException(status_code=500, detail="Vector database not available")
        
        # Read and process file
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        text = extract_text_from_file(file.filename, content)
        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="No text extracted or file too small")
        
        # Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks created")
        
        # Generate embeddings
        embeddings = embedding_service.embed_texts(chunks)
        
        # Prepare data for ChromaDB
        ids = generate_uuid_list(len(chunks))
        metadatas = [{
            "user_id": user_id, 
            "source": file.filename, 
            "chunk_index": i,
            "timestamp": datetime.utcnow().isoformat()
        } for i in range(len(chunks))]
        
        # Store in ChromaDB
        embedding_service.collection.add(
            ids=ids, 
            documents=chunks, 
            metadatas=metadatas, 
            embeddings=embeddings
        )
        
        return {
            "success": True, 
            "ingested_chunks": len(chunks),
            "message": f"Successfully ingested {len(chunks)} chunks from {file.filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")