from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from schemas import IngestResponse
from auth import get_user_id_from_auth_header
from embeddings import embedding_service
from utils import extract_text_from_file, chunk_text, generate_uuid_list
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/upload", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(..., max_size=10 * 1024 * 1024),  # 10MB limit
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Upload doc; chunks are stored with metadata including user_id and source.
    Header: Authorization: Bearer <token>
    """
    try:
        logger.info(f"Starting upload process for file: {file.filename}")
        user_id = get_user_id_from_auth_header(authorization)
        logger.info(f"User authenticated: {user_id}")
        
        # Check if ChromaDB is available
        if not embedding_service.collection:
            logger.error("ChromaDB collection not available")
            raise HTTPException(status_code=500, detail="Vector database not available")
        logger.info("ChromaDB available")
        
        # Read and process file
        logger.info("Reading file content...")
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        logger.info("Extracting text from file...")
        text = extract_text_from_file(file.filename, content)
        logger.info(f"Extracted text length: {len(text)} characters")
        
        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="No text extracted or file too small")
        
        # Chunk text
        logger.info("Chunking text...")
        chunks = chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks")
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks created")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        try:
            embeddings = embedding_service.embed_texts(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")
        except Exception as embed_error:
            logger.error(f"Embedding generation failed: {embed_error}")
            raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(embed_error)}")
        
        # Prepare data for ChromaDB
        ids = generate_uuid_list(len(chunks))
        metadatas = [{
            "user_id": user_id, 
            "source": file.filename, 
            "chunk_index": i,
            "timestamp": datetime.utcnow().isoformat()
        } for i in range(len(chunks))]
        
        # Store in ChromaDB
        logger.info("Storing in ChromaDB...")
        try:
            embedding_service.collection.add(
                ids=ids, 
                documents=chunks, 
                metadatas=metadatas, 
                embeddings=embeddings
            )
            logger.info("Successfully stored in ChromaDB")
        except Exception as chroma_error:
            logger.error(f"ChromaDB storage failed: {chroma_error}")
            raise HTTPException(status_code=500, detail=f"Storage failed: {str(chroma_error)}")
        
        logger.info("Upload completed successfully")
        
        return {
            "success": True, 
            "ingested_chunks": len(chunks),
            "message": f"Successfully ingested {len(chunks)} chunks from {file.filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")