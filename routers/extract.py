import asyncio
import json
from fastapi import APIRouter, UploadFile, HTTPException
from openai_client import call_deepseek
from services import text_extraction_service
from services.extraction_service import save_extraction

router = APIRouter()


@router.post("", response_model=dict)
async def extract_clauses(document: UploadFile):
    if (document.content_type == "application/pdf"
            or document.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
        extracted_text = await text_extraction_service.extract_text(document)
        result = await extract_clauses_from_document(extracted_text)
        payload = json.loads(result)

        try:
            await save_extraction(document.filename, extracted_text, payload)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {e}")

        return payload
    raise HTTPException(status_code=400, detail="Unsupported file type")


async def extract_clauses_from_document(text: str):
    return await asyncio.to_thread(call_deepseek, text)