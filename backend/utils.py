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

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
        
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if start >= L:
            break
    return chunks

def generate_uuid_list(count: int) -> List[str]:
    return [str(uuid.uuid4()) for _ in range(count)]