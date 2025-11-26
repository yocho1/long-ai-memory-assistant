import io
import uuid
import logging
from typing import List
from PyPDF2 import PdfReader
from docx import Document

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for p in reader.pages:
            txt = p.extract_text()
            if txt:
                texts.append(txt)
        return "\n".join(texts)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    fname = filename.lower()
    try:
        if fname.endswith(".pdf"):
            return extract_text_from_pdf(file_bytes)
        elif fname.endswith(".docx"):
            return extract_text_from_docx(file_bytes)
        elif fname.endswith(".txt"):
            return file_bytes.decode("utf-8")
        else:
            try:
                return file_bytes.decode("utf-8")
            except:
                return file_bytes.decode("latin-1", errors="ignore")
    except Exception as e:
        logger.error(f"File extraction error for {filename}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into chunks with overlap, with safety limits to prevent memory errors
    """
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    
    # Safety checks
    if overlap >= chunk_size:
        overlap = chunk_size // 4  # Ensure overlap is smaller than chunk_size
    
    chunks = []
    start = 0
    text_length = len(text)
    max_chunks = 1000  # Safety limit to prevent infinite loops
    
    # If text is smaller than chunk_size, return as single chunk
    if text_length <= chunk_size:
        return [text] if text.strip() else []
    
    # Create chunks with safety limit
    while start < text_length and len(chunks) < max_chunks:
        end = start + chunk_size
        chunk = text[start:end].strip()
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)
        
        # Move to next position with overlap
        start = end - overlap
        
        # Safety check: if we're not making progress, break
        if start <= 0:
            break
    
    logger.info(f"Created {len(chunks)} chunks from text of length {text_length}")
    return chunks

def generate_uuid_list(count: int) -> List[str]:
    return [str(uuid.uuid4()) for _ in range(count)]