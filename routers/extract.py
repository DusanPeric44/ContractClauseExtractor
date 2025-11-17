import asyncio
import json
from io import BytesIO
from fastapi import APIRouter, UploadFile, HTTPException
from openai_client import call_deepseek
from pypdf import PdfReader

router = APIRouter()


@router.post("")
async def extract_clauses(document: UploadFile):
    if document.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Unsupported file type")
    data = await document.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    reader = PdfReader(BytesIO(data))
    extracted_text =""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""
    result = await extract_clauses_from_document(extracted_text)
    return json.loads(result)


async def extract_clauses_from_document(text: str):
    return await asyncio.to_thread(call_deepseek, text)