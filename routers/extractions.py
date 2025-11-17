from typing import List
from fastapi import APIRouter
from models.extraction import Extraction
from services.extraction_service import get_by_document_id, list_extractions

router = APIRouter()

@router.get("/{document_id}", response_model=List[Extraction])
async def get_extraction_by_id(document_id: int):
    return await get_by_document_id(document_id)

@router.get("", response_model=List[Extraction])
async def get_extractions(pageNum: int, pageSize: int):
    return await list_extractions(pageNum, pageSize)