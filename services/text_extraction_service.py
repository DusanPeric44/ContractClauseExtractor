from io import BytesIO
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import docx

def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    buf = []
    for page in reader.pages:
        buf.append(page.extract_text() or "")
    return "".join(buf)

def _extract_docx(data: bytes) -> str:
    doc = docx.Document(BytesIO(data))
    return "\n".join(p.text or "" for p in doc.paragraphs)

async def extract_text(file: UploadFile) -> str:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    ct = file.content_type
    if ct == "application/pdf":
        return _extract_pdf(data)
    if ct == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            return _extract_docx(data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DOCX parse error: {e}")
    raise HTTPException(status_code=415, detail=f"Unsupported file type: {ct}")