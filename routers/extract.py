import asyncio
import json
from io import BytesIO
from fastapi import APIRouter, UploadFile, HTTPException
from openai_client import call_deepseek
from pypdf import PdfReader
from models.document import DocumentBase
from models.clause import ClauseBase
from models.metadata import MetadataBase
from repositories import document_repository, extraction_repository, clause_repository, metadata_repository

router = APIRouter()


@router.post("", response_model=dict)
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
    payload = json.loads(result)

    try:
        doc_id = await document_repository.insert(
            DocumentBase(name=document.filename, text=extracted_text)
        )
        extraction_id = await extraction_repository.insert(doc_id)

        clauses_data = payload.get('clauses', [])
        clauses = [
            ClauseBase(**c, extraction_id=extraction_id)
            for c in clauses_data
        ]
        await clause_repository.insert_many(clauses)

        metadata_data = payload.get('metadata', {})
        metadata = MetadataBase(**metadata_data, extraction_id=extraction_id)
        await metadata_repository.insert(metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")

    return payload


async def extract_clauses_from_document(text: str):
    return await asyncio.to_thread(call_deepseek, text)